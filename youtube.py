from flask import Flask, render_template, request, send_file
import yt_dlp
import os

app = Flask(__name__)
DOWNLOAD_FOLDER = os.path.abspath("downloads")  # Absolute path to store downloaded videos
FFMPEG_LOCATION = r"ffmpeg-7.1-essentials_build\ffmpeg-7.1-essentials_build\bin\ffmpeg.exe"  # Adjust this if needed
COOKIES_FILE = r"cookies.txt"  # Path to your cookies.txt file

# Ensure the downloads folder exists
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def home():
    # Debug: Log when the home page is accessed
    print("[DEBUG] Accessed Home Page")
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    try:
        # Get the video URL from the form
        video_url = request.form['url'].strip()
        if not video_url:
            print("[DEBUG] Error: No URL provided.")
            return "Error: No URL provided."

        # Debug: Log the provided URL
        print(f"[DEBUG] Video URL: {video_url}")

        # Define download options with sanitized filenames
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best[ext=webm]',  # Get best quality video + audio
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title).100s.%(ext)s',  # Sanitize and limit title length
            'noplaylist': True,  # Single video only
            'ffmpeg_location': FFMPEG_LOCATION,  # Specify FFmpeg path
            'cookiefile': COOKIES_FILE,  # Use cookies for authentication
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'webm',  # Convert to MP4 if necessary
            }],
            'overwrites': True,  # Force overwriting of existing files
        }

        # Debug: Log download options
        print(f"[DEBUG] yt-dlp Options: {ydl_opts}")
        print(f"[DEBUG] Download folder: {DOWNLOAD_FOLDER}")
        print(f"[DEBUG] FFmpeg location: {FFMPEG_LOCATION}")
        print(f"[DEBUG] Cookies file: {COOKIES_FILE}")

        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("[DEBUG] Starting video download...")
            info = ydl.extract_info(video_url, download=True)
            file_path = ydl.prepare_filename(info)
            print(f"[DEBUG] Downloaded file path: {file_path}")

        # Ensure the downloaded file has a valid MP4 extension
        file_base, file_ext = os.path.splitext(file_path)
        if file_ext.lower() != '.webm':
            file_path = f"{file_base}.webm"
            print(f"[DEBUG] Adjusted file path to: {file_path}")

        # Debug: Log before sending the file
        print(f"[DEBUG] Sending file: {file_path}")
        return send_file(file_path, as_attachment=True)

    except yt_dlp.utils.DownloadError as e:
        print(f"[ERROR] Download error: {e}")
        return f"Download error: {e}"
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
        return f"An error occurred: {e}"

if __name__ == "__main__":
    # Debug: Log when the server starts
    print("[DEBUG] Starting Flask server...")
    app.run(host='0.0.0.0', port=8000)
