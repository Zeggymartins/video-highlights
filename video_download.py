import yt_dlp
import os

def convert_youtube_url(url):
    """Convert YouTube Shorts URL to Standard YouTube URL."""
    if "shorts/" in url:
        url = url.replace("shorts/", "watch?v=")
    return url

def download_video(url):
    """Download the highest resolution video and return the file path."""
    url = convert_youtube_url(url)
    print(f"Converted URL: {url}")  # Debugging line

    os.makedirs("files", exist_ok=True)  # Ensure 'files/' directory exists

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'files/%(title)s.%(ext)s',  # Save in 'files/' folder
        'noplaylist': True,  # Ensure only one video is downloaded
        'quiet': False,  # Show download progress
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_filename = ydl.prepare_filename(info_dict)  # Get the actual filename

        print(f"✅ Download complete! Saved as: {video_filename}")
        return video_filename  # Return full path

    except Exception as e:
        print(f"❌ Download Error: {e}")
        return None  # Return None if download fails

if __name__ == "__main__":
    video_url = input("Enter YouTube URL: ").strip()
    print("📥 Downloading...")
    video_path = download_video(video_url)
    if video_path:
        print(f"✅ Video downloaded: {video_path}")
