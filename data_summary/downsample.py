# This script downsamples .wav files from 96kHz to 48kHz in a specified directory
# and saves them to a different output directory.
# It uses the pydub library for audio processing and the os library for file system operations.
# Enhanced to skip macOS system files and hidden files.

import os
from pydub import AudioSegment
from pydub.exceptions import CouldntEncodeError

def is_system_file(filename):
    """
    Check if a file is a macOS system file that should be skipped.
    
    Args:
        filename (str): The filename to check
    
    Returns:
        bool: True if it's a system file that should be skipped
    """
    # Skip files that start with . (hidden files and resource forks)
    if filename.startswith('.'):
        return True
    
    # Skip common macOS system files
    system_files = ['.DS_Store', 'Thumbs.db', '.Spotlight-V100', '.Trashes']
    if filename in system_files:
        return True
    
    return False

def downsample_wav_files(source_folder, dest_folder):
    """
    Downsamples .wav files from 96kHz to 48kHz from a source folder and
    saves them to a destination folder.
    
    Args:
        source_folder (str): The path to the folder containing the source .wav files.
        dest_folder (str): The path where the downsampled files will be saved.
    """
    if not os.path.isdir(source_folder):
        print(f"Error: The source folder '{source_folder}' does not exist.")
        return

    # Create the destination folder if it doesn't exist
    if not os.path.exists(dest_folder):
        print(f"Creating destination folder: '{dest_folder}'")
        os.makedirs(dest_folder)

    print(f"Scanning source folder: {source_folder}\n")
    
    processed_count = 0
    skipped_count = 0
    error_count = 0
    
    for filename in os.listdir(source_folder):
        # Skip system files and hidden files
        if is_system_file(filename):
            print(f"Skipping system file: '{filename}'")
            skipped_count += 1
            continue
        
        # Check if the file is a .wav file
        if filename.lower().endswith(".wav"):
            file_path = os.path.join(source_folder, filename)
            
            # Additional check: make sure it's actually a file (not a directory)
            if not os.path.isfile(file_path):
                print(f"Skipping '{filename}' - not a regular file")
                skipped_count += 1
                continue
            
            try:
                # Load the audio file
                audio = AudioSegment.from_wav(file_path)
                
                # Check if the sample rate is 96kHz (96000 Hz)
                if audio.frame_rate == 96000:
                    print(f"Processing '{filename}' (96kHz → 48kHz)...")
                    
                    # Set the new sample rate to 48kHz
                    downsampled_audio = audio.set_frame_rate(48000)
                    
                    # Create the output path, maintaining the original filename
                    output_path = os.path.join(dest_folder, filename)
                    
                    # Export the downsampled audio to the new file
                    downsampled_audio.export(output_path, format="wav")
                    print(f"✓ Successfully saved as '{output_path}'")
                    processed_count += 1
                    
                else:
                    print(f"Skipping '{filename}' - sample rate is {audio.frame_rate} Hz (not 96kHz)")
                    skipped_count += 1
                    
            except CouldntEncodeError:
                print(f"✗ Error: Could not encode '{filename}'. Please ensure you have ffmpeg installed.")
                error_count += 1
            except Exception as e:
                print(f"✗ Error processing '{filename}': {e}")
                error_count += 1
        else:
            print(f"Skipping '{filename}' - not a .wav file")
            skipped_count += 1

    print(f"\n=== Summary ===")
    print(f"Files processed: {processed_count}")
    print(f"Files skipped: {skipped_count}")
    print(f"Errors encountered: {error_count}")
    print("Downsampling process complete.")

if __name__ == "__main__":
    source_path = "/Volumes/theporp/Aquafort_2025/Aquafort_2025_soundfiles"
    destination_path = "/Volumes/theporp/Aquafort_2025/Aquafort_2025_48khz"
    downsample_wav_files(source_path, destination_path)