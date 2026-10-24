"""
GUI komponentlar — zamonaviy dark UI
Tuzatilgan: papka tanlash, 1 ustun natijalar, katta shriftlar
"""
import customtkinter as ctk
from tkinter import filedialog
import tkinter as tk
import os

# ── Rang palitasi ──────────────────────────────────────────────
COLORS = {
    'bg_dark':      '#0F1117',
    'bg_card':      '#1A1D2E',
    'bg_input':     '#252838',
    'border':       '#2E3250',
    'accent':       '#6C63FF',
    'accent_hover': '#5A52E0',
    'success':      '#22C55E',
    'success_h':    '#16A34A',
    'danger':       '#EF4444',
    'danger_h':     '#DC2626',
    'warning':      '#F59E0B',
    'text_primary': '#F0F0FF',
    'text_sec':     '#8B8FA8',
    'text_dim':     '#4B5063',
}

# ── Shrift o'lchamlari ─────────────────────────────────────────
F_TITLE  = ('Helvetica', 22, 'bold')
F_LABEL  = ('Helvetica', 17, 'bold')
F_BODY   = ('Helvetica', 15)
F_SMALL  = ('Helvetica', 14)
F_MONO   = ('Courier',   15)
F_BTN    = ('Helvetica', 16, 'bold')
F_BTN_SM = ('Helvetica', 15)


# ──────────────────────────────────────────────────────────────
# Bazaviy komponentlar
# ──────────────────────────────────────────────────────────────

