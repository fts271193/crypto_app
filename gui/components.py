"""
GUI komponentlar - qayta ishlatiladigan UI elementlari
"""
import customtkinter as ctk
from tkinter import filedialog
import tkinter as tk

class StyledButton(ctk.CTkButton):
    """Stilizatsiya qilingan tugma"""
    def __init__(self, master, **kwargs):
        # Default qiymatlar
        defaults = {
            'corner_radius': 8,
            'font': ("Arial", 12)
        }
        
        # kwargs bilan birlashtirish
        for key, value in defaults.items():
            if key not in kwargs:
                kwargs[key] = value
        
        super().__init__(master, **kwargs)

class StyledEntry(ctk.CTkEntry):
    """Stilizatsiya qilingan input maydon"""
    def __init__(self, master, **kwargs):
        # Default qiymatlar
        defaults = {
            'corner_radius': 5,
            'border_width': 2,
            'font': ("Arial", 11)
        }
        
        # kwargs bilan birlashtirish (kwargs ustunlik qiladi)
        for key, value in defaults.items():
            if key not in kwargs:
                kwargs[key] = value
        
        super().__init__(master, **kwargs)

class FileSelector(ctk.CTkFrame):
    """Fayl tanlash komponenti"""
    def __init__(self, master, label_text="Fayl tanlash:", file_filter=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.file_filter = file_filter
        self.selected_file = None
        
        # Label
        self.label = ctk.CTkLabel(self, text=label_text, font=("Arial", 12))
        self.label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Entry va Button
        self.entry = StyledEntry(self, width=400, state="readonly")
        self.entry.grid(row=1, column=0, padx=(0, 10))
        
        self.button = StyledButton(
            self,
            text="Tanlash",
            width=100,
            command=self.select_file
        )
        self.button.grid(row=1, column=1)
    
    def select_file(self):
        """Fayl tanlash dialogi"""
        filename = filedialog.askopenfilename(
            title="Faylni tanlang",
            filetypes=self.file_filter if self.file_filter else [("Barcha fayllar", "*.*")]
        )
        
        if filename:
            self.selected_file = filename
            self.entry.configure(state="normal")
            self.entry.delete(0, tk.END)
            self.entry.insert(0, filename)
            self.entry.configure(state="readonly")
    
    def get_file(self):
        """Tanlangan faylni qaytarish"""
        return self.selected_file
    
    def clear(self):
        """Tanlashni tozalash"""
        self.selected_file = None
        self.entry.configure(state="normal")
        self.entry.delete(0, tk.END)
        self.entry.configure(state="readonly")

class KeyInput(ctk.CTkFrame):
    """Kalit kiritish komponenti"""
    def __init__(self, master, label_text="Shifrlash kaliti:", show_generator=False, **kwargs):
        super().__init__(master, **kwargs)
        
        self.show_password = False
        
        # Label
        self.label = ctk.CTkLabel(self, text=label_text, font=("Arial", 12))
        self.label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Entry
        self.entry = StyledEntry(self, width=350, show="*", font=("Courier", 11))
        self.entry.grid(row=1, column=0, padx=(0, 5))
        
        # Ko'rish/yashirish tugmasi
        self.toggle_btn = StyledButton(
            self,
            text="👁",
            width=40,
            command=self.toggle_visibility
        )
        self.toggle_btn.grid(row=1, column=1, padx=(0, 5))
        
        # Generator tugmasi (ixtiyoriy)
        if show_generator:
            self.gen_btn = StyledButton(
                self,
                text="🔑",
                width=40,
                command=self.generate_key
            )
            self.gen_btn.grid(row=1, column=2)
            self.generate_callback = None
    
    def toggle_visibility(self):
        """Kalitni ko'rish/yashirish"""
        self.show_password = not self.show_password
        if self.show_password:
            self.entry.configure(show="")
        else:
            self.entry.configure(show="*")
    
    def get_key(self):
        """Kalitni olish"""
        return self.entry.get()
    
    def set_key(self, key):
        """Kalitni o'rnatish"""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, key)
    
    def clear(self):
        """Kalitni tozalash"""
        self.entry.delete(0, tk.END)
    
    def set_generate_callback(self, callback):
        """Generator callback o'rnatish"""
        self.generate_callback = callback
    
    def generate_key(self):
        """Kalit generatsiya"""
        if self.generate_callback:
            key = self.generate_callback()
            self.set_key(key)

