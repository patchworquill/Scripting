#!/usr/bin/env python3
"""
Simple Randomized Drum Kit Generator

Run this script and it will ask you for:
- Input folder (where your samples are)
- Output folder (where to create drum kits)
- Number of files per kit
- File extensions to include
"""

import os
import random
import shutil
from pathlib import Path
from datetime import datetime


def get_audio_files(input_dir, extensions):
    """Find all audio files in the input directory and subdirectories."""
    audio_files = []
    
    # Convert extensions to lowercase for comparison
    extensions = [ext.lower().strip('.') for ext in extensions]
    
    print(f"Searching for audio files in: {input_dir}")
    
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            # Skip macOS resource fork files and Ableton analysis files
            if file.startswith('._') or file.endswith('.asd'):
                continue
            
            file_path = os.path.join(root, file)
            # Get file extension without the dot
            file_ext = os.path.splitext(file)[1].lower().strip('.')
            
            if file_ext in extensions:
                audio_files.append(file_path)
    
    return audio_files


def create_drum_kit(audio_files, output_dir, max_files, use_symlinks=False):
    """Create a drum kit by copying or symlinking random audio files."""
    if not audio_files:
        print("No audio files found!")
        return False
    
    # Create timestamp for unique folder name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    kit_name = f"DrumKit_{timestamp}"
    kit_dir = os.path.join(output_dir, kit_name)
    
    # Create the kit directory
    os.makedirs(kit_dir, exist_ok=True)
    
    # Select random files (up to max_files)
    num_files = min(len(audio_files), max_files)
    selected_files = random.sample(audio_files, num_files)
    
    print(f"\nCreating drum kit: {kit_name}")
    action = "Creating symlinks to" if use_symlinks else "Copying"
    print(f"{action} {num_files} files...")
    
    # Copy or symlink files to kit directory
    for source_file in selected_files:
        # Get just the filename from the full path
        filename = os.path.basename(source_file)
        # Keep original filename exactly as it is
        dest_path = os.path.join(kit_dir, filename)
        
        try:
            if use_symlinks:
                os.symlink(source_file, dest_path)
            else:
                shutil.copy2(source_file, dest_path)
            print(f"    {filename}")
        except Exception as e:
            print(f"  Error {'linking' if use_symlinks else 'copying'} {filename}: {e}")
            return False
    
    print(f"\n✓ Drum kit created successfully!")
    print(f"  Location: {kit_dir}")
    return True


def main():
    print("=" * 60)
    print("          Randomized Drum Kit Generator")
    print("=" * 60)
    print()
    
    # Choose mode
    print("Select mode:")
    print("1. Simple mode (guided setup)")
    print("2. Advanced mode (more options)")
    while True:
        mode_choice = input("Choose mode (1 or 2): ").strip()
        if mode_choice in ['1', '2']:
            advanced_mode = mode_choice == '2'
            break
        print("Please enter 1 or 2.")
    
    print()
    
    if advanced_mode:
        run_advanced_mode()
    else:
        run_simple_mode()


def run_simple_mode():
    """Run the original simple mode with guided prompts."""
    
def categorize_audio_files(audio_files):
    """
    Categorize audio files by instrument type based on filename patterns.
    Returns a dictionary with instrument categories as keys and file lists as values.
    """
    categories = {
        'kick': [],
        'snare': [],
        'hihat_closed': [],
        'hihat_open': [],
        'tom': [],
        'clap': [],
        'shaker': [],
        'crash': [],
        'perc': [],
        'other': []
    }
    
    # Define patterns for each instrument type (case-insensitive)
    patterns = {
        'kick': ['kick', 'bd', 'bass', 'bassdrum', 'bass drum', '808', 'sub', 'boom'],
        'snare': ['snare', 'sn', 'snr', 'snap', 'rim'],
        'hihat_closed': ['chh', 'closed hat', 'closedhat', 'closedhh', 'closed hihat', 'hihat closed', 'hh closed', 'hhc'],
        'hihat_open': ['ohh', 'open hat', 'openhat', 'openhh', 'open hihat', 'hihat open', 'hh open', 'hho'],
        'tom': ['tom', 'tm', 'floor tom', 'floortom', 'hi tom', 'hitom', 'mid tom', 'midtom'],
        'clap': ['clap', 'cp', 'handclap', 'hand clap'],
        'shaker': ['shaker', 'shake', 'shk', 'tambourine', 'tamb'],
        'crash': ['crash', 'cym', 'cymbal', 'ride'],
        'perc': ['perc', 'percussion', 'bongo', 'conga', 'wood', 'block', 'cowbell', 'bell', 'triangle']
    }
    
    for file_path in audio_files:
        filename = os.path.basename(file_path).lower()
        categorized = False
        
        # Check each category
        for category, keywords in patterns.items():
            for keyword in keywords:
                if keyword in filename:
                    categories[category].append(file_path)
                    categorized = True
                    break
            if categorized:
                break
        
        # If no category matched, put in 'other'
        if not categorized:
            categories['other'].append(file_path)
    
    return categories


