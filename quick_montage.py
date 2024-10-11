import os
import subprocess
import tempfile
import glob
import shutil
import argparse

# Argument parsing
parser = argparse.ArgumentParser(description="Video montage script")
parser.add_argument('-yt', '--youtube', type=str, help='YouTube URL to download audio from')
parser.add_argument('-b', '--balance', type=float, help='Balance for audio mixing (0.0 to 1.0)')
args = parser.parse_args()

# Remove the existing output file if it exists
if os.path.exists('output_with_audio.mp4'):
    os.remove('output_with_audio.mp4')

# Create a temporary directory to hold the remuxed video files
temp_dir = tempfile.mkdtemp()

# Remux all video files to a common format and codec
video_files = glob.glob('*.[mM][pP]4') + glob.glob('*.[mM][kK][vV]') + glob.glob('*.[aA][vV][iI]') + glob.glob('*.[fF][lL][vV]') + glob.glob('*.[wW][mM][vV]') + glob.glob('*.[mM][oO][vV]') + glob.glob('*.[wW][eE][bB][mM]')
for file in sorted(video_files):
    output_file = os.path.join(temp_dir, os.path.splitext(os.path.basename(file))[0] + '.mp4')
    subprocess.run(['ffmpeg', '-i', file, '-c:v', 'copy', '-c:a', 'copy', output_file])

# Create a temporary file to hold the list of remuxed video files
video_temp_file = tempfile.NamedTemporaryFile(delete=False)
with open(video_temp_file.name, 'w') as f:
    for file in sorted(glob.glob(os.path.join(temp_dir, '*.mp4'))):
        f.write(f"file '{file}'\n")

# Combine the videos using ffmpeg
subprocess.run(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', video_temp_file.name, '-c', 'copy', 'combined_video.mp4'])

# Download audio from YouTube if URL is provided
if args.youtube:
    audio_file = 'downloaded_audio.mp3'
    subprocess.run(['yt-dlp', '-f', 'bestaudio', '-o', audio_file, args.youtube])
else:
    # Find the first audio file in the current directory
    audio_files = glob.glob('*.[mM][pP]3') + glob.glob('*.[wW][aA][vV]') + glob.glob('*.[aA][aA][cC]') + glob.glob('*.[fF][lL][aA][cC]')
    if audio_files:
        audio_file = sorted(audio_files)[0]
    else:
        print("No audio files found.")
        audio_file = None

# Add the audio file to the output video
if audio_file:
    if args.balance:
        subprocess.run(['ffmpeg', '-i', 'combined_video.mp4', '-i', audio_file, '-filter_complex', f"[1:a]volume={args.balance}[a1];[0:a][a1]amix=inputs=2:duration=first:dropout_transition=2", '-c:v', 'copy', '-c:a', 'aac', '-shortest', 'output_with_audio.mp4'])
    else:
        subprocess.run(['ffmpeg', '-i', 'combined_video.mp4', '-i', audio_file, '-c:v', 'copy', '-c:a', 'aac', '-map', '0:v:0', '-map', '1:a:0', '-shortest', 'output_with_audio.mp4'])

# Clean up the temporary files and directory
os.remove(video_temp_file.name)
os.remove('combined_video.mp4')
for file in glob.glob(os.path.join(temp_dir, '*.mp4')):
    os.remove(file)
os.rmdir(temp_dir)

# Check if VLC is installed and open the output video in a new process
if shutil.which("vlc"):
    print("Opening output video with VLC...")
    subprocess.Popen(["vlc", "output_with_audio.mp4"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
else:
    print("VLC is not installed.")