class ProgressPanel(ctk.CTkFrame):
    """Progress va ma'lumotlar paneli"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Sarlavha
        self.title = ctk.CTkLabel(
            self,
            text="JARAYON MA'LUMOTLARI",
            font=("Arial", 14, "bold")
        )
        self.title.pack(pady=(10, 5))
        
        # Progress bar
        self.progressbar = ctk.CTkProgressBar(self, width=400)
        self.progressbar.pack(pady=10, padx=20)
        self.progressbar.set(0)
        
        # Ma'lumotlar frame
        self.info_frame = ctk.CTkFrame(self)
        self.info_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Ma'lumot labellar
        self.labels = {}
        self.create_info_labels()
    
    def create_info_labels(self):
        """Ma'lumot labellarini yaratish"""
        info_keys = [
            ("algorithm", "Algoritm:"),
            ("operations", "Operatsiyalar:"),
            ("file_size", "Fayl hajmi:"),
            ("read_time", "O'qish vaqti:"),
            ("encrypt_time", "Shifrlash vaqti:"),
            ("write_time", "Yozish vaqti:"),
            ("total_time", "Umumiy vaqt:"),
            ("speed", "Tezlik:")
        ]
        
        for i, (key, label_text) in enumerate(info_keys):
            label = ctk.CTkLabel(
                self.info_frame,
                text=f"{label_text} -",
                font=("Arial", 14),
                anchor="w"
            )
            label.grid(row=i, column=0, sticky="w", padx=10, pady=3)
            self.labels[key] = label
    
    def update_progress(self, value):
        """Progress bar yangilash (0-1)"""
        self.progressbar.set(value)
    
    def update_info(self, key, value):
        """Ma'lumotni yangilash"""
        if key in self.labels:
            current_text = self.labels[key].cget("text").split(":")[0]
            self.labels[key].configure(text=f"{current_text}: {value}")
    
    def reset(self):
        """Barcha ma'lumotlarni tozalash"""
        self.progressbar.set(0)
        for key in self.labels:
            current_text = self.labels[key].cget("text").split(":")[0]
            self.labels[key].configure(text=f"{current_text}: -")

class OutputSelector(ctk.CTkFrame):
    """Chiqish fayl tanlash komponenti"""
    def __init__(self, master, label_text="Natija saqlanish manzili:", **kwargs):
        super().__init__(master, **kwargs)
        
        self.output_path = None
        
        # Label
        self.label = ctk.CTkLabel(self, text=label_text, font=("Arial", 12))
        self.label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Entry va Button
        self.entry = StyledEntry(self, width=400, state="readonly")
        self.entry.grid(row=1, column=0, padx=(0, 10))
        
        self.button = StyledButton(
            self,
            text="Tanlash",
            width=100,
            command=self.select_output
        )
        self.button.grid(row=1, column=1)
    
    def select_output(self):
        """Chiqish faylini tanlash"""
        filename = filedialog.asksaveasfilename(
            title="Natijani saqlash",
            defaultextension=".*",
            filetypes=[("Barcha fayllar", "*.*")]
        )
        
        if filename:
            self.output_path = filename
            self.entry.configure(state="normal")
            self.entry.delete(0, tk.END)
            self.entry.insert(0, filename)
            self.entry.configure(state="readonly")
    
    def get_path(self):
        """Tanlangan yo'lni qaytarish"""
        return self.output_path
    
    def set_path(self, path):
        """Yo'lni o'rnatish"""
        self.output_path = path
        self.entry.configure(state="normal")
        self.entry.delete(0, tk.END)
        self.entry.insert(0, path)
        self.entry.configure(state="readonly")
    
    def clear(self):
        """Tanlashni tozalash"""
        self.output_path = None
        self.entry.configure(state="normal")
        self.entry.delete(0, tk.END)
        self.entry.configure(state="readonly")