def create_organized_drum_kit(categorized_files, output_dir, kit_name, kit_structure, use_symlinks=False):
    """
    Create an organized drum kit following the specified structure.
    kit_structure is a list of tuples: [(category, count), ...]
    """
    kit_dir = os.path.join(output_dir, kit_name)
    os.makedirs(kit_dir, exist_ok=True)
    
    print(f"\nCreating organized drum kit: {kit_name}")
    action = "Creating symlinks to" if use_symlinks else "Copying"
    
    total_files = 0
    used_files = set()  # Track used files to avoid duplicates
    
    # Create a pool of all available files for fallback
    all_files = []
    for category_files in categorized_files.values():
        all_files.extend(category_files)
    
    for category, count in kit_structure:
        available_files = categorized_files.get(category, [])
        
        if not available_files:
            print(f"  Warning: No {category} files found, will use random samples for those slots...")
            # Use random files from the pool for this category
            available_files = [f for f in all_files if f not in used_files]
            if not available_files:
                available_files = all_files  # Reset if we've used everything
        
        # Select random files from this category (up to requested count)
        num_files = min(len(available_files), count)
        if num_files == 0:
            continue
            
        selected_files = random.sample(available_files, num_files)
        used_files.update(selected_files)  # Mark these as used
        
        print(f"  {category.replace('_', ' ').title()}: {num_files} files")
        
        # Copy/link the selected files
        for source_file in selected_files:
            filename = os.path.basename(source_file)
            # Keep original filename exactly as it is
            dest_path = os.path.join(kit_dir, filename)
            
            try:
                if use_symlinks:
                    os.symlink(source_file, dest_path)
                else:
                    shutil.copy2(source_file, dest_path)
                print(f"    {filename}")
                total_files += 1
            except Exception as e:
                print(f"    Error {'linking' if use_symlinks else 'copying'} {filename}: {e}")
                return False
    
    print(f"✓ Organized drum kit created with {total_files} files")
    print(f"  Location: {kit_dir}")
    return True


