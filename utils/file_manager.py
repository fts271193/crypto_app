"""
Fayl boshqarish moduli - fayl o'qish va yozish
"""
import os
from pathlib import Path

class FileManager:
    CHUNK_SIZE = 64 * 1024  # 64 KB chunks
    
    @staticmethod
    def read_file(file_path, callback=None):
        """
        Faylni o'qish
        Args:
            file_path: Fayl yo'li
            callback: Progress callback funksiyasi
        Returns:
            bytes: Fayl ma'lumotlari
        """
        path = Path(file_path)
        file_size = path.stat().st_size
        
        data = bytearray()
        bytes_read = 0
        
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(FileManager.CHUNK_SIZE)
                if not chunk:
                    break
                
                data.extend(chunk)
                bytes_read += len(chunk)
                
                if callback:
                    progress = (bytes_read / file_size) * 100
                    callback(progress, bytes_read, file_size)
        
        return bytes(data)
    
    @staticmethod
    def write_file(file_path, data, callback=None):
        """
        Faylga yozish
        Args:
            file_path: Fayl yo'li
            data: Yozish uchun ma'lumot
            callback: Progress callback
        """
        total_size = len(data)
        bytes_written = 0
        
        with open(file_path, 'wb') as f:
            # Katta fayllar uchun chunk'lar bilan yozish
            for i in range(0, total_size, FileManager.CHUNK_SIZE):
                chunk = data[i:i + FileManager.CHUNK_SIZE]
                f.write(chunk)
                bytes_written += len(chunk)
                
                if callback:
                    progress = (bytes_written / total_size) * 100
                    callback(progress, bytes_written, total_size)
    
    @staticmethod
    def get_output_filename(input_path, suffix='.encrypted'):
        """
        Chiqish fayl nomini yaratish
        Args:
            input_path: Kirish fayl yo'li
            suffix: Qo'shiladigan suffix
        Returns:
            str: Chiqish fayl yo'li
        """
        path = Path(input_path)
        output_name = path.stem + suffix + path.suffix
        return str(path.parent / output_name)
    
    @staticmethod
    def get_decrypted_filename(encrypted_path):
        """
        Deshifrlangan fayl nomini yaratish
        """
        path = Path(encrypted_path)
        name = path.stem
        
        # .encrypted suffiksini olib tashlash
        if name.endswith('.encrypted'):
            name = name[:-10]
        
        # .decrypted qo'shish
        output_name = name + '.decrypted' + path.suffix
        return str(path.parent / output_name)
    
    @staticmethod
    def ensure_directory(file_path):
        """
        Fayl uchun katalog mavjudligini ta'minlash
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def get_file_info(file_path):
        """
        Fayl haqida ma'lumot
        """
        path = Path(file_path)
        
        if not path.exists():
            return None
        
        stat = path.stat()
        
        return {
            'name': path.name,
            'size': stat.st_size,
            'size_formatted': FileManager._format_size(stat.st_size),
            'extension': path.suffix,
            'directory': str(path.parent),
            'modified': stat.st_mtime
        }
    
    @staticmethod
    def _format_size(size_bytes):
        """Hajmni formatlash"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
