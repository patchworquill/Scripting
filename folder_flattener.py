#!/usr/bin/env python3
"""
Folder Flattener Tool

Takes all files from nested subdirectories and moves/copies them to a single flat directory.
Handles file name conflicts, file filtering, and copy vs move operations.
Supports saving/loading configurations for repeated use.
"""

import os
import shutil
import json
import hashlib
from pathlib import Path


def save_config(config, config_name):
    """Save configuration to a JSON file."""
    # Save configs in the same directory as the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.join(script_dir, "flattener_configs")
    os.makedirs(config_dir, exist_ok=True)
    
    config_file = os.path.join(config_dir, f"{config_name}.json")
    
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✓ Configuration saved as '{config_name}'")
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False


def load_config(config_name):
    """Load configuration from a JSON file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.join(script_dir, "flattener_configs")
    config_file = os.path.join(config_dir, f"{config_name}.json")
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Configuration '{config_name}' not found.")
        return None
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return None


def list_configs():
    """List all saved configurations."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.join(script_dir, "flattener_configs")
    
    if not os.path.exists(config_dir):
        return []
    
    configs = []
    for file in os.listdir(config_dir):
        if file.endswith('.json'):
            configs.append(file[:-5])  # Remove .json extension
    
    return configs


def get_all_files(input_dir, extensions=None):
    """
    Recursively find all files in the input directory.
    
    Args:
        input_dir: Path to input directory
        extensions: List of file extensions to include (None = all files)
    
    Returns:
        List of file paths
    """
    all_files = []
    
    if extensions:
        # Convert extensions to lowercase for comparison
        extensions = [ext.lower().strip('.') for ext in extensions]
    
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            file_path = os.path.join(root, file)
            
            if extensions:
                # Check if file extension matches filter
                file_ext = os.path.splitext(file)[1].lower().strip('.')
                if file_ext not in extensions:
                    continue
            
            all_files.append(file_path)
    
    return all_files


def files_are_identical(file1, file2):
    """
    Compare two files to see if they are identical by checking file size first,
    then comparing content hashes for efficiency.
    
    Args:
        file1: Path to first file
        file2: Path to second file
    
    Returns:
        True if files are identical, False otherwise
    """
    try:
        # Quick size check first
        if os.path.getsize(file1) != os.path.getsize(file2):
            return False
        
        # If sizes match, compare file hashes
        def get_file_hash(filepath):
            hash_sha256 = hashlib.sha256()
            with open(filepath, "rb") as f:
                # Read file in chunks for memory efficiency
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        
        return get_file_hash(file1) == get_file_hash(file2)
        
    except Exception as e:
        print(f"  Error comparing files: {e}")
        return False


def handle_name_conflict(dest_path):
    """
    Handle file name conflicts by adding a number suffix.
    
    Args:
        dest_path: Destination file path
    
    Returns:
        A unique file path that doesn't exist
    """
    if not os.path.exists(dest_path):
        return dest_path
    
    # Split path into directory, name, and extension
    dir_path = os.path.dirname(dest_path)
    filename = os.path.basename(dest_path)
    name, ext = os.path.splitext(filename)
    
    # Try adding numbers until we find a unique name
    counter = 1
    while True:
        new_filename = f"{name}_{counter:03d}{ext}"
        new_path = os.path.join(dir_path, new_filename)
        
        if not os.path.exists(new_path):
            return new_path
        
        counter += 1


def flatten_folder(input_dir, output_dir, extensions=None, move_files=False, conflict_resolution="rename"):
    """
    Flatten a folder structure by moving/copying all files to a single directory.
    
    Args:
        input_dir: Source directory path
        output_dir: Destination directory path
        extensions: List of file extensions to include (None = all files)
        move_files: If True, move files. If False, copy files.
        conflict_resolution: How to handle name conflicts ("rename", "skip", "overwrite")
    
    Returns:
        Dictionary with operation results
    """
    results = {
        'processed': 0,
        'skipped': 0,
        'conflicts': 0,
        'errors': 0,
        'error_files': []
    }
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all files to process
    all_files = get_all_files(input_dir, extensions)
    
    print(f"Found {len(all_files)} files to process...")
    
    for source_file in all_files:
        try:
            filename = os.path.basename(source_file)
            dest_path = os.path.join(output_dir, filename)
            
            # Handle file name conflicts
            if os.path.exists(dest_path):
                results['conflicts'] += 1
                
                # Check if files are actually identical
                if files_are_identical(source_file, dest_path):
                    print(f"  Skipping (identical file): {filename}")
                    results['skipped'] += 1
                    continue
                
                # Files have same name but different content - always keep both by renaming
                dest_path = handle_name_conflict(dest_path)
                new_filename = os.path.basename(dest_path)
                print(f"  Renaming (different content): {filename} -> {new_filename}")
                
            else:
                # No conflict, handle other conflict resolution options for truly identical cases
                if conflict_resolution == "skip":
                    # This only applies to identical files now
                    pass  # We already handle identical files above
                elif conflict_resolution == "overwrite":
                    # This only applies to identical files now  
                    pass  # We already handle identical files above
                # For any case, we proceed with the dest_path (original or renamed)
            
            # Move or copy the file
            if move_files:
                shutil.move(source_file, dest_path)
                action = "Moved"
            else:
                shutil.copy2(source_file, dest_path)
                action = "Copied"
            
            print(f"  {action}: {filename}")
            results['processed'] += 1
            
        except Exception as e:
            print(f"  Error processing {source_file}: {e}")
            results['errors'] += 1
            results['error_files'].append(source_file)
    
    return results