def run_advanced_mode():
    """Run advanced mode with intelligent instrument categorization and organized kit structure."""
    print("=== ADVANCED MODE ===")
    print("Intelligent drum kit organization with instrument detection")
    print()
    
    # Get input directory (same as simple mode)
    while True:
        input_dir = input("Enter the path to your sample library folder: ").strip()
        input_dir = input_dir.strip('\'"')
        
        if os.path.exists(input_dir) and os.path.isdir(input_dir):
            break
        print("That folder doesn't exist. Please try again.")
    
    # Get output directory
    output_dir = input("Enter the output folder (where to save drum kits): ").strip()
    output_dir = output_dir.strip('\'"')
    if not os.path.exists(output_dir):
        print(f"Creating output directory: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
    
    # Get file extensions
    print("\nWhich audio file types to include?")
    print("Default: wav, aif, aiff, mp3, flac")
    extensions_input = input("Press Enter for default, or type extensions: ").strip()
    
    if extensions_input:
        extensions = extensions_input.split()
    else:
        extensions = ['wav', 'aif', 'aiff', 'mp3', 'flac']
    
    # Ask about copying vs symlinking
    print("\nFile handling options:")
    print("1. Create symbolic links (points to originals, saves disk space)")
    print("2. Copy files (duplicates files, uses more disk space)")
    while True:
        choice = input("Choose option (1 or 2): ").strip()
        if choice in ['1', '2']:
            use_symlinks = choice == '1'
            break
        print("Please enter 1 or 2.")
    
    print("\n" + "=" * 60)
    print("Scanning and categorizing audio files...")
    
    # Find and categorize all audio files
    audio_files = get_audio_files(input_dir, extensions)
    if not audio_files:
        print("No audio files found!")
        return
    
    categorized_files = categorize_audio_files(audio_files)
    
    # Show categorization results
    print(f"\nFound {len(audio_files)} total audio files:")
    for category, files in categorized_files.items():
        if files:
            print(f"  {category.replace('_', ' ').title()}: {len(files)} files")
    
    # Define kit structure (Ableton-optimized: kicks first, then snares)
    print("\nUsing Ableton-optimized kit structure:")
    kit_structure = [
        ('kick', 4),           # First 4 slots: kicks
        ('snare', 4),          # Next 4 slots: snares  
        ('hihat_closed', 2),   # Closed hihats
        ('hihat_open', 2),     # Open hihats
        ('clap', 1),           # Clap
        ('perc', 2),           # Percussion
        ('crash', 1),          # Crash/cymbal
    ]
    
    for category, count in kit_structure:
        available = len(categorized_files.get(category, []))
        print(f"  {category.replace('_', ' ').title()}: {count} slots ({available} available)")
    
    # Ask how many kits to generate
    while True:
        try:
            num_kits = int(input(f"\nHow many organized drum kits to generate? (1): ").strip() or "1")
            if num_kits > 0:
                break
            print("Please enter a number greater than 0.")
        except ValueError:
            print("Please enter a valid number.")
    
    print("\n" + "=" * 60)
    
    # Generate organized drum kits
    timestamp_base = datetime.now().strftime("%Y%m%d_%H%M%S")
    successful_kits = 0
    
    for kit_num in range(num_kits):
        if num_kits > 1:
            kit_name = f"OrganizedKit_{timestamp_base}_{kit_num+1:02d}"
        else:
            kit_name = f"OrganizedKit_{timestamp_base}"
        
        if create_organized_drum_kit(categorized_files, output_dir, kit_name, kit_structure, use_symlinks):
            successful_kits += 1
        
        # Wait between kits for unique timestamps
        if kit_num < num_kits - 1:
            import time
            time.sleep(1)
        
        print()  # Empty line between kits
    
    print("=" * 60)
    print(f"Generated {successful_kits}/{num_kits} organized drum kits successfully!")
    print("Perfect for drag & drop into Ableton Live!")
    print("Done!")
    # Placeholder - will add features based on user requirements


def run_simple_mode():
    """Run the original simple mode with guided prompts."""
    # Get input directory
    while True:
        input_dir = input("Enter the path to your sample library folder: ").strip()
        # Remove quotes if present (from drag & drop)
        input_dir = input_dir.strip('\'"')
        
        print(f"Checking path: '{input_dir}'")
        print(f"Path exists: {os.path.exists(input_dir)}")
        print(f"Is directory: {os.path.isdir(input_dir) if os.path.exists(input_dir) else 'N/A'}")
        
        if os.path.exists(input_dir) and os.path.isdir(input_dir):
            break
        print("That folder doesn't exist. Please try again.")
        
        # Suggest the parent directory if this one doesn't exist
        parent_dir = os.path.dirname(input_dir)
        if os.path.exists(parent_dir):
            print(f"Hint: Parent directory exists: {parent_dir}")
            print("Available folders in that directory:")
            try:
                items = os.listdir(parent_dir)
                folders = [item for item in items if os.path.isdir(os.path.join(parent_dir, item))]
                for folder in sorted(folders):
                    print(f"  - {folder}")
            except Exception as e:
                print(f"  Could not list directory: {e}")
            print("Maybe try one of these paths, or check the folder name spelling.")
    
    # Get output directory
    output_dir = input("Enter the output folder (where to save drum kits): ").strip()
    # Remove quotes if present (from drag & drop)
    output_dir = output_dir.strip('\'"')
    if not os.path.exists(output_dir):
        print(f"Creating output directory: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
    
    # Get number of files per kit
    while True:
        try:
            max_files = int(input("How many files per drum kit? (e.g., 10): ").strip())
            if max_files > 0:
                break
            print("Please enter a number greater than 0.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get file extensions
    print("Which audio file types to include?")
    print("Default: wav, aif, aiff, mp3, flac")
    extensions_input = input("Press Enter for default, or type extensions (e.g., wav mp3 aif): ").strip()
    
    if extensions_input:
        extensions = extensions_input.split()
    else:
        extensions = ['wav', 'aif', 'aiff', 'mp3', 'flac']
    
    print(f"\nLooking for files with extensions: {', '.join(extensions)}")
    
    # Ask about copying vs symlinking
    print("\nFile handling options:")
    print("1. Copy files (duplicates files, uses more disk space)")
    print("2. Create symbolic links (points to originals, saves disk space)")
    while True:
        choice = input("Choose option (1 or 2): ").strip()
        if choice in ['1', '2']:
            use_symlinks = choice == '2'
            break
        print("Please enter 1 or 2.")
    
    print("-" * 60)
    
    # Find all audio files
    audio_files = get_audio_files(input_dir, extensions)
    
    if not audio_files:
        print("No audio files found!")
        print(f"Searched for: {', '.join(extensions)}")
        print("Make sure your sample library contains files with these extensions.")
        return
    
    print(f"Found {len(audio_files)} audio files")
    
    # Ask how many kits to generate
    while True:
        try:
            num_kits = int(input(f"\nHow many drum kits to generate? (1): ").strip() or "1")
            if num_kits > 0:
                break
            print("Please enter a number greater than 0.")
        except ValueError:
            print("Please enter a valid number.")
    
    print("\n" + "=" * 60)
    
    # Generate drum kits
    successful_kits = 0
    for kit_num in range(num_kits):
        if create_drum_kit(audio_files, output_dir, max_files, use_symlinks):
            successful_kits += 1
        
        # Wait a second between kits to ensure unique timestamps
        if kit_num < num_kits - 1:
            import time
            time.sleep(1)
    
    print("=" * 60)
    print(f"Generated {successful_kits}/{num_kits} drum kits successfully!")
    print("Done!")


if __name__ == "__main__":
    main()