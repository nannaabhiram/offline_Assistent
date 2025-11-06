"""
File System Control Module
Handles file and folder operations
"""
import os
import shutil
from pathlib import Path
from typing import Dict, List, Any


def list_files(folder: str) -> Dict[str, Any]:
    """List files in a folder"""
    try:
        files = os.listdir(folder)
        return {
            'success': True,
            'message': f'Found {len(files)} files in {folder}',
            'folder': folder,
            'files': files,
            'count': len(files)
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to list files: {str(e)}',
            'folder': folder
        }


def copy_file(src: str, dst: str) -> Dict[str, Any]:
    """Copy a file"""
    try:
        # Create destination folder if needed
        dst_folder = os.path.dirname(dst)
        if dst_folder:
            Path(dst_folder).mkdir(parents=True, exist_ok=True)
        
        shutil.copy(src, dst)
        return {
            'success': True,
            'message': f'Copied {src} to {dst}',
            'source': src,
            'destination': dst
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to copy file: {str(e)}',
            'source': src,
            'destination': dst
        }


def move_file(src: str, dst: str) -> Dict[str, Any]:
    """Move a file"""
    try:
        # Create destination folder if needed
        dst_folder = os.path.dirname(dst)
        if dst_folder:
            Path(dst_folder).mkdir(parents=True, exist_ok=True)
        
        shutil.move(src, dst)
        return {
            'success': True,
            'message': f'Moved {src} to {dst}',
            'source': src,
            'destination': dst
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to move file: {str(e)}',
            'source': src,
            'destination': dst
        }


def delete_file(path: str) -> Dict[str, Any]:
    """Delete a file"""
    try:
        if os.path.isfile(path):
            os.remove(path)
            return {
                'success': True,
                'message': f'Deleted file: {path}',
                'path': path
            }
        else:
            return {
                'success': False,
                'message': f'File not found: {path}',
                'path': path
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to delete file: {str(e)}',
            'path': path
        }


def create_folder(path: str) -> Dict[str, Any]:
    """Create a folder"""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return {
            'success': True,
            'message': f'Created folder: {path}',
            'path': path
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to create folder: {str(e)}',
            'path': path
        }


def delete_folder(path: str, recursive: bool = False) -> Dict[str, Any]:
    """Delete a folder"""
    try:
        if recursive:
            shutil.rmtree(path)
            return {
                'success': True,
                'message': f'Deleted folder recursively: {path}',
                'path': path
            }
        else:
            os.rmdir(path)
            return {
                'success': True,
                'message': f'Deleted empty folder: {path}',
                'path': path
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to delete folder: {str(e)}',
            'path': path
        }


def get_file_info(path: str) -> Dict[str, Any]:
    """Get file information"""
    try:
        if not os.path.exists(path):
            return {
                'success': False,
                'message': f'File not found: {path}',
                'path': path
            }
        
        stats = os.stat(path)
        size_mb = round(stats.st_size / (1024 * 1024), 2)
        file_type = 'Directory' if os.path.isdir(path) else 'File'
        
        return {
            'success': True,
            'message': f'{file_type}: {path} ({size_mb} MB)',
            'path': path,
            'size': stats.st_size,
            'size_mb': size_mb,
            'created': stats.st_ctime,
            'modified': stats.st_mtime,
            'is_file': os.path.isfile(path),
            'is_dir': os.path.isdir(path)
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Failed to get file info: {str(e)}',
            'path': path
        }
