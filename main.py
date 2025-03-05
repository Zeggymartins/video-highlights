from flask import Flask, request, jsonify, send_file, send_from_directory, render_template
from flask_cors import CORS
import os
from video_download import download_video  
from frame import extract_frames  
from video import transcribe_video, detect_fast_speech, detect_fast_movements, merge_timestamps, create_highlight_reel  

# Initialize Flask app
app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = False
CORS(app)

# Ensure necessary directories exist
FILES_DIR = "files"
HIGHLIGHT_DIR = os.path.join(FILES_DIR, "highlights")
os.makedirs(HIGHLIGHT_DIR, exist_ok=True)

@app.route('/')
def home():
    return render_template("index.html")  # Load frontend

@app.route('/process', methods=['POST'])
def process_video():
    """API endpoint to process a video and return key moments & highlight clip."""
    data = request.json or request.form 
    video_url = data.get("url")

    if not video_url:
        return jsonify({"error": "No video URL provided"}), 400

    try:
        # Step 1: Download Video
        print("📥 Downloading video...")
        video_path = download_video(video_url)  

        if not video_path or not os.path.exists(video_path):
            return jsonify({"error": "Failed to download video"}), 500

        print(f"✅ Video saved at: {video_path}")

        # Step 2: Extract Frames
        extract_frames(video_path, interval=2)

        # Step 3: Transcribe Video & Detect Key Moments
        captions = transcribe_video(video_path)
        fast_speech = detect_fast_speech(captions)
        fast_movements = detect_fast_movements(video_path)

        # Step 4: Merge timestamps from fast speech & movement
        key_moments = merge_timestamps(fast_speech, fast_movements)

        # Step 5: Create Highlight Reel
        highlight_clip = create_highlight_reel(video_path, key_moments, captions, output_path=os.path.join(HIGHLIGHT_DIR, "highlight.mp4"))

        # Ensure the highlight clip exists before returning
        if not highlight_clip or not os.path.exists(highlight_clip):
            return jsonify({"error": "Failed to create highlight reel"}), 500

        response = {
            "key_moments": [
                {"timestamp": f"{start:.2f}", "caption": "Engaging moment detected"}
                for start, _ in key_moments
            ],
            "highlight_clip_url": f"{request.host_url}files/highlights/{os.path.basename(highlight_clip)}"
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/files/<path:filename>')
def serve_files(filename):
    """Serve processed files (e.g., highlight videos) via HTTP with correct content type."""
    highlight_path = os.path.join(HIGHLIGHT_DIR, filename)
    file_path = os.path.join(FILES_DIR, filename)

    if os.path.exists(file_path):
        return send_file(file_path, mimetype="video/mp4")
    elif os.path.exists(highlight_path):
        return send_file(highlight_path, mimetype="video/mp4")
    return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
   port = int(os.environ.get("PORT", 10000))  # Default to 10000
   app.run(host="0.0.0.0", port=port)
