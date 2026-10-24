"""
Simmetrik shifrlash oynasi — AES, DES, GOST va O'z DSt 1105
Tuzatilgan: vertikal algoritmlar, papka tanlash output, katta shrift
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
import tkinter as tk
import threading
import os

from gui.components import (
    GlassCard, SectionHeader,
    FileSelector, KeyInput, OutputSelector,
    ProgressPanel, SuccessButton, DangerButton,
    GhostButton, PrimaryButton, COLORS,
    F_TITLE, F_LABEL, F_BODY, F_SMALL, F_MONO
)
from crypto.aes_handler  import AESHandler
from crypto.des_handler  import DESHandler
from crypto.gost_handler import GOSTHandler
from crypto.uzbek_standard_handler import UzbekStandardHandler
from utils.validator     import Validator
from utils.file_manager  import FileManager
from utils.metrics       import PerformanceMetrics, Timer
from utils.key_manager   import KeyManager


class SymmetricWindow(ctk.CTkScrollableFrame):
    """Simmetrik shifrlash oynasi"""

    # (handler_class, algo_key, kalit_hint)
    ALGORITHMS = {
        'AES-256':        (AESHandler,  'AES',  'AQSh standarti'),#'64 hex belgi  (256 bit)'
        'DES':            (DESHandler,  'DES',  'AQSh standarti(eski)'),#'16 hex belgi  (64 bit)'
        'GOST Kuznechik': (GOSTHandler, 'GOST', 'Rossiya standarti'),#'64 hex belgi  (256 bit)'
        "O'z DSt 1105:2009": (UzbekStandardHandler, 'OZ_DST_1105', 'Özbekiton standarti'),#'128 hex belgi  (k || kf, 512 bit)'
    }

    def __init__(self, master, key_manager: KeyManager, **kwargs):
        kwargs.setdefault('fg_color', COLORS['bg_dark'])
        super().__init__(master, **kwargs)

        self.key_manager  = key_manager
        self.validator    = Validator()
        self.file_manager = FileManager()
        self.metrics      = None

        self._build_ui()

    # ─────────────────────────────────────────────────────────────
    def _build_ui(self):
        wrap = ctk.CTkFrame(self, fg_color='transparent')
        wrap.pack(fill='both', expand=True, padx=28, pady=22)

        # ── Sarlavha ──────────────────────────────────
        ctk.CTkLabel(
            wrap,
            text='🔒  Simmetrik Shifrlash',
            font=F_TITLE,
            text_color=COLORS['text_primary']
        ).pack(anchor='w', pady=(0, 18))

        # ── Algoritm tanlash — VERTIKAL ──────────────
        algo_card = GlassCard(wrap)
        algo_card.pack(fill='x', pady=(0, 14))

        SectionHeader(algo_card, text='Algoritm tanlang', icon='⚙️').pack(
            fill='x', padx=18, pady=(16, 12)
        )

        self.algo_var = tk.StringVar(value='AES-256')

        # Vertikal: har bir algoritm alohida qatorda
        for name, (_, _, hint) in self.ALGORITHMS.items():
            row = ctk.CTkFrame(algo_card, fg_color='transparent')
            row.pack(fill='x', padx=18, pady=4)

            ctk.CTkRadioButton(
                row,
                text=name,
                variable=self.algo_var,
                value=name,
                font=F_BODY,
                text_color=COLORS['text_primary'],
                fg_color=COLORS['accent'],
                hover_color=COLORS['accent_hover'],
                radiobutton_width=20, radiobutton_height=20,
                command=self._on_algo_change
            ).pack(side='left')

            ctk.CTkLabel(
                row,
                text=f'— {hint}',
                font=F_SMALL,
                text_color=COLORS['text_dim']
            ).pack(side='left', padx=(14, 0))

        # Tanlangan kalit uzunligi hint
        self.algo_hint = ctk.CTkLabel(
            algo_card,
            text='',
            font=F_SMALL,
            text_color=COLORS['text_dim']
        )
        self.algo_hint.pack(pady=(4, 14))

        # ── Fayl tanlash ──────────────────────────────
        file_card = GlassCard(wrap)
        file_card.pack(fill='x', pady=(0, 14))

        self.file_selector = FileSelector(
            file_card,
            label_text='Kirish fayli',
            file_filter=self.validator.format_file_filter()
        )
        self.file_selector.pack(fill='x', padx=18, pady=16)

        # ── Kalit kiritish ────────────────────────────
        key_card = GlassCard(wrap)
        key_card.pack(fill='x', pady=(0, 14))

        self.key_input = KeyInput(
            key_card,
            label_text='Shifrlash kaliti',
            show_generator=True
        )
        self.key_input.pack(fill='x', padx=18, pady=16)
        self.key_input.set_generate_callback(self._generate_key)
        #self._refresh_saved_keys()
        GhostButton(
            key_card, text='💾  Kalitni papkaga saqlash',
            command=self._save_key_to_file
        ).pack(fill='x', padx=18, pady=(0, 16))

        # ── Natija papkasi ────────────────────────────
        out_card = GlassCard(wrap)
        out_card.pack(fill='x', pady=(0, 14))

        self.output_selector = OutputSelector(
            out_card,
            label_text='Natija saqlanish papkasi'
        )
        self.output_selector.pack(fill='x', padx=18, pady=16)

        # ── Tugmalar ──────────────────────────────────
        btn_row = ctk.CTkFrame(wrap, fg_color='transparent')
        btn_row.pack(fill='x', pady=(4, 0))
        btn_row.columnconfigure((0, 1, 2), weight=1)

        SuccessButton(
            btn_row, text='⬆  Shifrlash',
            command=self.encrypt_file
        ).grid(row=0, column=0, sticky='ew', padx=(0, 8))

        DangerButton(
            btn_row, text='⬇  Deshifrlash',
            command=self.decrypt_file
        ).grid(row=0, column=1, sticky='ew', padx=8)

        GhostButton(
            btn_row, text='↺  Tozalash',
            command=self.clear_all
        ).grid(row=0, column=2, sticky='ew', padx=(8, 0))

        # ── Progress paneli ───────────────────────────
        self.progress_panel = ProgressPanel(wrap)
        self.progress_panel.pack(fill='x', pady=(18, 0))

        # ── Eksport ───────────────────────────────────
        GhostButton(
            wrap, text='📤  Natijalarni CSV ga eksport qilish',
            command=self._export_results
        ).pack(fill='x', pady=(10, 0))

    # ─────────────────────────────────────────────────────────────
    # Yordamchi
    # ─────────────────────────────────────────────────────────────
    def _algo_info(self):
        return self.ALGORITHMS[self.algo_var.get()]

    def _on_algo_change(self):
        _, _, hint = self._algo_info()
        # Algo o'zgarsa saqlangan kalitlar yangilanadi
        #self._refresh_saved_keys()
        self.output_selector.full_clear()

    def _generate_key(self):
        handler, _, _ = self._algo_info()
        return handler.generate_key()

    def _save_key_to_file(self):
        key = self.key_input.get_key()
        if not key:
            messagebox.showwarning('Ogohlantirish', 'Avval kalitni kiriting yoki yarating.')
            return

        _, algo_key, _ = self._algo_info()
        path = filedialog.asksaveasfilename(
            title='Kalitni saqlash',
            initialfile=f'{algo_key.lower()}_key.txt',
            defaultextension='.txt',
            filetypes=[('Kalit fayllari', '*.txt'), ('Barcha fayllar', '*.*')],
        )
        if not path:
            return

        try:
            with open(path, 'w', encoding='ascii') as key_file:
                key_file.write(key)
            messagebox.showinfo(
                'Saqlandi',
                f'Kalit saqlandi:\n{path}\n\nKalit fayli himoyalanmagan. Uni xavfsiz joyda saqlang.',
            )
        except OSError as exc:
            messagebox.showerror('Xato', f'Kalitni saqlab bo‘lmadi:\n{exc}')

    def _refresh_saved_keys(self):
        _, algo_key, _ = self._algo_info()
        self._update_saved_keys(algo_key)

    def _update_saved_keys(self, algo_key):
        keys = self.key_manager.get_recent_keys(algo_key, 10)
        self.key_input.update_saved_keys(keys)

    def _build_output_path(self, input_path: str, suffix: str) -> str:
        """Natija fayl yo'lini hisoblash"""
        src_dir  = os.path.dirname(input_path)
        src_name = os.path.basename(input_path)
        out_name = src_name + suffix          # masalan: doc.txt.enc
        return self.output_selector.get_output_path(src_dir, out_name)

    # ─────────────────────────────────────────────────────────────
    # Shifrlash
    # ─────────────────────────────────────────────────────────────
    def encrypt_file(self):
        file_path = self.file_selector.get_file()
        if not file_path:
            messagebox.showwarning('Ogohlantirish', 'Iltimos, faylni tanlang!')
            return

        key = self.key_input.get_key()
        handler, algo_key, _ = self._algo_info()
        algorithm_name = self.algo_var.get()

        ok, err = self.validator.validate_file(file_path)
        if not ok:
            messagebox.showerror('Fayl xatosi', err)
            return

        ok, err = self.validator.validate_key(key, algo_key)
        if not ok:
            messagebox.showerror('Kalit xatosi', err)
            return

        # Avtomatik papkani o'rnat (manba fayl papkasi)
        src_dir = os.path.dirname(file_path)
        self.output_selector.set_auto_dir(src_dir)

        # Fayl nomini ko'rsat
        out_name = os.path.basename(file_path) + '.enc'
        self.output_selector.set_filename(out_name)

        output_path = self._build_output_path(file_path, '.enc')
        if os.path.exists(output_path) and not messagebox.askyesno(
            'Fayl mavjud', f'{output_path}\n\nFayl ustiga yozilsinmi?'
        ):
            return

        self.progress_panel.reset()
        threading.Thread(
            target=self._encrypt_thread,
            args=(file_path, key, output_path, handler, algo_key, algorithm_name),
            daemon=True
        ).start()

    def _encrypt_thread(
        self, file_path, key, output_path, handler, algo_key, algorithm_name
    ):
        try:
            metrics = PerformanceMetrics()
            metrics.algorithm = algorithm_name
            metrics.filename = os.path.basename(file_path)
            metrics.output_filename = output_path
            metrics.start_timer()

            self.after(0, lambda: self.progress_panel.update_progress(0.1, "📖 Fayl o'qilmoqda..."))
            with Timer() as t:
                data = self.file_manager.read_file(file_path)
            metrics.read_time = t.get_elapsed()
            metrics.file_size = len(data)

            self.after(0, lambda name=algorithm_name: self.progress_panel.update_info('algorithm', name))
            self.after(0, lambda: self.progress_panel.update_info('file_size',  metrics.format_size(metrics.file_size)))
            self.after(0, lambda: self.progress_panel.update_info('read_time',  f'{metrics.read_time:.3f} s'))

            self.after(0, lambda: self.progress_panel.update_progress(0.45, '🔒 Shifrlanoqda...'))
            with Timer() as t:
                handler.key_from_hex(key)
            metrics.key_prep_time = t.get_elapsed()
            encryption_times = []
            encrypted = iv = None
            for _ in range(metrics.SAMPLE_COUNT):
                with Timer() as t:
                    encrypted, iv = handler.encrypt(data, key)
                encryption_times.append(t.get_elapsed())
            metrics.file_size = len(data)
            metrics.record_operation_times(encryption_times, 'encrypt')
            metrics.iv = iv
            self.after(0, lambda: self.progress_panel.update_info(
                'encrypt_time',
                f'{metrics.encrypt_time:.6f} ± {metrics.operation_std:.6f} s '
                f'(n={metrics.sample_count})',
            ))

            self.after(0, lambda: self.progress_panel.update_progress(0.8, '💾 Yozilmoqda...'))
            with Timer() as t:
                self.file_manager.write_file(output_path, encrypted)
            metrics.write_time = t.get_elapsed()
            metrics.stop_timer()

            self.after(0, lambda: self.progress_panel.update_info('write_time',  f'{metrics.write_time:.3f} s'))
            self.after(0, lambda: self.progress_panel.update_info('total_time',  f'{metrics.total_time:.3f} s'))
            speed_str = f'{metrics.speed:.2f} MB/s' if metrics.speed > 0 else '—'
            self.after(0, lambda s=speed_str: self.progress_panel.update_info('speed', s))
            self.after(0, lambda: self.progress_panel.update_progress(1.0, '✔ Muvaffaqiyatli!'))
            self.metrics = metrics

            # Kalitni avtomatik saqlash
            #self.key_manager.add_key(algo_key, key, label=f'{algorithm_name} kalit')
            #self.after(0, lambda key=algo_key: self._update_saved_keys(key))

            self.after(0, lambda: messagebox.showinfo(
                'Muvaffaqiyat ✅',
                f'Fayl shifrlandi!\n\n📁 Natija: {output_path}'
            ))
        except Exception as e:
            self.after(0, self.progress_panel.set_error)
            self.after(0, lambda err=e: messagebox.showerror('Xatolik ❌', str(err)))

    # ─────────────────────────────────────────────────────────────
    # Deshifrlash
    # ─────────────────────────────────────────────────────────────
    def decrypt_file(self):
        file_path = self.file_selector.get_file()
        if not file_path:
            messagebox.showwarning('Ogohlantirish', 'Iltimos, faylni tanlang!')
            return

        key = self.key_input.get_key()
        handler, algo_key, _ = self._algo_info()
        algorithm_name = self.algo_var.get()

        ok, err = self.validator.validate_key(key, algo_key)
        if not ok:
            messagebox.showerror('Kalit xatosi', err)
            return

        src_dir  = os.path.dirname(file_path)
        src_name = os.path.basename(file_path)
        # .enc kengaytmasini olib tashlash, yo'q bo'lsa .dec qo'shish
        if src_name.endswith('.enc'):
            out_name = src_name[:-4]
        else:
            out_name = src_name + '.dec'

        self.output_selector.set_auto_dir(src_dir)
        self.output_selector.set_filename(out_name)
        output_path = self.output_selector.get_output_path(src_dir, out_name)
        if os.path.abspath(output_path) == os.path.abspath(file_path):
            messagebox.showerror('Yo‘l xatosi', 'Natija fayli manba fayl bilan bir xil bo‘la olmaydi.')
            return
        if os.path.exists(output_path) and not messagebox.askyesno(
            'Fayl mavjud', f'{output_path}\n\nFayl ustiga yozilsinmi?'
        ):
            return

        self.progress_panel.reset()
        threading.Thread(
            target=self._decrypt_thread,
            args=(file_path, key, output_path, handler, algo_key, algorithm_name),
            daemon=True
        ).start()

    def _decrypt_thread(
        self, file_path, key, output_path, handler, algo_key, algorithm_name
    ):
        try:
            metrics = PerformanceMetrics()
            metrics.algorithm = algorithm_name
            metrics.filename = os.path.basename(file_path)
            metrics.output_filename = output_path
            metrics.start_timer()
            self.after(0, lambda: self.progress_panel.update_progress(0.15, "📖 O'qilmoqda..."))
            self.after(0, lambda name=algorithm_name: self.progress_panel.update_info('algorithm', name))
            with Timer() as t:
                data = self.file_manager.read_file(file_path)
            metrics.read_time = t.get_elapsed()
            metrics.file_size = len(data)
            self.after(0, lambda size=metrics.file_size: self.progress_panel.update_info(
                'file_size', metrics.format_size(size)
            ))
            self.after(0, lambda duration=metrics.read_time: self.progress_panel.update_info(
                'read_time', f'{duration:.3f} s'
            ))

            self.after(0, lambda: self.progress_panel.update_progress(0.5, '🔓 Deshifrlanmoqda...'))
            with Timer() as t:
                handler.key_from_hex(key)
            metrics.key_prep_time = t.get_elapsed()
            decryption_times = []
            decrypted = None
            for _ in range(metrics.SAMPLE_COUNT):
                with Timer() as t:
                    decrypted = handler.decrypt(data, key)
                decryption_times.append(t.get_elapsed())
            metrics.file_size = len(decrypted)
            metrics.record_operation_times(decryption_times, 'decrypt')

            self.after(0, lambda: self.progress_panel.update_progress(0.85, '💾 Yozilmoqda...'))
            with Timer() as t:
                self.file_manager.write_file(output_path, decrypted)
            metrics.write_time = t.get_elapsed()
            metrics.stop_timer()
            self.metrics = metrics
            self.after(0, lambda duration=metrics.decrypt_time: self.progress_panel.update_info(
                'encrypt_time',
                f'{duration:.6f} ± {metrics.operation_std:.6f} s '
                f'(n={metrics.sample_count})',
            ))
            self.after(0, lambda duration=metrics.write_time: self.progress_panel.update_info(
                'write_time', f'{duration:.3f} s'
            ))
            self.after(0, lambda duration=metrics.total_time: self.progress_panel.update_info(
                'total_time', f'{duration:.3f} s'
            ))
            self.after(0, lambda speed=f'{metrics.speed:.2f} MB/s': self.progress_panel.update_info(
                'speed', speed
            ))

            self.after(0, lambda: self.progress_panel.update_progress(1.0, '✔ Muvaffaqiyatli!'))
            self.after(0, lambda: messagebox.showinfo(
                'Muvaffaqiyat ✅',
                f'Fayl deshifrlandi!\n\n📁 Natija: {output_path}'
            ))
        except Exception as e:
            self.after(0, self.progress_panel.set_error)
            self.after(0, lambda err=e: messagebox.showerror('Xatolik ❌', str(err)))

    # ─────────────────────────────────────────────────────────────
    def clear_all(self):
        self.file_selector.clear()
        self.key_input.clear()
        self.output_selector.full_clear()
        self.progress_panel.reset()

    def _export_results(self):
        if not self.metrics:
            messagebox.showwarning('Ogohlantirish', 'Hali operatsiya bajarilmagan!')
            return
        path = filedialog.asksaveasfilename(
            defaultextension='.csv', filetypes=[('CSV', '*.csv')]
        )
        if path:
            try:
                self.metrics.export_to_csv(path)
                messagebox.showinfo('Eksport', f'CSV saqlandi:\n{path}')
            except Exception as e:
                messagebox.showerror('Xato', str(e))