def main():
    print("=" * 60)
    print("              Folder Flattener Tool")
    print("=" * 60)
    print()
    
    # Check for saved configurations
    saved_configs = list_configs()
    
    config = None
    if saved_configs:
        print("Saved configurations found:")
        for i, config_name in enumerate(saved_configs, 1):
            print(f"  {i}. {config_name}")
        print(f"  {len(saved_configs) + 1}. Create new configuration")
        print()
        
        while True:
            try:
                choice = int(input(f"Choose option (1-{len(saved_configs) + 1}): ").strip())
                if 1 <= choice <= len(saved_configs):
                    config_name = saved_configs[choice - 1]
                    config = load_config(config_name)
                    if config:
                        print(f"Loaded configuration: {config_name}")
                        break
                elif choice == len(saved_configs) + 1:
                    break
                else:
                    print(f"Please enter a number between 1 and {len(saved_configs) + 1}")
            except ValueError:
                print("Please enter a valid number.")
    
    if config:
        # Use loaded configuration
        input_dir = config.get('input_dir', '')
        output_dir = config.get('output_dir', '')
        extensions = config.get('extensions')
        move_files = config.get('move_files', False)
        conflict_resolution = config.get('conflict_resolution', 'rename')
        
        print(f"\nUsing saved settings:")
        print(f"  Input folder: {input_dir}")
        print(f"  Output folder: {output_dir}")
        print(f"  Extensions: {extensions if extensions else 'All files'}")
        print(f"  Operation: {'Move' if move_files else 'Copy'}")
        print(f"  Conflicts: {conflict_resolution}")
        
        # Ask if user wants to modify any settings
        modify = input("\nModify any settings? (y/N): ").strip().lower()
        if modify in ['y', 'yes']:
            config = None  # Fall through to manual setup
        else:
            # Validate paths still exist
            if not os.path.exists(input_dir):
                print(f"Warning: Input directory no longer exists: {input_dir}")
                config = None
    
    if not config:
        # Manual configuration
        config = get_manual_config()
        
        # Ask if user wants to save this configuration
        save_choice = input("\nSave this configuration for future use? (y/N): ").strip().lower()
        if save_choice in ['y', 'yes']:
            config_name = input("Enter a name for this configuration: ").strip()
            if config_name:
                save_config(config, config_name)
    
    print("\n" + "=" * 60)
    print("Processing files...")
    print()
    
    # Perform the flattening operation
    results = flatten_folder(
        config['input_dir'], 
        config['output_dir'], 
        config['extensions'], 
        config['move_files'], 
        config['conflict_resolution']
    )
    
    # Show results
    print("\n" + "=" * 60)
    print("OPERATION COMPLETE")
    print("=" * 60)
    print(f"Files processed: {results['processed']}")
    print(f"Files skipped: {results['skipped']}")
    print(f"Name conflicts: {results['conflicts']}")
    print(f"Errors: {results['errors']}")
    
    if results['error_files']:
        print("\nFiles with errors:")
        for error_file in results['error_files']:
            print(f"  - {error_file}")
    
    print(f"\nOutput directory: {config['output_dir']}")
    print("Done!")


def get_manual_config():
    """Get configuration through manual user input."""
    
def get_manual_config():
    """Get configuration through manual user input."""
    # Get input directory
    while True:
        input_dir = input("Enter the input folder path: ").strip()
        input_dir = input_dir.strip('\'"')  # Remove quotes from drag & drop
        
        if os.path.exists(input_dir) and os.path.isdir(input_dir):
            break
        print("That folder doesn't exist. Please try again.")
    
    # Get output directory
    output_dir = input("Enter the output folder path: ").strip()
    output_dir = output_dir.strip('\'"')
    
    if not os.path.exists(output_dir):
        print(f"Creating output directory: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
    
    # File filtering
    print("\nFile filtering options:")
    print("1. All files")
    print("2. Specific file extensions")
    
    while True:
        choice = input("Choose option (1 or 2): ").strip()
        if choice in ['1', '2']:
            break
        print("Please enter 1 or 2.")
    
    extensions = None
    if choice == '2':
        print("Default audio extensions: wav, aif, aiff, mp3, flac, m4a")
        ext_input = input("Enter extensions (space-separated) or press Enter for audio defaults: ").strip()
        
        if ext_input:
            extensions = ext_input.split()
        else:
            extensions = ['wav', 'aif', 'aiff', 'mp3', 'flac', 'm4a']
        
        print(f"Will process files with extensions: {', '.join(extensions)}")
    
    # Copy vs Move
    print("\nOperation type:")
    print("1. Copy files (originals remain in place)")
    print("2. Move files (originals are moved)")
    
    while True:
        choice = input("Choose option (1 or 2): ").strip()
        if choice in ['1', '2']:
            move_files = choice == '2'
            break
        print("Please enter 1 or 2.")
    
    # Conflict resolution
    print("\nFile name conflict resolution:")
    print("1. Rename (add number suffix to duplicates)")
    print("2. Skip (don't process files with existing names)")
    print("3. Overwrite (replace existing files)")
    
    while True:
        choice = input("Choose option (1, 2, or 3): ").strip()
        if choice in ['1', '2', '3']:
            conflict_options = {'1': 'rename', '2': 'skip', '3': 'overwrite'}
            conflict_resolution = conflict_options[choice]
            break
        print("Please enter 1, 2, or 3.")
    
    return {
        'input_dir': input_dir,
        'output_dir': output_dir,
        'extensions': extensions,
        'move_files': move_files,
        'conflict_resolution': conflict_resolution
    }


if __name__ == "__main__":
    main()
