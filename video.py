import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import cv2
import numpy as np
from faster_whisper import WhisperModel

# File paths
CAPTIONS_PATH = "files/captions.txt"
OUTPUT_VIDEO_PATH = "files/highlights/highlight.mp4"

# Initialize Whisper model
model = WhisperModel("medium", compute_type="float32")
def transcribe_video(video_path, language="en"):
    """Transcribes audio from video and saves English captions by default."""
    valid_languages = {
        "af", "am", "ar", "as", "az", "ba", "be", "bg", "bn", "bo", "br", "bs", "ca", "cs", "cy",
        "da", "de", "el", "en", "es", "et", "eu", "fa", "fi", "fo", "fr", "gl", "gu", "ha", "haw",
        "he", "hi", "hr", "ht", "hu", "hy", "id", "is", "it", "ja", "jw", "ka", "kk", "km", "kn",
        "ko", "la", "lb", "ln", "lo", "lt", "lv", "mg", "mi", "mk", "ml", "mn", "mr", "ms", "mt",
        "my", "ne", "nl", "nn", "no", "oc", "pa", "pl", "ps", "pt", "ro", "ru", "sa", "sd", "si",
        "sk", "sl", "sn", "so", "sq", "sr", "su", "sv", "sw", "ta", "te", "tg", "th", "tk", "tl",
        "tr", "tt", "uk", "ur", "uz", "vi", "yi", "yo", "zh", "yue"
    }

    if language not in valid_languages:
        print(f"⚠️ Invalid language '{language}', defaulting to English (en).")
        language = "en"  # Default to English if invalid

    print(f"🔹 Transcribing video: {video_path} in language: {language}")
    segments, _ = model.transcribe(video_path, language=language, task="translate")

    captions = []
    with open(CAPTIONS_PATH, "w", encoding="utf-8") as f:
        for segment in segments:
            start, end, text = segment.start, segment.end, segment.text
            captions.append((start, end, text))
            f.write(f"{start:.2f} --> {end:.2f}\n{text}\n\n")

    print(f"✅ Transcription complete! {len(captions)} segments found.")
    return captions

def detect_fast_speech(captions, threshold=3.5):
    """Detects segments where words per second exceed threshold."""
    print("🔹 Detecting fast speech...")
    fast_speech_timestamps = []
    
    for start, end, text in captions:
        duration = end - start
        word_count = len(text.split())
        words_per_second = word_count / duration if duration > 0 else 0
        if words_per_second > threshold:
            fast_speech_timestamps.append((start, end))

    print(f"✅ Fast speech detection complete! {len(fast_speech_timestamps)} segments found.")
    return fast_speech_timestamps

def detect_fast_movements(video_path, threshold=15):
    """Detects fast movements using optical flow analysis."""
    print("🔹 Detecting fast movements...")
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("❌ Error: Cannot open video file.")
        return []

    ret, prev_frame = cap.read()
    if not ret:
        print("❌ Error: Cannot read first frame.")
        return []

    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    fast_movement_timestamps = []
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_idx = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        movement = np.mean(np.abs(flow))

        if movement > threshold:
            timestamp = frame_idx / fps
            fast_movement_timestamps.append((timestamp, timestamp + 1))

        prev_gray = gray
        frame_idx += 1

    cap.release()
    print(f"✅ Fast movement detection complete! {len(fast_movement_timestamps)} segments found.")
    return fast_movement_timestamps

def merge_timestamps(fast_speech, fast_movements, margin=1.5):
    """Merges overlapping timestamps."""
    print("🔹 Merging timestamps...")
    combined = sorted(fast_speech + fast_movements)
    merged = []
    
    for start, end in combined:
        if merged and start - merged[-1][1] <= margin:
            merged[-1] = (merged[-1][0], end)
        else:
            merged.append((start, end))
    
    print(f"✅ Merging complete! {len(merged)} final highlight segments.")
    return merged


def create_highlight_reel(video_path, timestamps, captions, output_path=OUTPUT_VIDEO_PATH):
    """Creates a highlight reel with captions centered on the screen."""
    print("🔹 Creating highlight reel with captions...")
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("❌ Error: Cannot open video file.")
        return None

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    fourcc = cv2.VideoWriter_fourcc(*'H264')  # Codec for MP4
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Convert captions list into a dictionary {timestamp: caption}
    captions_dict = {round(start, 2): text for start, _, text in captions}

    for start, end in timestamps:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(start * fps))
        print(f"✂️ Extracting segment {start:.2f} to {end:.2f} seconds...")

        while cap.get(cv2.CAP_PROP_POS_MSEC) / 1000 < end:
            ret, frame = cap.read()
            if not ret:
                print("❌ Error: Frame read failed, stopping segment.")
                break

            # Get the caption for this timestamp
            timestamp = round(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000, 2)
            caption_text = captions_dict.get(timestamp, "")

            if caption_text:
                # Text properties
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 1
                font_thickness = 2
                text_color = (255, 255, 255)  # White
                outline_color = (0, 0, 0)  # Black

                # Get text size
                text_size = cv2.getTextSize(caption_text, font, font_scale, font_thickness)[0]
                text_x = (width - text_size[0]) // 2  # Center horizontally
                text_y = height // 2  # Center vertically

                # Draw text outline (for better visibility)
                cv2.putText(frame, caption_text, (text_x - 1, text_y - 1), font, font_scale, outline_color, font_thickness + 2, cv2.LINE_AA)
                cv2.putText(frame, caption_text, (text_x + 1, text_y + 1), font, font_scale, outline_color, font_thickness + 2, cv2.LINE_AA)
                cv2.putText(frame, caption_text, (text_x, text_y), font, font_scale, text_color, font_thickness, cv2.LINE_AA)

            out.write(frame)

    cap.release()
    out.release()
    print(f"✅ Highlight reel saved: {output_path}")
    return output_path  # Return file path of highlight video

if __name__ == "__main__":
    VIDEO_PATH = "files/sample.mp4"  # Change this to your video file

    # Step 1: Transcribe Video
    captions = transcribe_video(VIDEO_PATH)

    # Step 2: Detect Engaging Moments
    fast_speech = detect_fast_speech(captions)
    fast_movements = detect_fast_movements(VIDEO_PATH)

    # Step 3: Merge timestamps
    engaging_moments = merge_timestamps(fast_speech, fast_movements)

    # Step 4: Create Highlight Reel
    create_highlight_reel(VIDEO_PATH, engaging_moments)
