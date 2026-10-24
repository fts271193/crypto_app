"""RSA, ElGamal va DSA uchun GUI."""
import os
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from crypto.asymmetric_handler import AsymmetricHandler
from crypto.ecc_handler import ECCHandler
from gui.components import (
    COLORS,
    F_BODY,
    F_SMALL,
    F_TITLE,
    FileSelector,
    GlassCard,
    GhostButton,
    ModernEntry,
    OutputSelector,
    PrimaryButton,
    ProgressPanel,
    SectionHeader,
    SuccessButton,
    DangerButton,
)
from utils.file_manager import FileManager
from utils.validator import Validator


class AsymmetricWindow(ctk.CTkScrollableFrame):
    ALGORITHMS = ('ECC', 'RSA', 'ElGamal')#, 'DSA')

    def __init__(self, master, **kwargs):
        kwargs.setdefault('fg_color', COLORS['bg_dark'])
        super().__init__(master, **kwargs)
        self.algorithm = 'RSA'
        self.public_pem = None
        self.private_pem = None
        self.file_manager = FileManager()
        self.validator = Validator()
        self._build_ui()

    def _build_ui(self):
        wrap = ctk.CTkFrame(self, fg_color='transparent')
        wrap.pack(fill='both', expand=True, padx=28, pady=22)

        ctk.CTkLabel(
            wrap, text='🔑  Assimmetrik algoritmlar',
            font=F_TITLE, text_color=COLORS['text_primary'],
        ).pack(anchor='w', pady=(0, 18))

        algo_card = GlassCard(wrap)
        algo_card.pack(fill='x', pady=(0, 14))
        SectionHeader(algo_card, text='Algoritm tanlang', icon='⚙️').pack(
            fill='x', padx=18, pady=(16, 10)
        )
        self.algo_selector = ctk.CTkSegmentedButton(
            algo_card, values=list(self.ALGORITHMS), command=self._on_algorithm_change,
        )
        self.algo_selector.pack(fill='x', padx=18, pady=(0, 8))
        self.algo_selector.set(self.algorithm)
        self.info_label = ctk.CTkLabel(
            algo_card, text='', font=F_SMALL, text_color=COLORS['text_dim'],
        )
        self.info_label.pack(fill='x', padx=18, pady=(0, 14))

        key_card = GlassCard(wrap)
        key_card.pack(fill='x', pady=(0, 14))
        SectionHeader(key_card, text='Kalit boshqaruvi', icon='🗝️').pack(
            fill='x', padx=18, pady=(16, 12)
        )
        PrimaryButton(
            key_card, text='⚡  Yangi kalit juftligi yaratish',
            height=44, command=self._generate,
        ).pack(pady=(0, 12))

        for label, private in (('Public key', False), ('Private key', True)):
            row = ctk.CTkFrame(key_card, fg_color='transparent')
            row.pack(fill='x', padx=18, pady=(0, 10))
            row.columnconfigure(0, weight=1)
            entry = ModernEntry(
                row, state='readonly',
                placeholder_text=f'{label} yuklanmagan',
                show='•' if private else '',
            )
            entry.grid(row=0, column=0, sticky='ew', padx=(0, 10))
            GhostButton(
                row, text='📂 Yuklash', width=120,
                command=lambda is_private=private: self._load_key(is_private),
            ).grid(row=0, column=1)
            if private:
                self.private_entry = entry
            else:
                self.public_entry = entry

        GhostButton(
            key_card, text='💾  Kalitlarni papkaga saqlash',
            height=40, command=self._save_keys,
        ).pack(pady=(0, 16))

        file_card = GlassCard(wrap)
        file_card.pack(fill='x', pady=(0, 14))
        self.file_selector = FileSelector(
            file_card, label_text='Kirish fayli',
            file_filter=self.validator.format_file_filter(),
        )
        self.file_selector.pack(fill='x', padx=18, pady=16)
        self.signature_selector = FileSelector(
            file_card, label_text='Tekshirish uchun imzo fayli',
            file_filter=[('Imzo fayllari', '*.sig'), ('Barcha fayllar', '*.*')],
        )

        out_card = GlassCard(wrap)
        out_card.pack(fill='x', pady=(0, 14))
        self.output_selector = OutputSelector(out_card, label_text='Natija saqlanish papkasi')
        self.output_selector.pack(fill='x', padx=18, pady=16)

        button_card = ctk.CTkFrame(wrap, fg_color='transparent')
        button_card.pack(fill='x')
        button_card.columnconfigure((0, 1), weight=1)
        self.encrypt_button = SuccessButton(
            button_card, text='⬆  Shifrlash', command=self.encrypt_file,
        )
        self.encrypt_button.grid(row=0, column=0, sticky='ew', padx=(0, 8), pady=4)
        self.decrypt_button = DangerButton(
            button_card, text='⬇  Deshifrlash', command=self.decrypt_file,
        )
        self.decrypt_button.grid(row=0, column=1, sticky='ew', padx=(8, 0), pady=4)
        self.sign_button = SuccessButton(
            button_card, text='✍  Imzo yaratish', command=self.sign_file,
        )
        self.sign_button.grid(row=1, column=0, sticky='ew', padx=(0, 8), pady=4)
        self.verify_button = PrimaryButton(
            button_card, text='✓  Imzoni tekshirish', command=self.verify_file,
        )
        self.verify_button.grid(row=1, column=1, sticky='ew', padx=(8, 0), pady=4)

        self.progress_panel = ProgressPanel(wrap)
        self.progress_panel.pack(fill='x', pady=(18, 0))
        self._on_algorithm_change(self.algorithm)

    def _on_algorithm_change(self, algorithm):
        self.algorithm = algorithm
        is_dsa = algorithm == 'DSA'
        descriptions = {
            'RSA': 'RSA-OAEP', #+ AES-256-GCM: faylni ochiq kalit bilan shifrlaydi.',
            'ElGamal': 'ElGamal',# + AES-256-GCM: faylni ochiq kalit bilan shifrlaydi.',
            'ECC': 'ECIES (P-256/ECDH)',# + AES-256-GCM: egri chiziqli ochiq kalit bilan shifrlaydi.',
            'DSA': 'DSA shifrlamaydi: private key bilan imzo yaratadi, public key bilan tekshiradi.',
        }
        self.info_label.configure(text=descriptions[algorithm])
        self.signature_selector.pack_forget()
        self.encrypt_button.grid_remove()
        self.decrypt_button.grid_remove()
        self.sign_button.grid_remove()
        self.verify_button.grid_remove()
        if is_dsa:
            self.signature_selector.pack(fill='x', padx=18, pady=(0, 16))
            self.sign_button.grid()
            self.verify_button.grid()
        else:
            self.encrypt_button.grid()
            self.decrypt_button.grid()

    def _generate(self):
        try:
            if self.algorithm == 'ECC':
                self.private_pem, self.public_pem = ECCHandler.generate_keypair()
            else:
                self.private_pem, self.public_pem = AsymmetricHandler.generate_keypair(self.algorithm)
            self._set_entry(self.public_entry, f'[{len(self.public_pem)} belgi]')
            self._set_entry(self.private_entry, f'[{len(self.private_pem)} belgi]')
            messagebox.showinfo('Tayyor', f'{self.algorithm} kalit juftligi yaratildi.')
        except Exception as exc:
            messagebox.showerror('Xato', str(exc))

    def _load_key(self, private):
        path = filedialog.askopenfilename(
            title='Private key' if private else 'Public key',
            filetypes=[('PEM kalitlar', '*.pem'), ('Barcha fayllar', '*.*')],
        )
        if not path:
            return
        try:
            with open(path, 'r', encoding='ascii') as key_file:
                key_data = key_file.read()
            if private:
                self.private_pem = key_data
                self._set_entry(self.private_entry, f'[Yuklandi: {os.path.basename(path)}]')
            else:
                self.public_pem = key_data
                self._set_entry(self.public_entry, f'[Yuklandi: {os.path.basename(path)}]')
        except Exception as exc:
            messagebox.showerror('Kalit xatosi', str(exc))

    def _save_keys(self):
        if not self.public_pem and not self.private_pem:
            messagebox.showwarning('Ogohlantirish', 'Avval kalit juftligini yarating yoki yuklang.')
            return
        folder = filedialog.askdirectory(title='Kalitlarni saqlash papkasi')
        if not folder:
            return
        try:
            if self.public_pem:
                with open(os.path.join(folder, f'{self.algorithm.lower()}_public.pem'), 'w', encoding='ascii') as key_file:
                    key_file.write(self.public_pem)
            if self.private_pem:
                with open(os.path.join(folder, f'{self.algorithm.lower()}_private.pem'), 'w', encoding='ascii') as key_file:
                    key_file.write(self.private_pem)
            messagebox.showinfo('Saqlandi', f'Kalitlar saqlandi:\n{folder}')
        except Exception as exc:
            messagebox.showerror('Xato', str(exc))

    def _selected_file(self):
        path = self.file_selector.get_file()
        if not path:
            messagebox.showwarning('Ogohlantirish', 'Kirish faylini tanlang.')
            return None
        ok, error = self.validator.validate_file(path)
        if not ok:
            messagebox.showerror('Fayl xatosi', error)
            return None
        return path

    def _output_path(self, source, filename):
        source_dir = os.path.dirname(source)
        self.output_selector.set_auto_dir(source_dir)
        self.output_selector.set_filename(filename)
        return self.output_selector.get_output_path(source_dir, filename)

    def encrypt_file(self):
        if not self.public_pem:
            messagebox.showwarning('Ogohlantirish', 'Shifrlash uchun public key yuklang.')
            return
        source = self._selected_file()
        if source:
            extension = {'RSA': '.rsa', 'ElGamal': '.elg', 'ECC': '.ecc'}[self.algorithm]
            self._start_worker('encrypt', source, self._output_path(source, os.path.basename(source) + extension), self.public_pem)

    def decrypt_file(self):
        if not self.private_pem:
            messagebox.showwarning('Ogohlantirish', 'Deshifrlash uchun private key yuklang.')
            return
        source = self._selected_file()
        if source:
            extension = {'RSA': '.rsa', 'ElGamal': '.elg', 'ECC': '.ecc'}[self.algorithm]
            name = os.path.basename(source)
            filename = name[:-len(extension)] if name.endswith(extension) else name + '.dec'
            self._start_worker('decrypt', source, self._output_path(source, filename), self.private_pem)

    def sign_file(self):
        if not self.private_pem:
            messagebox.showwarning('Ogohlantirish', 'Imzo yaratish uchun DSA private key yuklang.')
            return
        source = self._selected_file()
        if source:
            self._start_worker('sign', source, self._output_path(source, os.path.basename(source) + '.sig'), self.private_pem)

    def verify_file(self):
        if not self.public_pem:
            messagebox.showwarning('Ogohlantirish', 'Imzoni tekshirish uchun DSA public key yuklang.')
            return
        source = self._selected_file()
        signature = self.signature_selector.get_file()
        if not source:
            return
        if not signature:
            messagebox.showwarning('Ogohlantirish', 'Tekshirish uchun imzo faylini tanlang.')
            return
        self._start_worker('verify', source, signature, self.public_pem)

    def _start_worker(self, action, source, destination, key_pem):
        if action != 'verify' and os.path.abspath(source) == os.path.abspath(destination):
            messagebox.showerror('Yo‘l xatosi', 'Natija fayli manba fayl bilan bir xil bo‘la olmaydi.')
            return
        if action != 'verify' and os.path.exists(destination) and not messagebox.askyesno(
            'Fayl mavjud', f'{destination}\n\nFayl ustiga yozilsinmi?'
        ):
            return
        self.progress_panel.reset()
        threading.Thread(
            target=self._worker,
            args=(action, source, destination, key_pem, self.algorithm),
            daemon=True,
        ).start()

    def _worker(self, action, source, destination, key_pem, algorithm):
        try:
            started_at = time.perf_counter()
            self.after(0, lambda: self.progress_panel.update_progress(0.15, "Fayl o'qilmoqda..."))
            self.after(0, lambda: self.progress_panel.update_info('algorithm', algorithm))
            read_started_at = time.perf_counter()
            data = self.file_manager.read_file(source)
            read_time = time.perf_counter() - read_started_at
            file_size = len(data)
            self.after(0, lambda size=file_size: self.progress_panel.update_info(
                'file_size', f'{size:,} bayt',
            ))
            self.after(0, lambda duration=read_time: self.progress_panel.update_info(
                'read_time', f'{duration:.3f} s',
            ))

            operation_names = {
                'encrypt': 'Shifrlash',
                'decrypt': 'Deshifrlash',
                'sign': 'Imzo yaratish',
                'verify': 'Imzoni tekshirish',
            }
            self.after(0, lambda name=operation_names[action]: self.progress_panel.update_progress(
                0.5, f'{name}...',
            ))
            signature = None
            if action == 'verify':
                with open(destination, 'rb') as signature_file:
                    signature = signature_file.read()
            if action not in {'encrypt', 'decrypt', 'sign', 'verify'}:
                raise ValueError(f'Noma’lum amal: {action}')

            operation_times = []
            result = None
            for _ in range(5):
                operation_started_at = time.perf_counter()
                if action == 'encrypt':
                    result = (
                        ECCHandler.encrypt(data, key_pem)
                        if algorithm == 'ECC'
                        else AsymmetricHandler.encrypt(data, key_pem, algorithm)
                    )
                elif action == 'decrypt':
                    result = (
                        ECCHandler.decrypt(data, key_pem)
                        if algorithm == 'ECC'
                        else AsymmetricHandler.decrypt(data, key_pem, algorithm)
                    )
                elif action == 'sign':
                    result = AsymmetricHandler.sign(data, key_pem)
                else:
                    valid = AsymmetricHandler.verify(data, signature, key_pem)
                operation_times.append(time.perf_counter() - operation_started_at)
            operation_time = sum(operation_times) / len(operation_times)
            variance = sum((duration - operation_time) ** 2 for duration in operation_times) / len(operation_times)
            operation_std = variance ** 0.5

            write_time = None
            if action != 'verify':
                self.after(0, lambda: self.progress_panel.update_progress(
                    0.85, 'Natija faylga yozilmoqda...',
                ))
                write_started_at = time.perf_counter()
                self.file_manager.write_file(destination, result)
                write_time = time.perf_counter() - write_started_at

            total_time = time.perf_counter() - started_at
            speed = file_size / operation_time / (1024 * 1024) if operation_time > 0 else 0
            metrics = [
                ('encrypt_time', f'{operation_time:.6f} ± {operation_std:.6f} s (n=5)'),
                ('write_time', f'{write_time:.3f} s' if write_time is not None else '—'),
                ('total_time', f'{total_time:.3f} s'),
                ('speed', f'{speed:.2f} MB/s'),
            ]
            for key, value in metrics:
                self.after(0, lambda key=key, value=value: self.progress_panel.update_info(
                    key, value,
                ))

            if action == 'verify':
                status = 'Imzo haqiqiy' if valid else 'Imzo haqiqiy emas'
                self.after(0, lambda text=status: self.progress_panel.update_progress(1.0, text))
                self.after(0, lambda result=valid: messagebox.showinfo(
                    'Imzo tekshiruvi',
                    'Imzo haqiqiy: fayl o‘zgartirilmagan.' if result else 'Imzo haqiqiy emas yoki fayl o‘zgartirilgan.',
                ))
            else:
                self.after(0, lambda: self.progress_panel.update_progress(1.0, 'Tugallandi'))
                self.after(0, lambda name=operation_names[action]: messagebox.showinfo(
                    'Muvaffaqiyat', f'{name} muvaffaqiyatli yakunlandi.\n\nNatija fayli:\n{destination}',
                ))
        except Exception as exc:
            self.after(0, self.progress_panel.set_error)
            self.after(0, lambda error=exc: messagebox.showerror('Xatolik', str(error)))

    @staticmethod
    def _set_entry(entry, text):
        entry.configure(state='normal')
        entry.delete(0, tk.END)
        entry.insert(0, text)
        entry.configure(state='readonly')