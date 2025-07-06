#!/usr/bin/env python3
"""
Cache cleanup script for the AI Finance Agent project.

This script helps clean up cache files and temporary data to keep the project directory clean.
"""

import os
import shutil
from pathlib import Path

def cleanup_cache():
    """Clean up cache files and temporary data."""
    print("🧹 Cleaning up cache files...")
    print("=" * 40)
    
    # Define cache directories (from utils folder)
    base_dir = Path(__file__).parent.parent
    cache_dirs = [
        base_dir / "backend" / "cache",
        base_dir / "backend" / "annual_report_processor" / "cache",
        base_dir / "backend" / "uploads",
        base_dir / "__pycache__",
        base_dir / "backend" / "__pycache__",
        base_dir / "backend" / "annual_report_processor" / "__pycache__",
        base_dir / "backend" / "company data" / "__pycache__"
    ]
    
    total_freed = 0
    
    for cache_dir in cache_dirs:
        if cache_dir.exists():
            try:
                # Calculate size before deletion
                size_before = get_dir_size(cache_dir)
                
                # Remove the directory
                shutil.rmtree(cache_dir)
                
                total_freed += size_before
                print(f"✅ Cleaned: {cache_dir.relative_to(base_dir)} ({format_size(size_before)})")
                
            except Exception as e:
                print(f"⚠️  Could not clean {cache_dir.relative_to(base_dir)}: {e}")
        else:
            print(f"ℹ️  Not found: {cache_dir.relative_to(base_dir)}")
    
    print(f"\n🎉 Total space freed: {format_size(total_freed)}")
    return total_freed

def get_dir_size(path):
    """Get the total size of a directory in bytes."""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
    except Exception:
        pass
    return total_size

def format_size(size_bytes):
    """Format size in bytes to human readable format."""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def show_cache_info():
    """Show information about current cache usage."""
    print("📊 Cache Usage Information")
    print("=" * 30)
    
    base_dir = Path(__file__).parent.parent
    cache_dirs = [
        base_dir / "backend" / "cache",
        base_dir / "backend" / "annual_report_processor" / "cache",
        base_dir / "backend" / "uploads"
    ]
    
    total_size = 0
    
    for cache_dir in cache_dirs:
        if cache_dir.exists():
            size = get_dir_size(cache_dir)
            total_size += size
            print(f"{cache_dir.relative_to(base_dir)}: {format_size(size)}")
        else:
            print(f"{cache_dir.relative_to(base_dir)}: Not found")
    
    print(f"\nTotal cache size: {format_size(total_size)}")

def main():
    """Main function."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--info":
        show_cache_info()
    else:
        print("AI Finance Agent - Cache Cleanup")
        print("=" * 30)
        print("This will remove all cache files and temporary data.")
        print("Use --info flag to see current cache usage without cleaning.")
        print()
        
        response = input("Do you want to proceed with cleanup? (y/N): ")
        if response.lower() in ['y', 'yes']:
            cleanup_cache()
        else:
            print("Cleanup cancelled.")

if __name__ == "__main__":
    main() 