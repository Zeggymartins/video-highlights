# 🎬 AI-Powered Video Highlight Generator

This is a Flask-based API that processes short-form videos to identify engaging moments using AI, generate English captions, and create a highlight reel. The API receives a video URL, processes it, and returns JSON output with timestamps and a link to the highlight clip.

## 🚀 Features

- 📥 **Download Videos**: Fetches video from a given URL.
- 📝 **Transcription & Translation**: Converts audio to text (English).
- 🏃‍♂️ **Detects Fast Speech & Movement**: Identifies key moments based on speed.
- 🎞 **Highlight Reel Creation**: Merges exciting moments into a short video.
- 🌐 **Live Demo**: Web UI to test video processing.

---

## 📂 Project Structure

```
📁 project-root/
│-- 📂 files/              # Stores processed videos & captions
│-- 📂 templates/          # Frontend HTML files
│-- 📜 main.py             # Flask API entry point
│-- 📜 video_download.py   # Handles downloading videos
│-- 📜 frame.py            # Extracts frames for analysis
│-- 📜 video.py            # Handles transcription & processing
│-- 📜 requirements.txt    # Dependencies list
│-- 📜 README.md           # Documentation
```

---

## 🛠️ Dependencies

Install required packages:

```bash
pip install -r requirements.txt
```

**Key Packages Used:**
- Flask & Flask-CORS (Backend API)
- OpenCV (Frame extraction & video editing)
- Faster Whisper (AI-based speech recognition)
- NumPy (Data processing)
- yt_dlp (YouTube video downloads)

---

## 🚀 Running the API

Start the Flask server:

```bash
python main.py
```

API will be available at:  
👉 `http://127.0.0.1:5001/`

### **Processing a Video**
Send a `POST` request to `/process` with JSON:

```json
{
    "url": "https://www.youtube.com/watch?v=example"
}
```

### **Response Format**
```json
{
    "key_moments": [
        {"timestamp": "12.50", "caption": "Engaging moment detected"}
    ],
    "highlight_clip_url": "http://127.0.0.1:5001/files/highlight.mp4"
}
```

---

## 🌍 Live Demo

The demo web interface is available at `http://127.0.0.1:5001/`.  
It allows users to enter a video URL, process it, and watch the highlight video.

---

## 🚀 Deployment on Render



## 🎥 Example Output

Here’s an example of a processed highlight reel with captions:

![Demo](https://via.placeholder.com/600x300?text=Demo+Video+Preview)

---

## 💡 Future Enhancements

- 🎙 Support more languages for transcription
- 🎨 Improve UI for better user experience
- 🚀 Optimize video processing for faster execution
