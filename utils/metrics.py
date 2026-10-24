"""Ishlash vaqtlarini va takroriy kriptografik o'lchovlarni qayd etish."""
import csv
import math
import time
from datetime import datetime


class PerformanceMetrics:
    SAMPLE_COUNT = 5

    def __init__(self):
        self.file_size = 0
        self.read_time = 0.0
        self.key_prep_time = 0.0
        self.encrypt_time = 0.0
        self.decrypt_time = 0.0
        self.write_time = 0.0
        self.total_time = 0.0
        self.speed = 0.0
        self.operation_std = 0.0
        self.sample_count = 0
        self.operation_time = 0.0
        self.algorithm = ''
        self.filename = ''
        self.output_filename = ''
        self.iv = ''
        self.start_time = None
        self.end_time = None

    def start_timer(self):
        self.start_time = time.perf_counter()

    def stop_timer(self):
        if self.start_time is None:
            raise RuntimeError('Umumiy taymer ishga tushirilmagan.')
        self.end_time = time.perf_counter()
        self.total_time = self.end_time - self.start_time

    def record_operation_times(self, durations, operation):
        if not durations or any(duration < 0 for duration in durations):
            raise ValueError('O‘lchov vaqtlari bo‘sh yoki manfiy bo‘lmasligi kerak.')
        mean = sum(durations) / len(durations)
        variance = sum((duration - mean) ** 2 for duration in durations) / len(durations)
        self.operation_time = mean
        self.operation_std = math.sqrt(variance)
        self.sample_count = len(durations)
        if operation == 'encrypt':
            self.encrypt_time = mean
        elif operation == 'decrypt':
            self.decrypt_time = mean
        else:
            raise ValueError(f'Noma’lum kriptografik amal: {operation}')
        self.calculate_speed()

    def calculate_speed(self):
        self.speed = (
            self.file_size / self.operation_time / (1024 * 1024)
            if self.operation_time > 0 else 0.0
        )

    @staticmethod
    def format_size(size_bytes):
        size = float(size_bytes)
        for unit in ('B', 'KB', 'MB', 'GB'):
            if size < 1024.0:
                return f'{size:.2f} {unit}'
            size /= 1024.0
        return f'{size:.2f} TB'

    def get_summary(self):
        return {
            'algorithm': self.algorithm,
            'filename': self.filename,
            'file_size': self.file_size,
            'file_size_formatted': self.format_size(self.file_size),
            'read_time': self.read_time,
            'key_prep_time': self.key_prep_time,
            'encrypt_time': self.encrypt_time,
            'decrypt_time': self.decrypt_time,
            'operation_std': self.operation_std,
            'sample_count': self.sample_count,
            'write_time': self.write_time,
            'total_time': self.total_time,
            'speed': self.speed,
            'iv': self.iv,
            'output_file': self.output_filename,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

    def get_detailed_report(self):
        summary = self.get_summary()
        operation_label = 'Shifrlash' if self.encrypt_time else 'Deshifrlash'
        operation_time = self.encrypt_time or self.decrypt_time
        return (
            '\n=== KRIPTOGRAFIK O‘LCHOVLAR ===\n'
            f'Algoritm: {summary["algorithm"]}\n'
            f'Fayl: {summary["filename"]}\n'
            f'Asl hajm: {self.file_size:,} bayt ({summary["file_size_formatted"]})\n'
            f'Faylni o‘qish: {self.read_time:.6f} s\n'
            f'Kalitni tayyorlash: {self.key_prep_time:.6f} s\n'
            f'{operation_label}: {operation_time:.6f} s '
            f'(o‘rtacha {self.sample_count} takror, og‘ish {self.operation_std:.6f} s)\n'
            f'Faylni yozish: {self.write_time:.6f} s\n'
            f'Umumiy vaqt (disk bilan): {self.total_time:.6f} s\n'
            f'Kripto amali tezligi: {self.speed:.2f} MB/s\n'
            f'Natija: {self.output_filename}\n'
            f'Sana: {summary["timestamp"]}\n'
        )

    def export_to_csv(self, path):
        summary = self.get_summary()
        row = {
            'Sana': summary['timestamp'].split()[0],
            'Vaqt': summary['timestamp'].split()[1],
            'Algoritm': summary['algorithm'],
            'Fayl': summary['filename'],
            'Hajm(MB)': self.file_size / (1024 * 1024),
            'Kalit tayyorlash(s)': self.key_prep_time,
            'Shifrlash(s)': self.encrypt_time,
            'Deshifrlash(s)': self.decrypt_time,
            'Takrorlar': self.sample_count,
            'Standart og‘ish(s)': self.operation_std,
            'Yozish(s)': self.write_time,
            'Umumiy(s)': self.total_time,
            'Kripto tezligi(MB/s)': self.speed,
        }
        with open(path, 'w', newline='', encoding='utf-8-sig') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=row.keys())
            writer.writeheader()
            writer.writerow(row)


class Timer:
    def __init__(self):
        self.start = None
        self.elapsed = 0.0

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.elapsed = time.perf_counter() - self.start

    def get_elapsed(self):
        return self.elapsed
