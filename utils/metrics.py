"""
Performance metrics moduli - vaqt va tezlikni o'lchash
"""
import time
from datetime import datetime

class PerformanceMetrics:
    def __init__(self):
        self.file_size = 0  # Bayt
        self.read_time = 0  # Soniya
        self.key_prep_time = 0  # Kalit tayyorlash vaqti
        self.encrypt_time = 0  # Shifrlash vaqti
        self.decrypt_time = 0  # Deshifrlash vaqti
        self.write_time = 0  # Yozish vaqti
        self.total_time = 0  # Umumiy vaqt
        self.speed = 0  # MB/s
        
        self.algorithm = ""
        self.filename = ""
        self.output_filename = ""
        self.iv = ""  # Initialization Vector
        
        self.start_time = None
        self.end_time = None
    
    def start_timer(self):
        """Umumiy taymer boshlash"""
        self.start_time = time.time()
    
    def stop_timer(self):
        """Umumiy taymerni to'xtatish"""
        if self.start_time:
            self.end_time = time.time()
            self.total_time = self.end_time - self.start_time
            self.calculate_speed()
    
    def calculate_speed(self):
        """Tezlikni hisoblash (MB/s)"""
        if self.total_time > 0:
            self.speed = self.file_size / self.total_time / (1024 * 1024)
        else:
            self.speed = 0
    
    def format_size(self, size_bytes):
        """Hajmni formatlash"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def get_summary(self):
        """Qisqacha natijalar"""
        return {
            'algorithm': self.algorithm,
            'filename': self.filename,
            'file_size': self.file_size,
            'file_size_formatted': self.format_size(self.file_size),
            'read_time': round(self.read_time, 3),
            'key_prep_time': round(self.key_prep_time, 3),
            'encrypt_time': round(self.encrypt_time, 3),
            'decrypt_time': round(self.decrypt_time, 3),
            'write_time': round(self.write_time, 3),
            'total_time': round(self.total_time, 3),
            'speed': round(self.speed, 2),
            'iv': self.iv,
            'output_file': self.output_filename,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_detailed_report(self):
        """Batafsil hisobot"""
        summary = self.get_summary()
        
        report = f"""
=== SHIFRLASH NATIJALARI ===
Algoritm: {summary['algorithm']}
Fayl: {summary['filename']}
Asl hajm: {self.file_size:,} bayt ({summary['file_size_formatted']})

--- VAQT TAFSILOTLARI ---
Faylni o'qish: {summary['read_time']} s
Kalit tayyorlash: {summary['key_prep_time']} s
Shifrlash: {summary['encrypt_time']} s
Faylni yozish: {summary['write_time']} s
─────────────────────────
Umumiy vaqt: {summary['total_time']} s
Tezlik: {summary['speed']} MB/s
"""
        if summary['iv']:
            report += f"IV (hex): {summary['iv']}\n"
        
        report += f"Natija: {summary['output_file']}\n"
        report += f"Sana: {summary['timestamp']}\n"
        
        return report
    
    def export_to_csv(self):
        """CSV formatida qaytarish"""
        summary = self.get_summary()
        return {
            'Sana': summary['timestamp'].split()[0],
            'Vaqt': summary['timestamp'].split()[1],
            'Algoritm': summary['algorithm'],
            'Fayl': summary['filename'],
            'Hajm(MB)': round(self.file_size / (1024 * 1024), 2),
            'O\'qish(s)': summary['read_time'],
            'Shifrlash(s)': summary['encrypt_time'],
            'Yozish(s)': summary['write_time'],
            'Umumiy(s)': summary['total_time'],
            'Tezlik(MB/s)': summary['speed']
        }

class Timer:
    """Vaqtni o'lchash uchun yordamchi klass"""
    def __init__(self):
        self.start = None
        self.elapsed = 0
    
    def __enter__(self):
        self.start = time.time()
        return self
    
    def __exit__(self, *args):
        self.elapsed = time.time() - self.start
    
    def get_elapsed(self):
        return self.elapsed
