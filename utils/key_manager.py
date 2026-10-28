"""
Kalit boshqaruvi moduli - kalitlarni saqlash va yuklash
"""
import json
import os
from pathlib import Path
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import hashlib

class KeyManager:
    def __init__(self, data_dir=None):
        if data_dir is None:
            # Default: ~/.crypto_app/
            home = Path.home()
            self.data_dir = home / '.crypto_app'
        else:
            self.data_dir = Path(data_dir)
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.keys_file = self.data_dir / 'keys.json.enc'
        self.config_file = self.data_dir / 'config.json'
        
        # Master kalit (dastur uchun)
        self.master_key = self._get_or_create_master_key()
    
    def _get_or_create_master_key(self):
        """Master kalitni olish yoki yaratish"""
        master_key_file = self.data_dir / '.master'
        
        if master_key_file.exists():
            with open(master_key_file, 'rb') as f:
                return f.read()
        else:
            # Yangi master kalit yaratish
            master_key = get_random_bytes(32)  # 256 bit
            with open(master_key_file, 'wb') as f:
                f.write(master_key)
            # Faylni yashirish (Unix)
            if os.name != 'nt':  # Windows emas
                os.chmod(master_key_file, 0o600)
            return master_key
    
    def _encrypt_data(self, data):
        """Ma'lumotni shifrlash"""
        cipher = AES.new(self.master_key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
        return cipher.iv + ct_bytes
    
    def _decrypt_data(self, encrypted_data):
        """Ma'lumotni deshifrlash"""
        iv = encrypted_data[:16]
        ct = encrypted_data[16:]
        cipher = AES.new(self.master_key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode('utf-8')
    
    def load_keys(self):
        """Saqlangan kalitlarni yuklash"""
        if not self.keys_file.exists():
            return {
                'AES': [],
                'DES': [],
                'GOST': [],
                'ECC': []
            }
        
        try:
            with open(self.keys_file, 'rb') as f:
                encrypted_data = f.read()
            
            if not encrypted_data:
                return {'AES': [], 'DES': [], 'GOST': [], 'ECC': []}
            
            json_data = self._decrypt_data(encrypted_data)
            return json.loads(json_data)
        except Exception as e:
            print(f"Kalitlarni yuklashda xatolik: {e}")
            return {'AES': [], 'DES': [], 'GOST': [], 'ECC': []}
    
    def save_keys(self, keys_dict):
        """Kalitlarni saqlash"""
        try:
            json_data = json.dumps(keys_dict, indent=2)
            encrypted_data = self._encrypt_data(json_data)
            
            with open(self.keys_file, 'wb') as f:
                f.write(encrypted_data)
            
            return True
        except Exception as e:
            print(f"Kalitlarni saqlashda xatolik: {e}")
            return False
    
    def add_key(self, algorithm, key, label=""):
        """Yangi kalit qo'shish"""
        keys = self.load_keys()
        
        if algorithm not in keys:
            keys[algorithm] = []
        
        # Kalit mavjudligini tekshirish
        for existing_key in keys[algorithm]:
            if existing_key.get('key') == key:
                return False, "Bu kalit allaqachon saqlangan"
        
        key_entry = {
            'key': key,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'label': label or f"{algorithm} kalit {len(keys[algorithm]) + 1}"
        }
        
        keys[algorithm].append(key_entry)
        
        # Faqat oxirgi 10 ta kalitni saqlash
        if len(keys[algorithm]) > 10:
            keys[algorithm] = keys[algorithm][-10:]
        
        self.save_keys(keys)
        return True, "Kalit saqlandi"
    
    def add_ecc_keypair(self, public_key, private_key, label=""):
        """ECC kalit juftligini qo'shish"""
        keys = self.load_keys()
        
        if 'ECC' not in keys:
            keys['ECC'] = []
        
        keypair_entry = {
            'public': public_key,
            'private': private_key,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'label': label or f"ECC kalit {len(keys['ECC']) + 1}"
        }
        
        keys['ECC'].append(keypair_entry)
        
        # Faqat oxirgi 10 ta juftlikni saqlash
        if len(keys['ECC']) > 10:
            keys['ECC'] = keys['ECC'][-10:]
        
        self.save_keys(keys)
        return True, "Kalit jufti saqlandi"
    
    def get_recent_keys(self, algorithm, count=5):
        """Oxirgi kalitlarni olish"""
        keys = self.load_keys()
        
        if algorithm not in keys:
            return []
        
        # Oxirgi N ta kalitni qaytarish
        return keys[algorithm][-count:]
    
    def delete_key(self, algorithm, index):
        """Kalitni o'chirish"""
        keys = self.load_keys()
        
        if algorithm not in keys or index >= len(keys[algorithm]):
            return False
        
        del keys[algorithm][index]
        self.save_keys(keys)
        return True
    
    def clear_all_keys(self, algorithm=None):
        """Barcha yoki ma'lum algoritm kalitlarini tozalash"""
        keys = self.load_keys()
        
        if algorithm:
            if algorithm in keys:
                keys[algorithm] = []
        else:
            keys = {'AES': [], 'DES': [], 'GOST': [], 'ECC': []}
        
        self.save_keys(keys)
        return True
    
    def load_config(self):
        """Konfiguratsiyani yuklash"""
        if not self.config_file.exists():
            return {
                'theme': 'light',
                'language': 'uz',
                'auto_save_keys': True,
                'max_file_size_mb': 500
            }
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_config(self, config):
        """Konfiguratsiyani saqlash"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except:
            return False
