import cv2
import os

def extract_frames(video_path, start_sec, end_sec, frame_rate, output_dir):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Open the video file
    video_capture = cv2.VideoCapture(video_path)
    fps = video_capture.get(cv2.CAP_PROP_FPS)  # Frames per second
    total_frames = video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
    video_duration = total_frames / fps

    # Check if the end second is within the video length
    if end_sec > video_duration:
        end_sec = video_duration

    # Set the start frame and end frame based on the seconds
    start_frame = int(start_sec * fps)
    end_frame = int(end_sec * fps)

    # Set the current frame position to the start frame
    video_capture.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    current_frame = start_frame
    frame_index = 0

    # Calculate the interval of frames to skip based on frame_rate and video FPS
    frame_interval = int(fps / frame_rate)

    while current_frame <= end_frame:
        success, frame = video_capture.read()
        if not success:
            break

        # Save the frame if it's the right one according to the frame_interval
        frame_filename = os.path.join(output_dir, f"frame_{frame_index}.png")
        cv2.imwrite(frame_filename, frame)
        frame_index += 1

        # Jump ahead by frame_interval frames
        current_frame += frame_interval
        video_capture.set(cv2.CAP_PROP_POS_FRAMES, current_frame)

    # Release the video capture object
    video_capture.release()

if __name__ == "__main__":
    video_path = "input_videos/abnormal_1.mp4"
    start_sec = 10  # Start extracting at 10 seconds
    end_sec = 20  # Stop extracting at 20 seconds
    frame_rate = 1  # Extract 1 frame per second
    output_dir = "output_frames"

    extract_frames(video_path, start_sec, end_sec, frame_rate, output_dir)
