"""
Fayl Shifrlash Dasturi — Asosiy fayl
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import sys

from gui.symmetric_window import SymmetricWindow
#from gui.ecc_window       import ECCWindow
from gui.asymmetric_window import AsymmetricWindow
from gui.components       import COLORS, F_BODY, F_SMALL
from utils.key_manager    import KeyManager

ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('blue')


class CryptoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('🔐  Fayl Shifrlash Dasturi')
        self.geometry('860x900')
        self.minsize(720, 600)
        self.configure(fg_color=COLORS['bg_dark'])

        self.key_manager = KeyManager()
        self._build_ui()
        self._bind_shortcuts()
        self.protocol('WM_DELETE_WINDOW', self._on_close)

    def _build_ui(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color=COLORS['bg_card'], corner_radius=0, height=60)
        hdr.pack(fill='x')
        hdr.pack_propagate(False)

        ctk.CTkLabel(
            hdr, text='🔐  FAYL SHIFRLASH DASTURI',
            font=('Helvetica', 20, 'bold'),
            text_color=COLORS['text_primary']
        ).pack(side='left', padx=24)

        btn_hdr = ctk.CTkFrame(hdr, fg_color='transparent')
        btn_hdr.pack(side='right', padx=16)

        for txt, cmd in [('❓ Yordam', self._show_help), ('ℹ Haqida', self._show_about)]:
            ctk.CTkButton(
                btn_hdr, text=txt, width=130, height=40,
                fg_color='transparent', hover_color=COLORS['bg_input'],
                border_width=1, border_color=COLORS['border'],
                text_color=COLORS['text_sec'],
                font=('Helvetica', 14), corner_radius=8,
                command=cmd
            ).pack(side='left', padx=4)

        # Tabs
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=COLORS['bg_dark'],
            segmented_button_fg_color=COLORS['bg_card'],
            segmented_button_selected_color=COLORS['accent'],
            segmented_button_selected_hover_color=COLORS['accent_hover'],
            segmented_button_unselected_color=COLORS['bg_card'],
            segmented_button_unselected_hover_color=COLORS['bg_input'],
            text_color=COLORS['text_primary'],
            corner_radius=0,
        )
        self.tabview.pack(fill='both', expand=True)

        TAB1 = "🔒  Simmetrik  (AES · DES · GOST · O'z DSt)"
        #TAB2 = '🔐  ECC  (Elliptic Curve)'
        TAB3 = '🔑  Assimmetrik  (ECC · RSA · ElGamal)'
        self.tabview.add(TAB1)
        #self.tabview.add(TAB2)
        self.tabview.add(TAB3)

        SymmetricWindow(self.tabview.tab(TAB1), self.key_manager).pack(fill='both', expand=True)
        #ECCWindow(self.tabview.tab(TAB2), self.key_manager).pack(fill='both', expand=True)
        AsymmetricWindow(self.tabview.tab(TAB3)).pack(fill='both', expand=True)

        # Status bar
        sb = ctk.CTkFrame(self, fg_color=COLORS['bg_card'], corner_radius=0, height=28)
        sb.pack(fill='x', side='bottom')
        sb.pack_propagate(False)

        ctk.CTkLabel(sb, text='Ctrl+Q: Chiqish  •  Ctrl+H: Yordam',
                     font=('Helvetica', 13), text_color=COLORS['text_dim']).pack(side='left', padx=16)
        ctk.CTkLabel(sb, text='Kalitlar ~/.crypto_app/ da saqlanadi',
                     font=('Helvetica', 13), text_color=COLORS['text_dim']).pack(side='right', padx=16)

    def _bind_shortcuts(self):
        self.bind('<Control-q>', lambda _: self._on_close())
        self.bind('<Control-h>', lambda _: self._show_help())

    def _on_close(self):
        if messagebox.askokcancel('Chiqish', 'Dasturdan chiqishni xohlaysizmi?'):
            self.destroy()

    def _show_about(self):
        w = ctk.CTkToplevel(self)
        w.title('Haqida'); w.geometry('400x300')
        w.configure(fg_color=COLORS['bg_card']); w.grab_set()

        ctk.CTkLabel(w, text='🔐  Fayl Shifrlash Dasturi',
                     font=('Helvetica', 17, 'bold'), text_color=COLORS['text_primary']).pack(pady=(22, 4))
        ctk.CTkFrame(w, height=1, fg_color=COLORS['border']).pack(fill='x', padx=24, pady=14)

        for label, val in [
            ('Algoritmlar', "AES-256 · DES · GOST · O'z DSt 1105 · ECC · RSA · ElGamal · DSA"),
            ('GUI', 'CustomTkinter'),
            ('Kriptografiya', 'PyCryptodome, Cryptography'),
        ]:
            row = ctk.CTkFrame(w, fg_color='transparent')
            row.pack(fill='x', padx=30, pady=4)
            ctk.CTkLabel(row, text=f'{label}:', font=('Helvetica', 13),
                         text_color=COLORS['text_dim'], width=120, anchor='w').pack(side='left')
            ctk.CTkLabel(row, text=val, font=('Helvetica', 13),
                         text_color=COLORS['text_primary'], anchor='w').pack(side='left')

        ctk.CTkButton(w, text='Yopish', width=120,
                      fg_color=COLORS['accent'], hover_color=COLORS['accent_hover'],
                      command=w.destroy).pack(pady=20)

    def _show_help(self):
        w = ctk.CTkToplevel(self)
        w.title('Yordam'); w.geometry('540x500')
        w.configure(fg_color=COLORS['bg_card']); w.grab_set()

        ctk.CTkLabel(w, text="📖  Foydalanish Qo'llanmasi",
                     font=('Helvetica', 16, 'bold'), text_color=COLORS['text_primary']).pack(pady=(18, 10))

        tb = ctk.CTkTextbox(w, fg_color=COLORS['bg_input'], text_color=COLORS['text_sec'],
                            font=('Helvetica', 13), corner_radius=8,
                            border_width=1, border_color=COLORS['border'])
        tb.pack(fill='both', expand=True, padx=16, pady=(0, 10))
        tb.insert('1.0', """
