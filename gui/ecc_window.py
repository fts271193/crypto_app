"""
ECC shifrlash oynasi — papka tanlash, katta shrift
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
import tkinter as tk
import threading
import os

from gui.components import (
    GlassCard, SectionHeader,
    FileSelector, OutputSelector,
    ProgressPanel, SuccessButton, DangerButton,
    GhostButton, PrimaryButton, ModernEntry, COLORS,
    F_TITLE, F_LABEL, F_BODY, F_SMALL, F_MONO
)
from crypto.ecc_handler  import ECCHandler
from utils.validator     import Validator
from utils.file_manager  import FileManager
from utils.metrics       import PerformanceMetrics, Timer
from utils.key_manager   import KeyManager


class ECCWindow(ctk.CTkScrollableFrame):
    def __init__(self, master, key_manager: KeyManager, **kwargs):
        kwargs.setdefault('fg_color', COLORS['bg_dark'])
        super().__init__(master, **kwargs)

        self.key_manager  = key_manager
        self.validator    = Validator()
        self.file_manager = FileManager()
        self.ecc_handler  = ECCHandler()
        self.metrics      = None

        self._pub_pem  = None
        self._priv_pem = None

        self._build_ui()

    # ─────────────────────────────────────────────────────────────
    def _build_ui(self):
        wrap = ctk.CTkFrame(self, fg_color='transparent')
        wrap.pack(fill='both', expand=True, padx=28, pady=22)

        # Sarlavha
        ctk.CTkLabel(
            wrap, text='🔐  ECC Shifrlash  (ECIES)',
            font=F_TITLE, text_color=COLORS['text_primary']
        ).pack(anchor='w', pady=(0, 18))

        # Info banner
        info_card = GlassCard(wrap)
        info_card.pack(fill='x', pady=(0, 14))
        inner = ctk.CTkFrame(info_card, fg_color='transparent')
        inner.pack(fill='x', padx=18, pady=12)
        ctk.CTkLabel(inner, text='📐  Egri chiziq: secp256r1  (P-256, NIST)',
                     font=F_BODY, text_color=COLORS['accent'], anchor='w').pack(fill='x', pady=2)
        ctk.CTkLabel(inner, text='🔗  Protokol: ECIES  •  Hybrid: ECC + AES-256-GCM',
                     font=F_BODY, text_color=COLORS['text_sec'], anchor='w').pack(fill='x', pady=2)

        # ── Kalit boshqaruvi ──────────────────────────
        key_card = GlassCard(wrap)
        key_card.pack(fill='x', pady=(0, 14))

        SectionHeader(key_card, text='Kalit boshqaruvi', icon='🗝️').pack(
            fill='x', padx=18, pady=(16, 12)
        )

        # Saqlangan juftliklar (1 ComboBox)
        '''sr = ctk.CTkFrame(key_card, fg_color='transparent')
        sr.pack(fill='x', padx=18, pady=(0, 10))
        sr.columnconfigure(1, weight=1)

        ctk.CTkLabel(sr, text='Saqlangan juftliklar:', font=F_BODY,
                     text_color=COLORS['text_sec'], width=180, anchor='w').grid(row=0, column=0, padx=(0, 10))

        self.saved_combo = ctk.CTkComboBox(
            sr,
            values=["— yo'q —"],
            fg_color=COLORS['bg_input'],
            border_color=COLORS['border'], border_width=1,
            button_color=COLORS['accent'],
            button_hover_color=COLORS['accent_hover'],
            dropdown_fg_color=COLORS['bg_card'],
            dropdown_hover_color=COLORS['bg_input'],
            text_color=COLORS['text_primary'],
            font=('Courier', 12),
            corner_radius=8, height=42,
            command=self._load_saved
        )
        self.saved_combo.grid(row=0, column=1, sticky='ew')
        self._ecc_keys_list = []
        self._refresh_saved()'''

        # Generatsiya
        PrimaryButton(
            key_card, text='⚡  Yangi kalit juftligi yaratish',
            height=44, width=300, command=self._generate
        ).pack(pady=(6, 14))

        # Public key
        SectionHeader(key_card, text='Public Key  (shifrlash uchun)', icon='🔓').pack(
            fill='x', padx=18, pady=(4, 10)
        )
        pub_row = ctk.CTkFrame(key_card, fg_color='transparent')
        pub_row.pack(fill='x', padx=18, pady=(0, 10))
        pub_row.columnconfigure(0, weight=1)
        self.pub_entry = ModernEntry(pub_row, state='readonly', placeholder_text='Public key yuklanmagan')
        self.pub_entry.grid(row=0, column=0, sticky='ew', padx=(0, 10))
        GhostButton(pub_row, text='📂 Yuklash', width=130, command=self._load_pub).grid(row=0, column=1)

        # Private key
        SectionHeader(key_card, text='Private Key  (deshifrlash uchun)', icon='🔒').pack(
            fill='x', padx=18, pady=(4, 10)
        )
        priv_row = ctk.CTkFrame(key_card, fg_color='transparent')
        priv_row.pack(fill='x', padx=18, pady=(0, 10))
        priv_row.columnconfigure(0, weight=1)
        self.priv_entry = ModernEntry(priv_row, state='readonly',
                                      placeholder_text='Private key yuklanmagan', show='•')
        self.priv_entry.grid(row=0, column=0, sticky='ew', padx=(0, 10))
        GhostButton(priv_row, text='📂 Yuklash', width=130, command=self._load_priv).grid(row=0, column=1)

        GhostButton(
            key_card, text='💾  Kalitlarni papkaga saqlash',
            height=40, command=self._save_keys
        ).pack(pady=(4, 16))

        # ── Fayl tanlash ──────────────────────────────
        file_card = GlassCard(wrap)
        file_card.pack(fill='x', pady=(0, 14))
        self.file_selector = FileSelector(
            file_card, label_text='Kirish fayli',
            file_filter=self.validator.format_file_filter()
        )
        self.file_selector.pack(fill='x', padx=18, pady=16)

        # ── Natija papkasi ────────────────────────────
        out_card = GlassCard(wrap)
        out_card.pack(fill='x', pady=(0, 14))
        self.output_selector = OutputSelector(
            out_card, label_text='Natija saqlanish papkasi'
        )
        self.output_selector.pack(fill='x', padx=18, pady=16)

        # ── Tugmalar ──────────────────────────────────
        btn_row = ctk.CTkFrame(wrap, fg_color='transparent')
        btn_row.pack(fill='x', pady=(4, 0))
        btn_row.columnconfigure((0, 1, 2), weight=1)

        SuccessButton(btn_row, text='⬆  Shifrlash', command=self.encrypt_file
                      ).grid(row=0, column=0, sticky='ew', padx=(0, 8))
        DangerButton(btn_row, text='⬇  Deshifrlash', command=self.decrypt_file
                     ).grid(row=0, column=1, sticky='ew', padx=8)
        GhostButton(btn_row, text='↺  Tozalash', command=self.clear_all
                    ).grid(row=0, column=2, sticky='ew', padx=(8, 0))

        # Progress
        self.progress_panel = ProgressPanel(wrap)
        self.progress_panel.pack(fill='x', pady=(18, 0))

    # ─────────────────────────────────────────────────────────────
    # Kalit boshqaruvi
    # ─────────────────────────────────────────────────────────────
    def _refresh_saved(self):
        keys = self.key_manager.get_recent_keys('ECC', 10)
        self._ecc_keys_list = keys
        self._saved_key_choices = {}
        values = []
        for index, item in enumerate(keys, start=1):
            suffix = item.get('id', f'#{index}')[:8]
            choice = (
                f"{item.get('label', 'ECC kalit')} "
                f"({item.get('date', 'sana yo‘q')}) [{suffix}] #{index}"
            )
            self._saved_key_choices[choice] = item
            values.append(choice)
        if not values:
            values = ["— yo'q —"]
        self.saved_combo.configure(values=values)
        self.saved_combo.set(values[0])

    def _load_saved(self, choice):
        item = self._saved_key_choices.get(choice)
        if item:
            self._pub_pem = item.get('public')
            self._priv_pem = item.get('private')
            self._set(self.pub_entry, f"[{len(self._pub_pem)} bayt]" if self._pub_pem else '')
            self._set(self.priv_entry, f"[{len(self._priv_pem)} bayt]" if self._priv_pem else '')

    def _generate(self):
        try:
            priv, pub = self.ecc_handler.generate_keypair()
            self._pub_pem, self._priv_pem = pub, priv
            self._set(self.pub_entry,  f'[{len(pub)} bayt]')
            self._set(self.priv_entry, f'[{len(priv)} bayt]')
            #self.key_manager.add_ecc_keypair(pub, priv, label='ECC kalit juftligi')
            #self._refresh_saved()
            messagebox.showinfo('Muvaffaqiyat', 'Kalit juftligi yaratildi va saqlandi!')
        except Exception as e:
            messagebox.showerror('Xato', str(e))

    def _load_pub(self):
        p = filedialog.askopenfilename(title='Public key', filetypes=[('PEM', '*.pem'), ('Barcha', '*.*')])
        if p:
            try:
                with open(p) as f: self._pub_pem = f.read()
                self._set(self.pub_entry, f'[Yuklandi: {os.path.basename(p)}]')
            except Exception as e: messagebox.showerror('Xato', str(e))

    def _load_priv(self):
        p = filedialog.askopenfilename(title='Private key', filetypes=[('PEM', '*.pem'), ('Barcha', '*.*')])
        if p:
            try:
                with open(p) as f: self._priv_pem = f.read()
                self._set(self.priv_entry, f'[Yuklandi: {os.path.basename(p)}]')
            except Exception as e: messagebox.showerror('Xato', str(e))

    def _save_keys(self):
        if not self._pub_pem and not self._priv_pem:
            messagebox.showwarning('Ogohlantirish', 'Avval kalit juftligini yarating!'); return
        folder = filedialog.askdirectory(title='Kalitlarni saqlash papkasi')
        if folder:
            try:
                if self._pub_pem:
                    with open(os.path.join(folder, 'public.pem'),  'w') as f: f.write(self._pub_pem)
                if self._priv_pem:
                    with open(os.path.join(folder, 'private.pem'), 'w') as f: f.write(self._priv_pem)
                messagebox.showinfo('Saqlandi', f'Kalitlar saqlandi:\n{folder}')
            except Exception as e: messagebox.showerror('Xato', str(e))

    # ─────────────────────────────────────────────────────────────
    # Shifrlash / Deshifrlash
    # ─────────────────────────────────────────────────────────────
    def encrypt_file(self):
        fp = self.file_selector.get_file()
        if not fp: messagebox.showwarning('Ogohlantirish', 'Faylni tanlang!'); return
        if not self._pub_pem: messagebox.showwarning('Ogohlantirish', 'Public key yuklanmagan!'); return

        ok, err = self.validator.validate_file(fp)
        if not ok: messagebox.showerror('Fayl xatosi', err); return

        src_dir  = os.path.dirname(fp)
        out_name = os.path.basename(fp) + '.ecc'
        self.output_selector.set_auto_dir(src_dir)
        self.output_selector.set_filename(out_name)
        out_path = self.output_selector.get_output_path(src_dir, out_name)
        if os.path.exists(out_path) and not messagebox.askyesno(
            'Fayl mavjud', f'{out_path}\n\nFayl ustiga yozilsinmi?'
        ):
            return

        self.progress_panel.reset()
        threading.Thread(
            target=self._enc_thread,
            args=(fp, out_path, self._pub_pem),
            daemon=True,
        ).start()

    def _enc_thread(self, fp, out_path, public_pem):
        try:
            metrics = PerformanceMetrics()
            metrics.algorithm = 'ECC (ECIES)'
            metrics.filename = os.path.basename(fp)
            metrics.output_filename = out_path
            metrics.start_timer()

            # O'qish
            self.after(0, lambda: self.progress_panel.update_progress(0.15, "📖 O'qilmoqda..."))
            self.after(0, lambda: self.progress_panel.update_info('algorithm', 'ECC (ECIES)'))
            with Timer() as timer:
                data = self.file_manager.read_file(fp)
            read_time = timer.get_elapsed()
            metrics.read_time = read_time
            file_size = len(data)
            metrics.file_size = file_size

            self.after(0, lambda: self.progress_panel.update_info('file_size', f'{file_size:,} bayt'))
            self.after(0, lambda: self.progress_panel.update_info('read_time', f'{read_time:.3f} s'))

            # Shifrlash
            self.after(0, lambda: self.progress_panel.update_progress(0.5, '🔒 ECC shifrlash...'))
            with Timer() as timer:
                ECCHandler.load_public_key(public_pem)
            metrics.key_prep_time = timer.get_elapsed()
            samples = []
            encrypted = None
            for _ in range(metrics.SAMPLE_COUNT):
                with Timer() as timer:
                    encrypted = self.ecc_handler.encrypt(data, public_pem)
                samples.append(timer.get_elapsed())
            metrics.record_operation_times(samples, 'encrypt')
            self.after(0, lambda duration=metrics.encrypt_time, deviation=metrics.operation_std:
                       self.progress_panel.update_info(
                           'encrypt_time',
                           f'{duration:.6f} ± {deviation:.6f} s (n={metrics.sample_count})',
                       ))

            # Yozish
            self.after(0, lambda: self.progress_panel.update_progress(0.85, '💾 Yozilmoqda...'))
            with Timer() as timer:
                self.file_manager.write_file(out_path, encrypted)
            write_time = timer.get_elapsed()
            metrics.write_time = write_time

            metrics.stop_timer()
            self.metrics = metrics

            self.after(0, lambda: self.progress_panel.update_info('write_time', f'{write_time:.3f} s'))
            self.after(0, lambda: self.progress_panel.update_info('total_time', f'{metrics.total_time:.3f} s'))
            self.after(0, lambda s=f'{metrics.speed:.2f} MB/s': self.progress_panel.update_info('speed', s))
            self.after(0, lambda: self.progress_panel.update_progress(1.0, '✔ Tugallandi!'))
            self.after(0, lambda: messagebox.showinfo('Muvaffaqiyat ✅', f'ECC shifrlash tugadi!\n\n📁 {out_path}'))
        except Exception as e:
            self.after(0, self.progress_panel.set_error)
            self.after(0, lambda err=e: messagebox.showerror('Xatolik ❌', str(err)))

    def decrypt_file(self):
        fp = self.file_selector.get_file()
        if not fp: messagebox.showwarning('Ogohlantirish', 'Faylni tanlang!'); return
        if not self._priv_pem: messagebox.showwarning('Ogohlantirish', 'Private key yuklanmagan!'); return

        src_dir  = os.path.dirname(fp)
        src_name = os.path.basename(fp)
        out_name = src_name[:-4] if src_name.endswith('.ecc') else src_name + '.dec'
        self.output_selector.set_auto_dir(src_dir)
        self.output_selector.set_filename(out_name)
        out_path = self.output_selector.get_output_path(src_dir, out_name)
        if os.path.abspath(out_path) == os.path.abspath(fp):
            messagebox.showerror('Yo‘l xatosi', 'Natija fayli manba fayl bilan bir xil bo‘la olmaydi.')
            return
        if os.path.exists(out_path) and not messagebox.askyesno(
            'Fayl mavjud', f'{out_path}\n\nFayl ustiga yozilsinmi?'
        ):
            return

        self.progress_panel.reset()
        threading.Thread(
            target=self._dec_thread,
            args=(fp, out_path, self._priv_pem),
            daemon=True,
        ).start()

    def _dec_thread(self, fp, out_path, private_pem):
        try:
            metrics = PerformanceMetrics()
            metrics.algorithm = 'ECC (ECIES)'
            metrics.filename = os.path.basename(fp)
            metrics.output_filename = out_path
            metrics.start_timer()

            # O'qish
            self.after(0, lambda: self.progress_panel.update_progress(0.15, "📖 O'qilmoqda..."))
            self.after(0, lambda: self.progress_panel.update_info('algorithm', 'ECC (ECIES)'))
            with Timer() as timer:
                data = self.file_manager.read_file(fp)
            read_time = timer.get_elapsed()
            metrics.read_time = read_time
            file_size = len(data)

            self.after(0, lambda: self.progress_panel.update_info('file_size', f'{file_size:,} bayt'))
            self.after(0, lambda: self.progress_panel.update_info('read_time', f'{read_time:.3f} s'))

            # Deshifrlash
            self.after(0, lambda: self.progress_panel.update_progress(0.5, '🔓 ECC deshifrlash...'))
            with Timer() as timer:
                ECCHandler.load_private_key(private_pem)
            metrics.key_prep_time = timer.get_elapsed()
            samples = []
            decrypted = None
            for _ in range(metrics.SAMPLE_COUNT):
                with Timer() as timer:
                    decrypted = self.ecc_handler.decrypt(data, private_pem)
                samples.append(timer.get_elapsed())
            metrics.file_size = len(decrypted)
            metrics.record_operation_times(samples, 'decrypt')
            self.after(0, lambda duration=metrics.decrypt_time, deviation=metrics.operation_std:
                       self.progress_panel.update_info(
                           'encrypt_time',
                           f'{duration:.6f} ± {deviation:.6f} s (n={metrics.sample_count})',
                       ))

            # Yozish
            self.after(0, lambda: self.progress_panel.update_progress(0.85, '💾 Yozilmoqda...'))
            with Timer() as timer:
                self.file_manager.write_file(out_path, decrypted)
            write_time = timer.get_elapsed()
            metrics.write_time = write_time

            metrics.stop_timer()
            self.metrics = metrics

            self.after(0, lambda: self.progress_panel.update_info('write_time', f'{write_time:.3f} s'))
            self.after(0, lambda: self.progress_panel.update_info('total_time', f'{metrics.total_time:.3f} s'))
            self.after(0, lambda s=f'{metrics.speed:.2f} MB/s': self.progress_panel.update_info('speed', s))
            self.after(0, lambda: self.progress_panel.update_progress(1.0, '✔ Tugallandi!'))
            self.after(0, lambda: messagebox.showinfo('Muvaffaqiyat ✅', f'ECC deshifrlash tugadi!\n\n📁 {out_path}'))
        except Exception as e:
            self.after(0, self.progress_panel.set_error)
            self.after(0, lambda err=e: messagebox.showerror('Xatolik ❌', str(err)))

    # ─────────────────────────────────────────────────────────────
    def clear_all(self):
        self.file_selector.clear()
        self.output_selector.full_clear()
        self.progress_panel.reset()
        self._pub_pem = self._priv_pem = None
        for e in (self.pub_entry, self.priv_entry):
            e.configure(state='normal'); e.delete(0, tk.END); e.configure(state='readonly')

    @staticmethod
    def _set(entry, text):
        entry.configure(state='normal')
        entry.delete(0, tk.END)
        entry.insert(0, text)
        entry.configure(state='readonly')