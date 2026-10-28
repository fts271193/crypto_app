"""
Simmetrik shifrlash oynasi - AES, DES, GOST
"""
import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
import threading
import time

from gui.components import (
    FileSelector, KeyInput, ProgressPanel,
    OutputSelector, StyledButton
)
from crypto.aes_handler import AESHandler
from crypto.des_handler import DESHandler
from crypto.gost_handler import GOSTHandler
from utils.validator import Validator
from utils.file_manager import FileManager
from utils.metrics import PerformanceMetrics, Timer
from utils.key_manager import KeyManager


class SymmetricWindow(ctk.CTkScrollableFrame):
    """Simmetrik shifrlash oynasi"""
    
    def __init__(self, master, key_manager, **kwargs):
        super().__init__(master, **kwargs)
        
        self.key_manager = key_manager
        self.validator = Validator()
        self.file_manager = FileManager()
        self.metrics = None
        
        # Algoritmlar
        self.algorithms = {
            'AES-256': AESHandler,
            'DES': DESHandler,
            'GOST Kuz': GOSTHandler
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        """UI yaratish"""
        # Markaziy container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Sarlavha
        title = ctk.CTkLabel(
            container,
            text="SIMMETRIK SHIFRLASH ALGORITMLARI",
            font=("Arial", 18, "bold"),
            text_color="#2C3E50"
        )
        title.pack(pady=20)
        
        # Algoritm tanlash
        algo_frame = ctk.CTkFrame(container)
        algo_frame.pack(pady=10)
        
        algo_label = ctk.CTkLabel(
            algo_frame,
            text="Algoritmni tanlang:",
            font=("Arial", 12, "bold")
        )
        algo_label.pack(anchor="center", pady=(10, 5), padx=10)
        
        self.algo_var = tk.StringVar(value="AES-256")
        
        radio_container = ctk.CTkFrame(algo_frame, fg_color="transparent")
        radio_container.pack(pady=5)
        
        for algo in self.algorithms.keys():
            radio = ctk.CTkRadioButton(
                radio_container,
                text=algo,
                variable=self.algo_var,
                value=algo,
                font=("Arial", 11),
                command=self.on_algorithm_change
            )
            radio.pack(anchor="center", pady=2)
        
        # Fayl tanlash
        file_frame = ctk.CTkFrame(container)
        file_frame.pack(pady=10)
        
        self.file_selector = FileSelector(
            file_frame,
            label_text="Fayl tanlash:",
            file_filter=self.validator.format_file_filter()
        )
        self.file_selector.pack(padx=20, pady=10)
        
        # Kalit kiritish
        key_frame = ctk.CTkFrame(container)
        key_frame.pack(pady=10)
        
        self.key_input = KeyInput(
            key_frame,
            label_text="Shifrlash kaliti (qo'lda kiritish):",
            show_generator=True
        )
        self.key_input.pack(padx=20, pady=10)
        self.key_input.set_generate_callback(self.generate_key)
        
        # Kalit uzunligi ko'rsatish
        self.key_length_label = ctk.CTkLabel(
            container,
            text="Kalit uzunligi: 256 bit (64 hex belgi)",
            font=("Arial", 10),
            text_color="gray"
        )
        self.key_length_label.pack(pady=(0, 10))
        
        # Oldingi kalitlar
        saved_keys_frame = ctk.CTkFrame(container)
        saved_keys_frame.pack(pady=10)
        
        ctk.CTkLabel(
            saved_keys_frame,
            text="Oldingi kalitlar:",
            font=("Arial", 11)
        ).pack(anchor="center", padx=10, pady=5)
        
        keys_container = ctk.CTkFrame(saved_keys_frame, fg_color="transparent")
        keys_container.pack(padx=10, pady=5)
        
        self.saved_keys_combos = []
        for i in range(3):
            combo = ctk.CTkComboBox(
                keys_container,
                values=["Kalit yo'q"],
                width=160,
                command=lambda choice, idx=i: self.load_saved_key(choice, idx)
            )
            combo.pack(side="left", padx=5)
            self.saved_keys_combos.append(combo)
        
        self.update_saved_keys()
        
        # Chiqish yo'li
        output_frame = ctk.CTkFrame(container)
        output_frame.pack(pady=10)
        
        self.output_selector = OutputSelector(
            output_frame,
            label_text="Natija saqlanish manzili:"
        )
        self.output_selector.pack(padx=20, pady=10)
        
        # Tugmalar
        buttons_frame = ctk.CTkFrame(container, fg_color="transparent")
        buttons_frame.pack(pady=20)
        
        StyledButton(
            buttons_frame,
            text="Shifrlash",
            width=150,
            fg_color="#27AE60",
            hover_color="#229954",
            command=self.encrypt_file
        ).pack(side="left", padx=5)
        
        StyledButton(
            buttons_frame,
            text="Deshifrlash",
            width=150,
            fg_color="#3498DB",
            hover_color="#2980B9",
            command=self.decrypt_file
        ).pack(side="left", padx=5)
        
        StyledButton(
            buttons_frame,
            text="Tozalash",
            width=150,
            fg_color="#95A5A6",
            hover_color="#7F8C8D",
            command=self.clear_all
        ).pack(side="left", padx=5)
        
        # Progress panel
        progress_frame = ctk.CTkFrame(container)
        progress_frame.pack(pady=10)
        
        self.progress_panel = ProgressPanel(progress_frame)
        self.progress_panel.pack(padx=20, pady=10)
        
        # Eksport tugmasi
        StyledButton(
            container,
            text="Natijalarni eksport qilish (CSV)",
            width=250,
            fg_color="#E67E22",
            hover_color="#D35400",
            command=self.export_results
        ).pack(pady=10)
    
    def on_algorithm_change(self):
        """Algoritm o'zgarganda"""
        algo = self.algo_var.get()
        
        # Kalit uzunligi haqida ma'lumot
        if algo == "AES-256":
            self.key_length_label.configure(text="Kalit uzunligi: 256 bit (64 hex belgi)")
        elif algo == "DES":
            self.key_length_label.configure(text="Kalit uzunligi: 64 bit (16 hex belgi)")
        elif algo == "GOST Kuznechik":
            self.key_length_label.configure(text="Kalit uzunligi: 256 bit (64 hex belgi)")
        
        # Saqlangan kalitlarni yangilash
        self.update_saved_keys()
    
    def generate_key(self):
        """Tasodifiy kalit generatsiya"""
        algo = self.algo_var.get()
        handler = self.algorithms[algo]
        return handler.generate_key()
    
    def update_saved_keys(self):
        """Saqlangan kalitlarni yangilash"""
        algo = self.algo_var.get()
        algo_key = algo.split('-')[0]  # AES, DES, GOST
        
        saved_keys = self.key_manager.get_recent_keys(algo_key, 5)
        
        for combo in self.saved_keys_combos:
            if saved_keys:
                values = [f"{key['label']} ({key['date'][:10]})" for key in saved_keys]
                combo.configure(values=values)
                combo.set(values[0] if values else "Kalit yo'q")
            else:
                combo.configure(values=["Kalit yo'q"])
                combo.set("Kalit yo'q")
    
    def load_saved_key(self, choice, index):
        """Saqlangan kalitni yuklash"""
        if choice == "Kalit yo'q":
            return
        
        algo = self.algo_var.get()
        algo_key = algo.split('-')[0]
        
        saved_keys = self.key_manager.get_recent_keys(algo_key, 5)
        
        if index < len(saved_keys):
            key = saved_keys[index]['key']
            self.key_input.set_key(key)
    
    def encrypt_file(self):
        """Faylni shifrlash"""
        # Validatsiya
        file_path = self.file_selector.get_file()
        if not file_path:
            messagebox.showwarning("Ogohlantirish", "Iltimos, faylni tanlang!")
            return
        
        is_valid, error = self.validator.validate_file(file_path)
        if not is_valid:
            messagebox.showerror("Xato", error)
            return
        
        key = self.key_input.get_key()
        algo = self.algo_var.get()
        algo_key = algo.split('-')[0]
        
        is_valid, error = self.validator.validate_key(key, algo_key)
        if not is_valid:
            messagebox.showerror("Xato", error)
            return
        
        output_path = self.output_selector.get_path()
        if not output_path:
            output_path = self.file_manager.get_output_filename(file_path)
            self.output_selector.set_path(output_path)
        
        # Thread'da shifrlash
        threading.Thread(
            target=self._encrypt_thread,
            args=(file_path, key, output_path),
            daemon=True
        ).start()
    
    def _encrypt_thread(self, file_path, key, output_path):
        """Shifrlash thread funksiyasi"""
        try:
            self.metrics = PerformanceMetrics()
            self.metrics.algorithm = self.algo_var.get()
            self.metrics.filename = file_path.split('/')[-1]
            self.metrics.output_filename = output_path
            
            self.metrics.start_timer()
            
            # Algoritm va operatsiyalar haqida ma'lumot
            self.after(0, lambda: self.progress_panel.update_info(
                "algorithm",
                self.algo_var.get()
            ))
            self.after(0, lambda: self.progress_panel.update_info(
                "operations",
                "1/4 - Tayyorgarlik"
            ))
            
            # 1. Faylni o'qish (0-20%)
            self.after(0, lambda: self.progress_panel.update_info(
                "operations",
                "2/4 - Faylni o'qish"
            ))
            
            with Timer() as t:
                file_data = self.file_manager.read_file(file_path)
            self.metrics.read_time = t.get_elapsed()
            self.metrics.file_size = len(file_data)
            
            self.after(0, lambda: self.progress_panel.update_progress(0.2))
            self.after(0, lambda: self.progress_panel.update_info(
                "file_size",
                self.metrics.format_size(self.metrics.file_size)
            ))
            self.after(0, lambda: self.progress_panel.update_info(
                "read_time",
                f"{self.metrics.read_time:.3f} s"
            ))
            
            # 2. Shifrlash (20-80%)
            self.after(0, lambda: self.progress_panel.update_info(
                "operations",
                "3/4 - Shifrlash"
            ))
            
            handler = self.algorithms[self.algo_var.get()]
            
            with Timer() as t:
                encrypted_data, iv = handler.encrypt(file_data, key)
            self.metrics.encrypt_time = t.get_elapsed()
            self.metrics.iv = iv
            
            self.after(0, lambda: self.progress_panel.update_progress(0.8))
            self.after(0, lambda: self.progress_panel.update_info(
                "encrypt_time",
                f"{self.metrics.encrypt_time:.3f} s"
            ))
            
            # 3. Yozish (80-100%)
            self.after(0, lambda: self.progress_panel.update_info(
                "operations",
                "4/4 - Faylga yozish"
            ))
            
            with Timer() as t:
                self.file_manager.write_file(output_path, encrypted_data)
            self.metrics.write_time = t.get_elapsed()
            
            self.after(0, lambda: self.progress_panel.update_progress(1.0))
            self.after(0, lambda: self.progress_panel.update_info(
                "write_time",
                f"{self.metrics.write_time:.3f} s"
            ))
            
            self.metrics.stop_timer()
            
            self.after(0, lambda: self.progress_panel.update_info(
                "operations",
                "✅ Tugallandi!"
            ))
            self.after(0, lambda: self.progress_panel.update_info(
                "total_time",
                f"{self.metrics.total_time:.3f} s"
            ))
            self.after(0, lambda: self.progress_panel.update_info(
                "speed",
                f"{self.metrics.speed:.2f} MB/s"
            ))
            
            # Kalitni saqlash
            algo_key = self.algo_var.get().split('-')[0]
            # GOST Kuznechik uchun maxsus ishlov
            if 'GOST' in algo_key:
                algo_key = 'GOST'
            self.key_manager.add_key(algo_key, key)
            self.after(0, self.update_saved_keys)
            
            self.after(0, lambda: messagebox.showinfo(
                "Muvaffaqiyat",
                f"Fayl muvaffaqiyatli shifrlandi!\n\nNatija: {output_path}"
            ))
            
        except Exception as e:
            self.after(0, lambda: self.progress_panel.update_info(
                "operations",
                "❌ Xatolik!"
            ))
            self.after(0, lambda: messagebox.showerror("Xato", f"Shifrlashda xato: {str(e)}"))
    
    def decrypt_file(self):
        """Faylni deshifrlash"""
        file_path = self.file_selector.get_file()
        if not file_path:
            messagebox.showwarning("Ogohlantirish", "Iltimos, faylni tanlang!")
            return
        
        key = self.key_input.get_key()
        algo = self.algo_var.get()
        algo_key = algo.split('-')[0]
        
        is_valid, error = self.validator.validate_key(key, algo_key)
        if not is_valid:
            messagebox.showerror("Xato", error)
            return
        
        output_path = self.output_selector.get_path()
        if not output_path:
            output_path = self.file_manager.get_decrypted_filename(file_path)
            self.output_selector.set_path(output_path)
        
        threading.Thread(
            target=self._decrypt_thread,
            args=(file_path, key, output_path),
            daemon=True
        ).start()
    
    def _decrypt_thread(self, file_path, key, output_path):
        """Deshifrlash thread funksiyasi"""
        try:
            # Faylni o'qish
            encrypted_data = self.file_manager.read_file(file_path)
            self.after(0, lambda: self.progress_panel.update_progress(0.3))
            
            # Deshifrlash
            handler = self.algorithms[self.algo_var.get()]
            decrypted_data = handler.decrypt(encrypted_data, key)
            self.after(0, lambda: self.progress_panel.update_progress(0.7))
            
            # Yozish
            self.file_manager.write_file(output_path, decrypted_data)
            self.after(0, lambda: self.progress_panel.update_progress(1.0))
            
            self.after(0, lambda: messagebox.showinfo(
                "Muvaffaqiyat",
                f"Fayl muvaffaqiyatli deshifrlandi!\n\nNatija: {output_path}"
            ))
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Xato", f"Deshifrlashda xato: {str(e)}"))
    
    def clear_all(self):
        """Barcha maydonlarni tozalash"""
        self.file_selector.clear()
        self.key_input.clear()
        self.output_selector.clear()
        self.progress_panel.reset()
    
    def export_results(self):
        """Natijalarni CSV ga eksport qilish"""
        if not self.metrics:
            messagebox.showwarning("Ogohlantirish", "Hali hech qanday operatsiya bajarilmadi!")
            return
        
        try:
            import csv
            from datetime import datetime
            from pathlib import Path
            
            # Eksport katalogini yaratish
            export_dir = Path("exports/reports")
            export_dir.mkdir(parents=True, exist_ok=True)
            
            # Fayl nomi
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = export_dir / f"encryption_report_{timestamp}.csv"
            
            # CSV yozish
            data = self.metrics.export_to_csv()
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data.keys())
                writer.writeheader()
                writer.writerow(data)
            
            messagebox.showinfo("Muvaffaqiyat", f"Hisobot saqlandi:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Xato", f"Eksport qilishda xato: {str(e)}")
