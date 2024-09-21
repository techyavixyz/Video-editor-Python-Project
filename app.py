from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import os
from moviepy.editor import VideoFileClip

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
AUDIO_FOLDER = 'audio'
ORIGINALS_FOLDER = 'originals'  # New folder for original videos
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['AUDIO_FOLDER'] = AUDIO_FOLDER
app.config['ORIGINALS_FOLDER'] = ORIGINALS_FOLDER

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)
os.makedirs(ORIGINALS_FOLDER, exist_ok=True)

# Get all files in the uploads folder
def get_saved_videos():
    return [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith(('.mp4', '.webm'))]

# Get all files in the audio folder
def get_saved_audios():
    return [f for f in os.listdir(app.config['AUDIO_FOLDER']) if f.endswith('.mp3')]

@app.route('/')
def index():
    videos = get_saved_videos()  # Show all saved videos
    audios = get_saved_audios()  # Show all saved audios
    return render_template('index.html', videos=videos, audios=audios)

@app.route('/upload', methods=['POST'])
def upload_video():
    # Get the uploaded file
    if 'video' not in request.files:
        return redirect(request.url)
    file = request.files['video']

    if file.filename == '':
        return redirect(request.url)

    if file:
        # Get start/end times and new filename for the trimmed video
        start_time = int(request.form['start_time'])
        end_time = int(request.form['end_time'])
        new_filename = request.form['new_filename']

        # Save the original video in the originals folder
        original_video_path = os.path.join(app.config['ORIGINALS_FOLDER'], file.filename)
        file.save(original_video_path)

        # Create new file names for the audio
        audio_filename = new_filename + '.mp3'
        audio_path = os.path.join(app.config['AUDIO_FOLDER'], audio_filename)

        # Create new file names for the trimmed video
        trimmed_video_filename = new_filename + '.mp4'
        trimmed_video_path = os.path.join(app.config['UPLOAD_FOLDER'], trimmed_video_filename)

        # Trim the video
        with VideoFileClip(original_video_path) as video:  # Use original video for trimming
            trimmed_clip = video.subclip(start_time, end_time)

            # Check if the user wants to save only the audio
            if 'trim_only_audio' in request.form:
                trimmed_clip.audio.write_audiofile(audio_path)
                return redirect(url_for('index'))  # Redirect back to the index

            # Save both trimmed video and audio if user wants
            trimmed_clip.write_videofile(trimmed_video_path)

            # Save audio if the user selects the option
            if 'save_audio' in request.form:
                trimmed_clip.audio.write_audiofile(audio_path)

        # Redirect to the video player page
        return redirect(url_for('play_video', filename=trimmed_video_filename))


@app.route('/play/<filename>')
def play_video(filename):
    return render_template('play.html', filename=filename)

@app.route('/uploads/<path:filename>')
def serve_video(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory(app.config['AUDIO_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
