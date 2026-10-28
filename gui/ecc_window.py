"""
ECC shifrlash oynasi - Elliptic Curve Cryptography
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
import tkinter as tk
import threading

from gui.components import (
    FileSelector, ProgressPanel, OutputSelector, StyledButton
)
from crypto.ecc_handler import ECCHandler
from utils.validator import Validator
from utils.file_manager import FileManager
from utils.metrics import PerformanceMetrics, Timer
from utils.key_manager import KeyManager


class ECCWindow(ctk.CTkScrollableFrame):
    """ECC shifrlash oynasi"""
    
    def __init__(self, master, key_manager, **kwargs):
        super().__init__(master, **kwargs)
        
        self.key_manager = key_manager
        self.validator = Validator()
        self.file_manager = FileManager()
        self.ecc_handler = ECCHandler()
        self.metrics = None
        
        self.public_key_pem = None
        self.private_key_pem = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """UI yaratish"""
        # Markaziy container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Sarlavha
        title = ctk.CTkLabel(
            container,
            text="ELLIPTIK EGRI CHIZIQLAR (ECC)",
            font=("Arial", 18, "bold"),
            text_color="#2C3E50"
        )
        title.pack(pady=20)
        
        # Egri chiziq ma'lumoti
        info_frame = ctk.CTkFrame(container)
        info_frame.pack(pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text="Egri chiziq: secp256r1 (P-256, NIST standarti)",
            font=("Arial", 11),
            text_color="#3498DB"
        ).pack(pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text="Protokol: ECIES (Elliptic Curve Integrated Encryption Scheme)",
            font=("Arial", 10),
            text_color="gray"
        ).pack(pady=(0, 10))
        
        # Fayl tanlash
        file_frame = ctk.CTkFrame(container)
        file_frame.pack(pady=10)
        
        self.file_selector = FileSelector(
            file_frame,
            label_text="Fayl tanlash:",
            file_filter=self.validator.format_file_filter()
        )
        self.file_selector.pack(padx=20, pady=10)
        
        # Public Key
        public_key_frame = ctk.CTkFrame(container)
        public_key_frame.pack(pady=10)
        
        ctk.CTkLabel(
            public_key_frame,
            text="Ochiq kalit (Public Key):",
            font=("Arial", 12)
        ).pack(pady=5, padx=10)
        
        key_input_frame = ctk.CTkFrame(public_key_frame, fg_color="transparent")
        key_input_frame.pack(pady=5)
        
        self.public_key_entry = ctk.CTkEntry(
            key_input_frame,
            width=350,
            state="readonly",
            font=("Courier", 9)
        )
        self.public_key_entry.pack(side="left", padx=5)
        
        StyledButton(
            key_input_frame,
            text="Yuklash",
            width=100,
            command=self.load_public_key
        ).pack(side="left", padx=5)
        
        # Private Key
        private_key_frame = ctk.CTkFrame(container)
        private_key_frame.pack(pady=10)
        
        ctk.CTkLabel(
            private_key_frame,
            text="Maxfiy kalit (Private Key):",
            font=("Arial", 12)
        ).pack(pady=5, padx=10)
        
        priv_input_frame = ctk.CTkFrame(private_key_frame, fg_color="transparent")
        priv_input_frame.pack(pady=5)
        
        self.private_key_entry = ctk.CTkEntry(
            priv_input_frame,
            width=350,
            state="readonly",
            font=("Courier", 9)
        )
        self.private_key_entry.pack(side="left", padx=5)
        
        StyledButton(
            priv_input_frame,
            text="Yuklash",
            width=100,
            command=self.load_private_key
        ).pack(side="left", padx=5)
        
        # Kalit generatsiya tugmasi
        StyledButton(
            container,
            text="🔑 Kalit juftligini yaratish",
            width=250,
            fg_color="#9B59B6",
            hover_color="#8E44AD",
            command=self.generate_keypair
        ).pack(pady=10)
        
        # Oldingi kalitlar
        saved_keys_frame = ctk.CTkFrame(container)
        saved_keys_frame.pack(pady=10)
        
        ctk.CTkLabel(
            saved_keys_frame,
            text="Oldingi kalit juftliklari:",
            font=("Arial", 11)
        ).pack(anchor="center", padx=10, pady=5)
        
        self.saved_keys_combo = ctk.CTkComboBox(
            saved_keys_frame,
            values=["Kalit yo'q"],
            width=300,
            command=self.load_saved_keypair
        )
        self.saved_keys_combo.pack(padx=10, pady=5)
        
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
    
    def generate_keypair(self):
        """ECC kalit juftligini yaratish"""
        try:
            with Timer() as t:
                private_pem, public_pem = self.ecc_handler.generate_keypair()
            
            self.private_key_pem = private_pem
            self.public_key_pem = public_pem
            
            # Entry'larga qisqa versiya ko'rsatish
            self.public_key_entry.configure(state="normal")
            self.public_key_entry.delete(0, tk.END)
            self.public_key_entry.insert(0, f"[{len(public_pem)} bayt]")
            self.public_key_entry.configure(state="readonly")
            
            self.private_key_entry.configure(state="normal")
            self.private_key_entry.delete(0, tk.END)
            self.private_key_entry.insert(0, f"[{len(private_pem)} bayt]")
            self.private_key_entry.configure(state="readonly")
            
            # Saqlash taklifi
            result = messagebox.askyesno(
                "Kalit juftligi yaratildi",
                f"Kalit juftligi yaratildi ({t.get_elapsed():.3f} s)\n\n"
                "Kalitlarni faylga saqlaysizmi?"
            )
            
            if result:
                self.save_keypair_to_files()
                # Kalit juftligini key manager'ga saqlash
                self.key_manager.add_ecc_keypair(
                    public_pem,
                    private_pem,
                    label=f"ECC kalit {self.get_timestamp()}"
                )
                self.update_saved_keys()
            
        except Exception as e:
            messagebox.showerror("Xato", f"Kalit yaratishda xato: {str(e)}")
    
    def save_keypair_to_files(self):
        """Kalit juftligini faylga saqlash"""
        try:
            # Public key saqlash
            pub_file = filedialog.asksaveasfilename(
                title="Public Key saqlash",
                defaultextension=".pem",
                filetypes=[("PEM fayllar", "*.pem"), ("Barcha fayllar", "*.*")]
            )
            
            if pub_file:
                with open(pub_file, 'w') as f:
                    f.write(self.public_key_pem)
            
            # Private key saqlash
            priv_file = filedialog.asksaveasfilename(
                title="Private Key saqlash",
                defaultextension=".pem",
                filetypes=[("PEM fayllar", "*.pem"), ("Barcha fayllar", "*.*")]
            )
            
            if priv_file:
                with open(priv_file, 'w') as f:
                    f.write(self.private_key_pem)
                
                messagebox.showinfo("Muvaffaqiyat", "Kalitlar saqlandi!")
        
        except Exception as e:
            messagebox.showerror("Xato", f"Saqlashda xato: {str(e)}")
    
    def load_public_key(self):
        """Public key yuklash"""
        filename = filedialog.askopenfilename(
            title="Public Key yuklash",
            filetypes=[("PEM fayllar", "*.pem"), ("Barcha fayllar", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    self.public_key_pem = f.read()
                
                self.public_key_entry.configure(state="normal")
                self.public_key_entry.delete(0, tk.END)
                self.public_key_entry.insert(0, f"[Yuklandi: {filename.split('/')[-1]}]")
                self.public_key_entry.configure(state="readonly")
                
            except Exception as e:
                messagebox.showerror("Xato", f"Yuklashda xato: {str(e)}")
    
    def load_private_key(self):
        """Private key yuklash"""
        filename = filedialog.askopenfilename(
            title="Private Key yuklash",
            filetypes=[("PEM fayllar", "*.pem"), ("Barcha fayllar", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    self.private_key_pem = f.read()
                
                self.private_key_entry.configure(state="normal")
                self.private_key_entry.delete(0, tk.END)
                self.private_key_entry.insert(0, f"[Yuklandi: {filename.split('/')[-1]}]")
                self.private_key_entry.configure(state="readonly")
                
            except Exception as e:
                messagebox.showerror("Xato", f"Yuklashda xato: {str(e)}")
    
    def update_saved_keys(self):
        """Saqlangan kalit juftliklarini yangilash"""
        saved_keys = self.key_manager.get_recent_keys('ECC', 5)
        
        if saved_keys:
            values = [f"{key['label']} ({key['date'][:10]})" for key in saved_keys]
            self.saved_keys_combo.configure(values=values)
            self.saved_keys_combo.set(values[0] if values else "Kalit yo'q")
        else:
            self.saved_keys_combo.configure(values=["Kalit yo'q"])
            self.saved_keys_combo.set("Kalit yo'q")
    
    def load_saved_keypair(self, choice):
        """Saqlangan kalit juftligini yuklash"""
        if choice == "Kalit yo'q":
            return
        
        saved_keys = self.key_manager.get_recent_keys('ECC', 5)
        
        # Index topish
        for i, key in enumerate(saved_keys):
            if f"{key['label']} ({key['date'][:10]})" == choice:
                self.public_key_pem = key['public']
                self.private_key_pem = key['private']
                
                self.public_key_entry.configure(state="normal")
                self.public_key_entry.delete(0, tk.END)
                self.public_key_entry.insert(0, f"[{len(self.public_key_pem)} bayt]")
                self.public_key_entry.configure(state="readonly")
                
                self.private_key_entry.configure(state="normal")
                self.private_key_entry.delete(0, tk.END)
                self.private_key_entry.insert(0, f"[{len(self.private_key_pem)} bayt]")
                self.private_key_entry.configure(state="readonly")
                break
    
    def encrypt_file(self):
        """Faylni shifrlash"""
        file_path = self.file_selector.get_file()
        if not file_path:
            messagebox.showwarning("Ogohlantirish", "Iltimos, faylni tanlang!")
            return
        
        is_valid, error = self.validator.validate_file(file_path)
        if not is_valid:
            messagebox.showerror("Xato", error)
            return
        
        if not self.public_key_pem:
            messagebox.showwarning("Ogohlantirish", "Iltimos, public key yuklang yoki yarating!")
            return
        
        output_path = self.output_selector.get_path()
        if not output_path:
            output_path = self.file_manager.get_output_filename(file_path, '.ecc')
            self.output_selector.set_path(output_path)
        
        threading.Thread(
            target=self._encrypt_thread,
            args=(file_path, output_path),
            daemon=True
        ).start()
    
    def _encrypt_thread(self, file_path, output_path):
        """Shifrlash thread"""
        try:
            self.metrics = PerformanceMetrics()
            self.metrics.algorithm = "ECC (ECIES)"
            self.metrics.filename = file_path.split('/')[-1]
            self.metrics.output_filename = output_path
            
            self.metrics.start_timer()
            
            # Algoritm va operatsiyalar
            self.after(0, lambda: self.progress_panel.update_info(
                "algorithm",
                "ECC (ECIES)"
            ))
            self.after(0, lambda: self.progress_panel.update_info(
                "operations",
                "1/4 - Tayyorgarlik"
            ))
            
            # Faylni o'qish
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
            
            # Shifrlash
            self.after(0, lambda: self.progress_panel.update_info(
                "operations",
                "3/4 - Hybrid shifrlash (ECC+AES)"
            ))
            
            with Timer() as t:
                encrypted_data = self.ecc_handler.encrypt(file_data, self.public_key_pem)
            self.metrics.encrypt_time = t.get_elapsed()
            
            self.after(0, lambda: self.progress_panel.update_progress(0.8))
            self.after(0, lambda: self.progress_panel.update_info(
                "encrypt_time",
                f"{self.metrics.encrypt_time:.3f} s"
            ))
            
            # Yozish
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
        
        if not self.private_key_pem:
            messagebox.showwarning("Ogohlantirish", "Iltimos, private key yuklang!")
            return
        
        output_path = self.output_selector.get_path()
        if not output_path:
            output_path = self.file_manager.get_decrypted_filename(file_path)
            self.output_selector.set_path(output_path)
        
        threading.Thread(
            target=self._decrypt_thread,
            args=(file_path, output_path),
            daemon=True
        ).start()
    
    def _decrypt_thread(self, file_path, output_path):
        """Deshifrlash thread"""
        try:
            # O'qish
            encrypted_data = self.file_manager.read_file(file_path)
            self.after(0, lambda: self.progress_panel.update_progress(0.3))
            
            # Deshifrlash
            decrypted_data = self.ecc_handler.decrypt(encrypted_data, self.private_key_pem)
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
        self.output_selector.clear()
        self.progress_panel.reset()
    
    def get_timestamp(self):
        """Timestamp olish"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