SIMMETRIK SHIFRLASH  (AES · DES · GOST · O'Z DST 1105)
─────────────────────────────────────────
1. Algoritmni radio tugma bilan tanlang (vertikal ro'yxat)
2. "Barcha fayllar" orqali istalgan turdagi faylni tanlang (video, audio, rasm, PDF va boshqalar; 500 MB gacha)
3. Kalit kiriting yoki "⚡ Yangi" tugmasini bosing
   • "💾 Kalitni papkaga saqlash" orqali kalitni alohida faylga eksport qiling
4. Natija papkasini tanlang:
   • "📁 Papka" — qo'lda papka tanlang
   • Bo'sh qoldirsangiz — manba fayl papkasiga saqlanadi
   • Fayl nomi avtomatik hosil qilinadi  (fayl.enc)
5. "Shifrlash" yoki "Deshifrlash" tugmasini bosing

SAQLANGAN KALITLAR
─────────────────────────────────────────
• Shifrlash tugagach kalit avtomatik saqlanadi
• "Saqlangan kalitlar" ro'yxatidan oldingi kalitni yuklang
• Har algoritm uchun oxirgi 10 ta kalit saqlanadi

ECC SHIFRLASH
─────────────────────────────────────────
1. "⚡ Yangi kalit juftligi yaratish" tugmasini bosing
2. Faylni tanlang
3. Shifrlash → Public key bilan
4. Deshifrlash → Private key bilan
5. "💾 Kalitlarni papkaga saqlash" orqali saqlang

RSA / ELGAMAL / ECC SHIFRLASH
─────────────────────────────────────────
1. RSA, ElGamal yoki ECC algoritmini tanlang
2. Kalit juftligini yarating yoki PEM kalitlarini yuklang
3. Shifrlashda public key, deshifrlashda private key ishlatiladi
4. Katta fayllar AES-256-GCM bilan gibrid tarzda himoyalanadi
5. ECC rejimi ECIES, ECDH va P-256 egri chizig‘idan foydalanadi

DSA ELEKTRON IMZOSI
─────────────────────────────────────────
1. DSA algoritmini tanlang va kalit juftligini yarating
2. "Imzo yaratish" private key bilan .sig fayl hosil qiladi
3. "Imzoni tekshirish" public key va .sig fayl bilan tekshiradi
4. DSA shifrlash algoritmi emas; u fayl yaxlitligini tasdiqlaydi

KALIT FORMATLARI
─────────────────────────────────────────
  AES-256 : 64 hex belgi  (256 bit)
  DES     : 16 hex belgi  ( 64 bit)
  GOST    : 64 hex belgi  (256 bit)
    O'z DSt : 128 hex belgi (512 bit, k || kf)
  ECC     : PEM format (avtomatik)

KLAVIATURA
─────────────────────────────────────────
  Ctrl+Q  →  Dasturdan chiqish
  Ctrl+H  →  Ushbu yordam oynasi
""")
        tb.configure(state='disabled')
        ctk.CTkButton(w, text='Yopish', width=120,
                      fg_color=COLORS['accent'], hover_color=COLORS['accent_hover'],
                      command=w.destroy).pack(pady=(0, 14))


def main():
    try:
        CryptoApp().mainloop()
    except Exception as e:
        messagebox.showerror('Kritik xatolik', f'Dastur ishga tushmadi:\n{e}')
        sys.exit(1)


if __name__ == '__main__':
    main()