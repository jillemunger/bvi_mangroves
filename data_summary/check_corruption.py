import os
import wave

# Specify the directory you want to check
subdirectory = r"/Volumes/SeaBABELa/BVI Mangroves_2024/raw/Round 3/6532_HansB_R3"

# Traverse the subdirectory and check each file
for dirpath, dirnames, filenames in os.walk(subdirectory):
    for file_name in filenames:
        file_path = os.path.join(dirpath, file_name)
        
        # Check if the file is a WAV file
        if file_path.lower().endswith('.wav'):
            try:
                # Try to open the WAV file to check for corruption
                with wave.open(file_path, 'rb') as audio_file:
                    # If the file opens successfully, we assume it's not corrupt
                    print(f"{file_name}: OK")
            except wave.Error as e:
                print(f"{file_name}: WAV file is corrupt or unreadable - {e}")
            except Exception as e:
                print(f"{file_name}: An unexpected error occurred - {e}")
