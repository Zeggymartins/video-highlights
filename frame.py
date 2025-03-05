import cv2
import os

def extract_frames(video_path, output_folder="files/frames", interval=2):
    """Extract frames from a video at a given interval (in seconds)."""
    os.makedirs(output_folder, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("❌ Error: Could not open video.")
        return
    
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_interval = fps * interval  # Frames to skip
    
    frame_count = 0
    saved_count = 0

    while True:
        success, frame = cap.read()
        if not success:
            break

        if frame_count % frame_interval == 0:
            frame_filename = os.path.join(output_folder, f"frame_{saved_count}.jpg")
            cv2.imwrite(frame_filename, frame)
            print(f"✅ Saved: {frame_filename}")
            saved_count += 1

        frame_count += 1

    cap.release()
    print("✅ Frame extraction complete!")

if __name__ == "__main__":
    video_file = "files/sample.mp4"  # Change this to your downloaded video
    extract_frames(video_file, interval=2)