class GlassCard(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        kwargs.setdefault('fg_color',      COLORS['bg_card'])
        kwargs.setdefault('corner_radius', 12)
        kwargs.setdefault('border_width',  1)
        kwargs.setdefault('border_color',  COLORS['border'])
        super().__init__(master, **kwargs)


class SectionHeader(ctk.CTkFrame):
    """Bo'lim sarlavhasi + chiziq"""
    def __init__(self, master, text, icon='', **kwargs):
        kwargs['fg_color'] = 'transparent'
        super().__init__(master, **kwargs)

        row = ctk.CTkFrame(self, fg_color='transparent')
        row.pack(fill='x')

        if icon:
            ctk.CTkLabel(
                row, text=icon,
                font=('Helvetica', 16),
                text_color=COLORS['accent'], width=28
            ).pack(side='left', padx=(0, 6))

        ctk.CTkLabel(
            row, text=text,
            font=F_LABEL,
            text_color=COLORS['text_primary']
        ).pack(side='left')

        ctk.CTkFrame(
            self, height=1,
            fg_color=COLORS['border'], corner_radius=0
        ).pack(fill='x', pady=(8, 0))


# ── Tugmalar ──────────────────────────────────────────────────

class PrimaryButton(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        kwargs.setdefault('fg_color',      COLORS['accent'])
        kwargs.setdefault('hover_color',   COLORS['accent_hover'])
        kwargs.setdefault('corner_radius', 8)
        kwargs.setdefault('font',          F_BTN_SM)
        kwargs.setdefault('text_color',    '#FFFFFF')
        kwargs.setdefault('height',        46)
        super().__init__(master, **kwargs)


class SuccessButton(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        kwargs.setdefault('fg_color',      COLORS['success'])
        kwargs.setdefault('hover_color',   COLORS['success_h'])
        kwargs.setdefault('corner_radius', 8)
        kwargs.setdefault('font',          F_BTN)
        kwargs.setdefault('text_color',    '#FFFFFF')
        kwargs.setdefault('height',        52)
        super().__init__(master, **kwargs)


class DangerButton(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        kwargs.setdefault('fg_color',      COLORS['danger'])
        kwargs.setdefault('hover_color',   COLORS['danger_h'])
        kwargs.setdefault('corner_radius', 8)
        kwargs.setdefault('font',          F_BTN)
        kwargs.setdefault('text_color',    '#FFFFFF')
        kwargs.setdefault('height',        52)
        super().__init__(master, **kwargs)


class GhostButton(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        kwargs.setdefault('fg_color',      'transparent')
        kwargs.setdefault('hover_color',   COLORS['bg_input'])
        kwargs.setdefault('border_width',  1)
        kwargs.setdefault('border_color',  COLORS['border'])
        kwargs.setdefault('corner_radius', 8)
        kwargs.setdefault('font',          F_BTN_SM)
        kwargs.setdefault('text_color',    COLORS['text_sec'])
        kwargs.setdefault('height',        46)
        super().__init__(master, **kwargs)


class ModernEntry(ctk.CTkEntry):
    def __init__(self, master, **kwargs):
        kwargs.setdefault('fg_color',      COLORS['bg_input'])
        kwargs.setdefault('border_color',  COLORS['border'])
        kwargs.setdefault('border_width',  1)
        kwargs.setdefault('corner_radius', 8)
        kwargs.setdefault('font',          F_MONO)
        kwargs.setdefault('text_color',    COLORS['text_primary'])
        kwargs.setdefault('height',        48)
        super().__init__(master, **kwargs)


# ──────────────────────────────────────────────────────────────
# FileSelector
# ──────────────────────────────────────────────────────────────

class FileSelector(ctk.CTkFrame):
    def __init__(self, master, label_text='Fayl tanlash:', file_filter=None, **kwargs):
        kwargs['fg_color'] = 'transparent'
        super().__init__(master, **kwargs)

        self.file_filter   = file_filter
        self.selected_file = None

        SectionHeader(self, text=label_text, icon='📂').pack(fill='x', pady=(0, 10))

        row = ctk.CTkFrame(self, fg_color='transparent')
        row.pack(fill='x')
        row.columnconfigure(0, weight=1)

        self.entry = ModernEntry(row, state='readonly', placeholder_text='Fayl tanlanmagan...')
        self.entry.grid(row=0, column=0, sticky='ew', padx=(0, 10))

        PrimaryButton(row, text='Tanlash', width=120, command=self.select_file).grid(row=0, column=1)

    def select_file(self):
        f = filedialog.askopenfilename(
            title='Faylni tanlang',
            filetypes=self.file_filter if self.file_filter else [('Barcha fayllar', '*.*')]
        )
        if f:
            self.selected_file = f
            self.entry.configure(state='normal')
            self.entry.delete(0, tk.END)
            self.entry.insert(0, f)
            self.entry.configure(state='readonly')

    def get_file(self):
        return self.selected_file

    def clear(self):
        self.selected_file = None
        self.entry.configure(state='normal')
        self.entry.delete(0, tk.END)
        self.entry.configure(state='readonly')


# ──────────────────────────────────────────────────────────────
# KeyInput
# ──────────────────────────────────────────────────────────────

class KeyInput(ctk.CTkFrame):
    """Yashirilgan kalit kiritish maydoni va saqlangan kalitlar ro'yxati."""
    def __init__(self, master, label_text='Shifrlash kaliti:', show_generator=False, **kwargs):
        kwargs['fg_color'] = 'transparent'
        super().__init__(master, **kwargs)

        self.generate_callback = None
        self._saved_keys_data  = []
        self._saved_key_choices = {}

        SectionHeader(self, text=label_text, icon='🔑').pack(fill='x', pady=(0, 10))

        # Kiritish qatori
        row = ctk.CTkFrame(self, fg_color='transparent')
        row.pack(fill='x')
        row.columnconfigure(0, weight=1)

        self.entry = ModernEntry(row, show='•', placeholder_text='Hex formatda kalit kiriting...')
        self.entry.grid(row=0, column=0, sticky='ew', padx=(0, 8))

        if show_generator:
            PrimaryButton(row, text='⚡ Yangi', width=130, command=self._on_generate).grid(row=0, column=1)

        '''# Saqlangan kalitlar (1 ta ComboBox)
        saved_row = ctk.CTkFrame(self, fg_color='transparent')
        saved_row.pack(fill='x', pady=(10, 0))
        saved_row.columnconfigure(1, weight=1)

        ctk.CTkLabel(
            saved_row, text='Saqlangan kalitlar:',
            font=F_BODY, text_color=COLORS['text_sec'],
            width=170, anchor='w'
        ).grid(row=0, column=0, padx=(0, 10))

        self.saved_combo = ctk.CTkComboBox(
            saved_row,
            values=["— yo'q —"],
            fg_color=COLORS['bg_input'],
            border_color=COLORS['border'],
            border_width=1,
            button_color=COLORS['accent'],
            button_hover_color=COLORS['accent_hover'],
            dropdown_fg_color=COLORS['bg_card'],
            dropdown_hover_color=COLORS['bg_input'],
            text_color=COLORS['text_primary'],
            font=('Courier', 14),
            corner_radius=8,
            height=46,
            command=self._on_saved_key_selected
        )
        self.saved_combo.grid(row=0, column=1, sticky='ew')'''

    def _on_generate(self):
        if self.generate_callback:
            key = self.generate_callback()
            if key:
                self.set_key(key)

    def _on_saved_key_selected(self, choice):
        item = self._saved_key_choices.get(choice)
        if item:
            self.set_key(item['key'])

    def set_generate_callback(self, cb): self.generate_callback = cb

    def set_key(self, key):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, key)

    def get_key(self): return self.entry.get().strip()
    def clear(self):   self.entry.delete(0, tk.END)

    def update_saved_keys(self, keys_list):
        self._saved_keys_data = keys_list or []
        self._saved_key_choices = {}
        values = []
        for index, item in enumerate(self._saved_keys_data, start=1):
            suffix = item.get('id', f'#{index}')[:8]
            choice = (
                f"{item.get('label', 'Kalit')} "
                f"({item.get('date', 'sana yo‘q')}) [{suffix}] #{index}"
            )
            self._saved_key_choices[choice] = item
            values.append(choice)
        if not values:
            values = ["— yo'q —"]
        self.saved_combo.configure(values=values)
        self.saved_combo.set(values[0])


# ──────────────────────────────────────────────────────────────
# OutputSelector  — PAPKA tanlash
# ──────────────────────────────────────────────────────────────

class OutputSelector(ctk.CTkFrame):
    """
    Natija PAPKASI tanlash.
    Fayl nomi avtomatik hosil qilinadi, faqat papka tanlanadi.
    """
    def __init__(self, master, label_text='Natija papkasi:', **kwargs):
        kwargs['fg_color'] = 'transparent'
        super().__init__(master, **kwargs)

        self._custom_dir = None
        self._auto_dir   = None
        self._filename   = ''

        SectionHeader(self, text=label_text, icon='📁').pack(fill='x', pady=(0, 10))

        row = ctk.CTkFrame(self, fg_color='transparent')
        row.pack(fill='x')
        row.columnconfigure(0, weight=1)

        self.entry = ModernEntry(
            row, state='readonly',
            placeholder_text='Papka tanlanmasa — manba fayl papkasiga saqlanadi'
        )
        self.entry.grid(row=0, column=0, sticky='ew', padx=(0, 8))

        GhostButton(row, text='📁 Papka', width=130, command=self._browse).grid(row=0, column=1, padx=(0, 6))
        GhostButton(row, text='✕', width=44, command=self.clear).grid(row=0, column=2)

        self.hint_label = ctk.CTkLabel(
            self, text='',
            font=F_SMALL, text_color=COLORS['text_dim'], anchor='w'
        )
        self.hint_label.pack(fill='x', pady=(6, 0))

    def _browse(self):
        folder = filedialog.askdirectory(title='Natija papkasini tanlang')
        if folder:
            self._custom_dir = folder
            self._refresh()

    def _refresh(self):
        folder = self._custom_dir or self._auto_dir
        self.entry.configure(state='normal')
        self.entry.delete(0, tk.END)
        if folder:
            display = os.path.join(folder, self._filename) if self._filename else folder
            self.entry.insert(0, display)
            if self._custom_dir:
                self.hint_label.configure(
                    text=f'✔  Papka: {folder}', text_color=COLORS['success']
                )
            else:
                self.hint_label.configure(
                    text='ℹ  Avtomatik papka  •  "Papka" tugmasi bilan o\'zgartiring',
                    text_color=COLORS['text_dim']
                )
        else:
            self.hint_label.configure(text='', text_color=COLORS['text_dim'])
        self.entry.configure(state='readonly')

    def set_auto_dir(self, folder: str):
        self._auto_dir = folder
        if not self._custom_dir:
            self._refresh()

    def set_filename(self, filename: str):
        self._filename = filename
        self._refresh()

    def get_output_path(self, fallback_dir: str, filename: str) -> str:
        folder = self._custom_dir or self._auto_dir or fallback_dir
        return os.path.join(folder, filename)

    def clear(self):
        self._custom_dir = None
        self._filename   = ''
        self._refresh()

    def full_clear(self):
        self._custom_dir = None
        self._auto_dir   = None
        self._filename   = ''
        self.entry.configure(state='normal')
        self.entry.delete(0, tk.END)
        self.entry.configure(state='readonly')
        self.hint_label.configure(text='')


# ──────────────────────────────────────────────────────────────
# ProgressPanel — 1 ustun, katta shrift
# ──────────────────────────────────────────────────────────────

class ProgressPanel(ctk.CTkFrame):
    _INFO_KEYS = [
        ('algorithm',    'Algoritm'),
        ('file_size',    'Fayl hajmi'),
        ('read_time',    "O'qish vaqti"),
        ('encrypt_time', 'Operatsiya vaqti'),
        ('write_time',   'Yozish vaqti'),
        ('total_time',   'Jami vaqt'),
        ('speed',        'Kripto amali tezligi'),
    ]

    def __init__(self, master, **kwargs):
        kwargs.setdefault('fg_color',      COLORS['bg_card'])
        kwargs.setdefault('corner_radius', 12)
        kwargs.setdefault('border_width',  1)
        kwargs.setdefault('border_color',  COLORS['border'])
        super().__init__(master, **kwargs)

        # Sarlavha
        top = ctk.CTkFrame(self, fg_color='transparent')
        top.pack(fill='x', padx=18, pady=(16, 8))

        ctk.CTkLabel(top, text='📊  Natijalar', font=F_LABEL,
                     text_color=COLORS['text_primary']).pack(side='left')

        self.status_label = ctk.CTkLabel(
            top, text='Kutilmoqda',
            font=('Helvetica', 14, 'bold'),
            text_color=COLORS['text_dim'],
            fg_color=COLORS['bg_input'],
            corner_radius=8, padx=12, pady=4
        )
        self.status_label.pack(side='right')

        # Progress bar
        self.progressbar = ctk.CTkProgressBar(
            self, fg_color=COLORS['bg_input'],
            progress_color=COLORS['accent'],
            corner_radius=4, height=8
        )
        self.progressbar.pack(fill='x', padx=18, pady=(0, 12))
        self.progressbar.set(0)

        ctk.CTkFrame(self, height=1, fg_color=COLORS['border']).pack(fill='x')

        # 1 ustun ma'lumotlar
        col = ctk.CTkFrame(self, fg_color='transparent')
        col.pack(fill='x', padx=18, pady=12)

        self._value_labels = {}
        for key, display in self._INFO_KEYS:
            row = ctk.CTkFrame(col, fg_color='transparent')
            row.pack(fill='x', pady=6)
            row.columnconfigure(0, weight=0, minsize=210)
            row.columnconfigure(1, weight=1)

            ctk.CTkLabel(
                row,
                text=f'{display}:',
                font=F_BODY, text_color=COLORS['text_sec'],
                anchor='w', width=210
            ).grid(row=0, column=0, sticky='w')

            val = ctk.CTkLabel(
                row, text='—',
                font=F_MONO, text_color=COLORS['accent'], anchor='w'
            )
            val.grid(row=0, column=1, sticky='w')
            self._value_labels[key] = val

    def update_progress(self, value: float, status: str = None):
        self.progressbar.set(value)
        if value >= 1.0:
            color, text = COLORS['success'], '✔ Tugallandi'
            self.progressbar.configure(progress_color=COLORS['success'])
        elif value > 0:
            color, text = COLORS['warning'], '⏳ Jarayonda...'
            self.progressbar.configure(progress_color=COLORS['accent'])
        else:
            color, text = COLORS['text_dim'], 'Kutilmoqda'
            self.progressbar.configure(progress_color=COLORS['accent'])
        self.status_label.configure(
            text=status if status else text, text_color=color
        )

    def update_info(self, key: str, value: str):
        if key in self._value_labels:
            self._value_labels[key].configure(text=value)

    def set_error(self):
        self.status_label.configure(text='✕ Xatolik', text_color=COLORS['danger'])
        self.progressbar.configure(progress_color=COLORS['danger'])

    def reset(self):
        self.progressbar.set(0)
        self.progressbar.configure(progress_color=COLORS['accent'])
        self.status_label.configure(text='Kutilmoqda', text_color=COLORS['text_dim'])
        for lbl in self._value_labels.values():
            lbl.configure(text='—')


StyledButton = GhostButton