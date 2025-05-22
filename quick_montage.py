import os
import subprocess
import tempfile
import glob
import shutil
import argparse

# Argument parsing
parser = argparse.ArgumentParser(description="Video montage script")
parser.add_argument('-y', '--youtube', type=str, help='YouTube URL to download audio from')
parser.add_argument('-b', '--balance', type=float, nargs='?', const=0.2, help='Balance for audio mixing (0.0 to 1.0)')
args = parser.parse_args()

# Validate balance option if provided
if args.balance is not None and (args.balance < 0.0 or args.balance > 1.0):
    print("Invalid balance value: {}. It should be a number between 0.0 and 1.0.".format(args.balance))
    exit(1)

# Remove the existing output file if it exists
if os.path.exists('output.mp4'):
    os.remove('output.mp4')

if os.path.exists('downloaded_audio.mp3'):
    os.remove('downloaded_audio.mp3')

# Create a temporary directory to hold the remuxed video files
temp_dir = tempfile.mkdtemp()
print("Temporary directory created: {}".format(temp_dir))

# Remux all video files to a common format and codec
video_files = glob.glob('*.[mM][pP]4') + glob.glob('*.[mM][kK][vV]') + glob.glob('*.[aA][vV][iI]') + glob.glob('*.[fF][lL][vV]') + glob.glob('*.[wW][mM][vV]') + glob.glob('*.[mM][oO][vV]') + glob.glob('*.[wW][eE][bB][mM]')
print("Found video files: {}".format(video_files))
for file in sorted(video_files):
    output_file = os.path.join(temp_dir, os.path.splitext(os.path.basename(file))[0] + '.mp4')
    print("Remuxing video file: {} to {}".format(file, output_file))
    subprocess.run(['ffmpeg', '-i', file, '-c:v', 'copy', '-c:a', 'copy', output_file])

# Create a temporary file to hold the list of remuxed video files
video_temp_file = tempfile.NamedTemporaryFile(delete=False)
print("Temporary file for video list created: {}".format(video_temp_file.name))
with open(video_temp_file.name, 'w') as f:
    for file in sorted(glob.glob(os.path.join(temp_dir, '*.mp4'))):
        f.write("file '{}'\n".format(file))

# Combine the videos using ffmpeg
print("Combining videos...")
subprocess.run(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', video_temp_file.name, '-c', 'copy', 'combined_video.mp4'])

# Download audio from YouTube if URL is provided
audio_file = None
if args.youtube:
    subprocess.run(['yt-dlp', '-f', 'bestaudio', '-o', 'downloaded_audio.%(ext)s', args.youtube])
    downloaded_file = glob.glob('downloaded_audio.*')[0]
    os.rename(downloaded_file, 'downloaded_audio.mp3')
    audio_file = 'downloaded_audio.mp3'
else:
    # Find the first audio file in the current directory
    audio_files = glob.glob('*.[mM][pP]3') + glob.glob('*.[wW][aA][vV]') + glob.glob('*.[aA][aA][cC]') + glob.glob('*.[fF][lL][aA][cC]')
    print("Found audio files: {}".format(audio_files))
    if audio_files:
        audio_file = sorted(audio_files)[0]
        print("Using audio file: {}".format(audio_file))
    else:
        print("No audio files found.")

# Add the audio file to the output video if available
if audio_file:
    if args.balance is None:
        # No balance provided, replace the video audio with the downloaded audio
        subprocess.run(['ffmpeg', '-i', 'combined_video.mp4', '-i', audio_file, '-c:v', 'copy', '-c:a', 'aac', '-map', '0:v:0', '-map', '1:a:0', '-shortest', '-fflags', '+genpts', 'output.mp4'])
    else:
        # Balance provided, mix the audio and video
        subprocess.run(['ffmpeg', '-i', 'combined_video.mp4', '-i', audio_file, '-filter_complex', f"[1:a]volume={args.balance}[a1];[0:a][a1]amix=inputs=2:duration=first:dropout_transition=2", '-c:v', 'copy', '-c:a', 'aac', '-shortest', '-fflags', '+genpts', 'output.mp4'])
else:
    # No audio file found, just rename the combined video
    os.rename('combined_video.mp4', 'output.mp4')

# Clean up the temporary files and directory
print("Cleaning up temporary files...")
os.remove(video_temp_file.name)
shutil.rmtree(temp_dir)
if os.path.exists('downloaded_audio.mp3'):
    os.remove('downloaded_audio.mp3')
if os.path.exists('combined_video.mp4'):
    os.remove('combined_video.mp4')

# Check if VLC is installed and open the output video in a new process
if shutil.which("vlc"):
    print("Opening output video with VLC...")
    subprocess.Popen(["vlc", "output.mp4"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
else:
    print("VLC is not installed.")