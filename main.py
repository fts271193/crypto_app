"""
Fayl Shifrlash Dasturi
Kriptografik algoritmlar: AES, DES, GOST, ECC
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import sys

from gui.symmetric_window import SymmetricWindow
from gui.ecc_window import ECCWindow
from utils.key_manager import KeyManager


class CryptoApp(ctk.CTk):
    """Asosiy dastur oynasi"""
    
    def __init__(self):
        super().__init__()
        
        # Oyna sozlamalari
        self.title("Fayl Shifrlash Dasturi")
        self.geometry("900x850")
        
        # Rang palitrasi
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Key manager
        self.key_manager = KeyManager()
        
        # Notebook (tab) yaratish
        self.tabview = ctk.CTkTabview(self, width=850, height=800)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Tab'lar qo'shish
        self.tabview.add("Simmetrik Shifrlash")
        self.tabview.add("ECC Shifrlash")
        
        # Simmetrik oyna
        self.symmetric_window = SymmetricWindow(
            self.tabview.tab("Simmetrik Shifrlash"),
            self.key_manager
        )
        self.symmetric_window.pack(fill="both", expand=True)
        
        # ECC oyna
        self.ecc_window = ECCWindow(
            self.tabview.tab("ECC Shifrlash"),
            self.key_manager
        )
        self.ecc_window.pack(fill="both", expand=True)
        
        # Menu yaratish
        self.create_menu()
        
        # Klaviatura shortcut'lari
        self.bind_shortcuts()
        
        # Yopilishda
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_menu(self):
        """Menu yaratish"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # Fayl menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fayl", menu=file_menu)
        file_menu.add_command(label="Chiqish", command=self.on_closing, accelerator="Ctrl+Q")
        
        # Yordam menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Yordam", menu=help_menu)
        help_menu.add_command(label="Haqida", command=self.show_about)
        help_menu.add_command(label="Qo'llanma", command=self.show_help)
    
    def bind_shortcuts(self):
        """Klaviatura shortcut'lari"""
        self.bind("<Control-q>", lambda e: self.on_closing())
        self.bind("<Control-h>", lambda e: self.show_help())
    
    def show_about(self):
        """Haqida oynasi"""
        about_text = """
Fayl Shifrlash Dasturi
Versiya 1.0

Qo'llab-quvvatlanadigan algoritmlar:
• AES-256-CBC
• DES-CBC
• GOST Kuznechik
• ECC (ECIES)

Yaratuvchi: Claude
Sana: 2026-01-24
        """
        messagebox.showinfo("Dastur haqida", about_text)
    
    def show_help(self):
        """Yordam oynasi"""
        help_text = """
FOYDALANISH QO'LLANMASI

1. SIMMETRIK SHIFRLASH:
   - Algoritmni tanlang (AES, DES, GOST)
   - Faylni tanlang
   - Kalitni kiriting yoki yarating (🔑)
   - "Shifrlash" tugmasini bosing

2. ECC SHIFRLASH:
   - Kalit juftligini yarating
   - Faylni tanlang
   - Public key bilan shifrlang
   - Private key bilan deshifrlang

3. KLAVIATURA SHORTCUT'LARI:
   Ctrl+Q - Chiqish
   Ctrl+H - Yordam

4. KALIT FORMATLARI:
   AES: 64 hex belgi (256 bit)
   DES: 16 hex belgi (64 bit)
   GOST: 64 hex belgi (256 bit)
        """
        
        # Yordam oynasi
        help_window = ctk.CTkToplevel(self)
        help_window.title("Yordam")
        help_window.geometry("500x400")
        
        text = ctk.CTkTextbox(help_window, width=480, height=360)
        text.pack(padx=10, pady=10)
        text.insert("1.0", help_text)
        text.configure(state="disabled")
    
    def on_closing(self):
        """Dasturni yopish"""
        if messagebox.askokcancel("Chiqish", "Dasturdan chiqishni xohlaysizmi?"):
            self.destroy()


def main():
    """Asosiy funksiya"""
    try:
        app = CryptoApp()
        app.mainloop()
    except Exception as e:
        print(f"Xatolik: {e}")
        messagebox.showerror("Xato", f"Dastur ishga tushmadi:\n{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
