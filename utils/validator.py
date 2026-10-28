"""
Validatsiya moduli - kalitlar va fayllarni tekshirish
"""
import re
import os
from pathlib import Path

class Validator:
    # Qo'llab-quvvatlanadigan fayl formatlari
    SUPPORTED_FORMATS = {
        'text': ['.txt', '.doc', '.docx', '.pdf'],
        'spreadsheet': ['.xlsx', '.xls', '.csv'],
        'presentation': ['.ppt', '.pptx'],
        'code': ['.py', '.java', '.cpp', '.js', '.html', '.css'],
        'database': ['.db', '.sql'],
        'archive': ['.zip', '.rar', '.7z'],
        'data': ['.json', '.xml']
    }
    
    # Kalit patternlari
    KEY_PATTERNS = {
        'AES': r'^[0-9a-fA-F]{64}$',  # 256 bit = 64 hex
        'DES': r'^[0-9a-fA-F]{16}$',  # 64 bit = 16 hex
        'GOST': r'^[0-9a-fA-F]{64}$', # 256 bit = 64 hex
        'GOST Kuznechik': r'^[0-9a-fA-F]{64}$', # 256 bit = 64 hex
    }
    
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB
    
    @staticmethod
    def validate_file(file_path):
        """
        Faylni tekshirish
        Returns: (is_valid, error_message)
        """
        if not file_path:
            return False, "Fayl tanlanmadi"
        
        path = Path(file_path)
        
        # Fayl mavjudligini tekshirish
        if not path.exists():
            return False, "❌ Fayl topilmadi. Iltimos, mavjud faylni tanlang."
        
        # Fayl emasligini tekshirish
        if not path.is_file():
            return False, "❌ Bu fayl emas, katalog."
        
        # Fayl formatini tekshirish
        ext = path.suffix.lower()
        all_formats = []
        for formats in Validator.SUPPORTED_FORMATS.values():
            all_formats.extend(formats)
        
        if ext not in all_formats:
            return False, f"❌ Fayl formati qo'llab-quvvatlanmaydi: {ext}"
        
        # Fayl hajmini tekshirish
        file_size = path.stat().st_size
        if file_size > Validator.MAX_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            return False, f"❌ Fayl hajmi chegaradan oshdi: {size_mb:.2f} MB > 500 MB"
        
        if file_size == 0:
            return False, "❌ Fayl bo'sh (0 bayt)"
        
        return True, ""
    
    @staticmethod
    def validate_key(key, algorithm):
        """
        Kalitni tekshirish
        Returns: (is_valid, error_message)
        """
        if not key:
            return False, "Kalit kiritilmadi"
        
        if algorithm not in Validator.KEY_PATTERNS:
            return False, f"Noma'lum algoritm: {algorithm}"
        
        pattern = Validator.KEY_PATTERNS[algorithm]
        if not re.match(pattern, key):
            expected_len = {
                'AES': '64 hex belgi (256 bit)',
                'DES': '16 hex belgi (64 bit)',
                'GOST': '64 hex belgi (256 bit)'
            }
            return False, f"❌ Kalit formati noto'g'ri. {algorithm} uchun {expected_len[algorithm]} kerak."
        
        return True, ""
    
    @staticmethod
    def validate_output_path(output_path):
        """
        Natija yo'lini tekshirish
        """
        if not output_path:
            return False, "Natija yo'li kiritilmadi"
        
        path = Path(output_path)
        parent = path.parent
        
        # Parent katalog mavjudligini tekshirish
        if not parent.exists():
            return False, f"❌ Katalog topilmadi: {parent}"
        
        # Yozish ruxsatini tekshirish
        if not os.access(parent, os.W_OK):
            return False, "❌ Faylga yozish uchun ruxsat yo'q."
        
        return True, ""
    
    @staticmethod
    def get_all_supported_formats():
        """Barcha qo'llab-quvvatlanadigan formatlarni olish"""
        all_formats = []
        for formats in Validator.SUPPORTED_FORMATS.values():
            all_formats.extend(formats)
        return all_formats
    
    @staticmethod
    def format_file_filter():
        """Fayl tanlash dialogi uchun filter yaratish"""
        all_formats = Validator.get_all_supported_formats()
        formats_str = ' '.join(f'*{fmt}' for fmt in all_formats)
        return [
            ("Barcha qo'llab-quvvatlanadigan fayllar", formats_str),
            ("Matnli fayllar", "*.txt *.doc *.docx *.pdf"),
            ("Jadval fayllar", "*.xlsx *.xls *.csv"),
            ("Kod fayllar", "*.py *.java *.cpp *.js *.html *.css"),
            ("Barcha fayllar", "*.*")
        ]
