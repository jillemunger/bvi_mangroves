"""
Enhanced WAV File Checker and Cleaner

This script checks WAV files for corruption and problematic characteristics that might
cause issues with audio analysis tools like pyporcc. It identifies and optionally removes:
- macOS system files (._ files, .DS_Store, etc.)
- Corrupted or unreadable WAV files
- Very small files (likely incomplete downloads or corrupted)
- Empty audio files (files with headers but no actual audio data)

The script provides detailed information about each file (size, duration, sample rate, channels)
and can run in check-only mode or cleanup mode. It's particularly useful for preparing
audio datasets for batch processing tools that may fail on problematic files.
"""

import os
import wave

def is_system_file(filename):
    """
    Check if a file is a macOS system file that should be skipped.
    """
    # Skip files that start with . (hidden files and resource forks)
    if filename.startswith('.'):
        return True
    
    # Skip common macOS system files
    system_files = ['.DS_Store', 'Thumbs.db', '.Spotlight-V100', '.Trashes']
    if filename in system_files:
        return True
    
    return False

def check_and_clean_wav_files(subdirectory, remove_corrupt=False, remove_small=False, min_size_kb=1):
    """
    Check WAV files for corruption and optionally remove problematic files.
    
    Args:
        subdirectory (str): Directory to check
        remove_corrupt (bool): If True, delete corrupt files
        remove_small (bool): If True, delete files smaller than min_size_kb
        min_size_kb (int): Minimum file size in KB (default 1KB)
    """
    
    print(f"Checking WAV files in: {subdirectory}")
    print(f"Remove corrupt files: {remove_corrupt}")
    print(f"Remove small files (<{min_size_kb}KB): {remove_small}")
    print("-" * 60)
    
    stats = {
        'total_files': 0,
        'ok_files': 0,
        'corrupt_files': 0,
        'small_files': 0,
        'system_files': 0,
        'removed_files': 0
    }
    
    # Traverse the subdirectory and check each file
    for dirpath, dirnames, filenames in os.walk(subdirectory):
        for file_name in filenames:
            file_path = os.path.join(dirpath, file_name)
            
            # Check if the file is a WAV file
            if file_path.lower().endswith('.wav'):
                stats['total_files'] += 1
                
                # Skip macOS system files
                if is_system_file(file_name):
                    print(f"{file_name}: SYSTEM FILE - skipping")
                    stats['system_files'] += 1
                    if remove_corrupt:  # Remove system files if cleanup is enabled
                        try:
                            os.remove(file_path)
                            print("  → Removed system file")
                            stats['removed_files'] += 1
                        except OSError as e:
                            print(f"  → Failed to remove: {e}")
                    continue
                
                # Check file size
                file_size = os.path.getsize(file_path)
                file_size_kb = file_size / 1024
                
                if file_size < (min_size_kb * 1024):
                    print(f"{file_name}: VERY SMALL ({file_size_kb:.1f}KB - likely corrupt)")
                    stats['small_files'] += 1
                    if remove_small:
                        try:
                            os.remove(file_path)
                            print("  → Removed small file")
                            stats['removed_files'] += 1
                        except OSError as e:
                            print(f"  → Failed to remove: {e}")
                    continue
                
                # Try to open the WAV file to check for corruption
                try:
                    with wave.open(file_path, 'rb') as audio_file:
                        # Get some basic info about the file
                        frames = audio_file.getnframes()
                        sample_rate = audio_file.getframerate()
                        channels = audio_file.getnchannels()
                        duration = frames / sample_rate if sample_rate > 0 else 0
                        
                        # Additional checks
                        if frames == 0:
                            print(f"{file_name}: EMPTY (no audio frames)")
                            stats['corrupt_files'] += 1
                            if remove_corrupt:
                                try:
                                    os.remove(file_path)
                                    print("  → Removed empty file")
                                    stats['removed_files'] += 1
                                except OSError as e:
                                    print(f"  → Failed to remove: {e}")
                        else:
                            print(f"{file_name}: OK ({file_size_kb:.1f}KB, {duration:.1f}s, {sample_rate}Hz, {channels}ch)")
                            stats['ok_files'] += 1
                            
                except wave.Error as e:
                    print(f"{file_name}: CORRUPT WAV - {e}")
                    stats['corrupt_files'] += 1
                    if remove_corrupt:
                        try:
                            os.remove(file_path)
                            print("  → Removed corrupt file")
                            stats['removed_files'] += 1
                        except OSError as e:
                            print(f"  → Failed to remove: {e}")
                            
                except Exception as e:
                    print(f"{file_name}: UNEXPECTED ERROR - {e}")
                    stats['corrupt_files'] += 1
                    if remove_corrupt:
                        try:
                            os.remove(file_path)
                            print("  → Removed problematic file")
                            stats['removed_files'] += 1
                        except OSError as e:
                            print(f"  → Failed to remove: {e}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"Total WAV files found: {stats['total_files']}")
    print(f"OK files: {stats['ok_files']}")
    print(f"Corrupt files: {stats['corrupt_files']}")
    print(f"Small files: {stats['small_files']}")
    print(f"System files: {stats['system_files']}")
    if remove_corrupt or remove_small:
        print(f"Files removed: {stats['removed_files']}")
    
    return stats

def test_specific_files(file_list, base_directory):
    """
    Test specific files that pyporcc flagged as corrupted
    """
    print("=== TESTING PYPORCC-FLAGGED FILES ===")
    
    for filename in file_list:
        file_path = os.path.join(base_directory, filename)
        if os.path.exists(file_path):
            try:
                with wave.open(file_path, 'rb') as audio_file:
                    frames = audio_file.getnframes()
                    sample_rate = audio_file.getframerate()
                    channels = audio_file.getnchannels()
                    duration = frames / sample_rate if sample_rate > 0 else 0
                    file_size = os.path.getsize(file_path)
                    
                    print(f"✓ {filename}: OK - {file_size/1024/1024:.1f}MB, {duration:.1f}s, {sample_rate}Hz")
            except Exception as e:
                print(f"✗ {filename}: ERROR - {e}")
        else:
            print(f"? {filename}: FILE NOT FOUND")

# Example usage - update the path to your directory
if __name__ == "__main__":
    # Your directory
    subdirectory = r"/Volumes/theporp/Aquafort_2025/Aquafort_2025_48khz"
    
    # Test the specific files pyporcc flagged as corrupted
    flagged_files = [
        "aquafort_6863_20250621_011418.wav",
        "aquafort_6863_20250621_041229.wav", 
        "aquafort_6863_20250621_071033.wav",
        "aquafort_6863_20250621_100912.wav",
        "aquafort_6863_20250621_130803.wav",
        "aquafort_6863_20250622_005519.wav"  # Just test a few
    ]
    
    test_specific_files(flagged_files, subdirectory)
    
    print("\n" + "="*60)
    
    # First, just check without removing anything
    print("=== CHECKING ALL FILES (no removal) ===")
    stats = check_and_clean_wav_files(subdirectory, remove_corrupt=False, remove_small=False)
    
    # If you want to clean up, uncomment one of these:
    
    # Option 1: Remove only corrupt files, keep small files for manual inspection
    # print("\n=== REMOVING CORRUPT FILES ===")
    # stats = check_and_clean_wav_files(subdirectory, remove_corrupt=True, remove_small=False)
    
    # Option 2: Remove both corrupt and very small files
    # print("\n=== REMOVING CORRUPT AND SMALL FILES ===")
    # stats = check_and_clean_wav_files(subdirectory, remove_corrupt=True, remove_small=True, min_size_kb=1)
    
    if stats['corrupt_files'] > 0 or stats['small_files'] > 0 or stats['system_files'] > 0:
        print(f"\n⚠ Found {stats['corrupt_files']} corrupt, {stats['small_files']} small, and {stats['system_files']} system files.")
        print("Uncomment the cleanup options in the script to remove them automatically.")
    else:
        print(f"\n✓ All {stats['ok_files']} WAV files appear to be valid!")
        print("The issue might be with pyporcc configuration rather than file corruption.")