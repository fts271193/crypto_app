"""Kalitlar omborini foydalanuvchi hisobiga bog'lab himoyalash."""
import ctypes
import json
import os
import tempfile
import uuid
from ctypes import wintypes
from datetime import datetime
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class _DataBlob(ctypes.Structure):
    _fields_ = [
        ('cbData', wintypes.DWORD),
        ('pbData', ctypes.POINTER(ctypes.c_ubyte)),
    ]


class KeyManager:
    MASTER_MARKER = b'DPAPI1'
    STORE_MARKER = b'KEYS1'
    NONCE_SIZE = 12

    def __init__(self, data_dir=None):
        self.data_dir = Path(data_dir) if data_dir else Path.home() / '.crypto_app'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.keys_file = self.data_dir / 'keys.json.enc'
        self.config_file = self.data_dir / 'config.json'
        self.master_key = self._get_or_create_master_key()

    @staticmethod
    def _blob(data):
        buffer = ctypes.create_string_buffer(data)
        return _DataBlob(
            len(data),
            ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte)),
        ), buffer

    @classmethod
    def _protect_windows(cls, data, unprotect=False):
        crypt32 = ctypes.WinDLL('crypt32', use_last_error=True)
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        blob_pointer = ctypes.POINTER(_DataBlob)
        crypt32.CryptProtectData.argtypes = [
            blob_pointer, wintypes.LPCWSTR, blob_pointer, ctypes.c_void_p,
            ctypes.c_void_p, wintypes.DWORD, blob_pointer,
        ]
        crypt32.CryptProtectData.restype = wintypes.BOOL
        crypt32.CryptUnprotectData.argtypes = [
            blob_pointer, ctypes.POINTER(wintypes.LPWSTR), blob_pointer,
            ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, blob_pointer,
        ]
        crypt32.CryptUnprotectData.restype = wintypes.BOOL
        kernel32.LocalFree.argtypes = [ctypes.c_void_p]
        kernel32.LocalFree.restype = ctypes.c_void_p
        input_blob, input_buffer = cls._blob(data)
        output_blob = _DataBlob()
        if unprotect:
            success = crypt32.CryptUnprotectData(
                ctypes.byref(input_blob), None, None, None, None, 1,
                ctypes.byref(output_blob),
            )
        else:
            success = crypt32.CryptProtectData(
                ctypes.byref(input_blob), 'Crypto App master key',
                None, None, None, 1, ctypes.byref(output_blob),
            )
        if not success:
            raise ctypes.WinError(ctypes.get_last_error())
        try:
            return ctypes.string_at(output_blob.pbData, output_blob.cbData)
        finally:
            kernel32.LocalFree(output_blob.pbData)
            del input_buffer

    def _atomic_write(self, path, data, mode=0o600):
        temp_name = None
        try:
            with tempfile.NamedTemporaryFile(
                mode='wb', dir=self.data_dir, delete=False
            ) as temp_file:
                temp_name = temp_file.name
                temp_file.write(data)
                temp_file.flush()
                os.fsync(temp_file.fileno())
            if os.name != 'nt':
                os.chmod(temp_name, mode)
            os.replace(temp_name, path)
        except OSError:
            if temp_name and os.path.exists(temp_name):
                os.unlink(temp_name)
            raise

    def _get_or_create_master_key(self):
        master_file = self.data_dir / '.master'
        if master_file.exists():
            stored = master_file.read_bytes()
            if os.name == 'nt':
                if stored.startswith(self.MASTER_MARKER):
                    master_key = self._protect_windows(
                        stored[len(self.MASTER_MARKER):], unprotect=True
                    )
                elif len(stored) == 32:
                    master_key = stored
                    protected = self._protect_windows(master_key)
                    self._atomic_write(
                        master_file, self.MASTER_MARKER + protected
                    )
                else:
                    raise ValueError('Master kalit faylining formati noto‘g‘ri.')
            else:
                if len(stored) != 32:
                    raise ValueError('Master kalit faylining formati noto‘g‘ri.')
                master_key = stored
                os.chmod(master_file, 0o600)
            if len(master_key) != 32:
                raise ValueError('Master kalit uzunligi noto‘g‘ri.')
            return master_key

        master_key = get_random_bytes(32)
        stored = (
            self.MASTER_MARKER + self._protect_windows(master_key)
            if os.name == 'nt' else master_key
        )
        self._atomic_write(master_file, stored)
        return master_key

    def _encrypt_data(self, data):
        nonce = get_random_bytes(self.NONCE_SIZE)
        ciphertext = AESGCM(self.master_key).encrypt(
            nonce, data.encode('utf-8'), self.STORE_MARKER
        )
        return self.STORE_MARKER + nonce + ciphertext

    def _decrypt_data(self, encrypted_data):
        if encrypted_data.startswith(self.STORE_MARKER):
            offset = len(self.STORE_MARKER)
            if len(encrypted_data) < offset + self.NONCE_SIZE + 16:
                raise ValueError('Kalitlar fayli to‘liq emas.')
            nonce = encrypted_data[offset:offset + self.NONCE_SIZE]
            try:
                plaintext = AESGCM(self.master_key).decrypt(
                    nonce, encrypted_data[offset + self.NONCE_SIZE:],
                    self.STORE_MARKER,
                )
            except InvalidTag as exc:
                raise ValueError('Kalitlar fayli buzilgan yoki master kalit mos emas.') from exc
            return plaintext.decode('utf-8')

        if len(encrypted_data) < AES.block_size * 2 or (
            len(encrypted_data) - AES.block_size
        ) % AES.block_size:
            raise ValueError('Eski kalitlar faylining formati noto‘g‘ri.')
        iv, ciphertext = encrypted_data[:AES.block_size], encrypted_data[AES.block_size:]
        try:
            plaintext = unpad(
                AES.new(self.master_key, AES.MODE_CBC, iv).decrypt(ciphertext),
                AES.block_size,
            )
            return plaintext.decode('utf-8')
        except (ValueError, UnicodeDecodeError) as exc:
            raise ValueError('Eski kalitlar faylini ochib bo‘lmadi.') from exc

    @staticmethod
    def _empty_keys():
        return {'AES': [], 'DES': [], 'GOST': [], 'OZ_DST_1105': [], 'ECC': []}

    def load_keys(self):
        if not self.keys_file.exists():
            return self._empty_keys()
        encrypted_data = self.keys_file.read_bytes()
        if not encrypted_data:
            return self._empty_keys()
        try:
            keys = json.loads(self._decrypt_data(encrypted_data))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError(f'Saqlangan kalitlarni yuklab bo‘lmadi: {exc}') from exc
        if not isinstance(keys, dict) or any(
            not isinstance(entries, list) for entries in keys.values()
        ):
            raise ValueError('Saqlangan kalitlar ombori tuzilishi noto‘g‘ri.')

        # Oldingi CBC formatidagi ombor yangi autentifikatsiyalangan formatga ko'chiriladi.
        if not encrypted_data.startswith(self.STORE_MARKER):
            self.save_keys(keys)
        return keys

    def save_keys(self, keys_dict):
        encrypted_data = self._encrypt_data(json.dumps(keys_dict, indent=2))
        self._atomic_write(self.keys_file, encrypted_data)
        return True

    @staticmethod
    def _new_entry_id():
        return uuid.uuid4().hex

    def add_key(self, algorithm, key, label=''):
        keys = self.load_keys()
        entries = keys.setdefault(algorithm, [])
        if any(item.get('key') == key for item in entries):
            return False, 'Bu kalit allaqachon saqlangan'
        entries.append({
            'id': self._new_entry_id(),
            'key': key,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'label': label or f'{algorithm} kalit {len(entries) + 1}',
        })
        keys[algorithm] = entries[-10:]
        self.save_keys(keys)
        return True, 'Kalit saqlandi'

    def add_ecc_keypair(self, public_key, private_key, label=''):
        keys = self.load_keys()
        entries = keys.setdefault('ECC', [])
        entries.append({
            'id': self._new_entry_id(),
            'public': public_key,
            'private': private_key,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'label': label or f'ECC kalit {len(entries) + 1}',
        })
        keys['ECC'] = entries[-10:]
        self.save_keys(keys)
        return True, 'Kalit jufti saqlandi'

    def get_recent_keys(self, algorithm, count=5):
        if count <= 0:
            return []
        return list(reversed(self.load_keys().get(algorithm, [])[-count:]))

    def delete_key(self, algorithm, index):
        keys = self.load_keys()
        if algorithm not in keys or not 0 <= index < len(keys[algorithm]):
            return False
        del keys[algorithm][index]
        self.save_keys(keys)
        return True

    def clear_all_keys(self, algorithm=None):
        keys = self.load_keys()
        if algorithm:
            keys.setdefault(algorithm, [])
            keys[algorithm] = []
        else:
            keys = self._empty_keys()
        self.save_keys(keys)
        return True

    def load_config(self):
        if not self.config_file.exists():
            return {
                'theme': 'light',
                'language': 'uz',
                'auto_save_keys': True,
                'max_file_size_mb': 500,
            }
        try:
            with self.config_file.open('r', encoding='utf-8') as config_file:
                config = json.load(config_file)
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f'Konfiguratsiyani o‘qib bo‘lmadi: {exc}') from exc
        if not isinstance(config, dict):
            raise ValueError('Konfiguratsiya JSON obyekt bo‘lishi kerak.')
        return config

    def save_config(self, config):
        data = json.dumps(config, indent=2).encode('utf-8')
        self._atomic_write(self.config_file, data)
        return True
