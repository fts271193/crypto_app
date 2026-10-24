"""
DES-CBC shifrlash va deshifrlash
"""
from Crypto.Cipher import DES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import binascii
from crypto.authenticated_cbc import AuthenticatedCBC

class DESHandler:
    KEY_SIZE = 8  # 64 bit (56 bit effective)
    BLOCK_SIZE = 8  # 64 bit
    MAGIC = b'DESC1'
    
    @staticmethod
    def generate_key():
        """Tasodifiy kalit generatsiya"""
        key = get_random_bytes(DESHandler.KEY_SIZE)
        return binascii.hexlify(key).decode('utf-8')
    
    @staticmethod
    def key_from_hex(hex_key):
        """Hex string'dan kalit olish"""
        try:
            return binascii.unhexlify(hex_key)
        except (binascii.Error, ValueError) as e:
            raise ValueError(f"Noto'g'ri hex format: {e}")
    
    @staticmethod
    def encrypt(data, hex_key):
        """
        Ma'lumotni shifrlash
        Args:
            data: bytes - shifrlash uchun ma'lumot
            hex_key: str - hex formatdagi kalit (16 belgi)
        Returns:
            tuple: (encrypted_data, iv_hex)
        """
        # Kalitni bytes'ga aylantirish
        key = DESHandler.key_from_hex(hex_key)
        
        if len(key) != DESHandler.KEY_SIZE:
            raise ValueError(f"Kalit uzunligi {DESHandler.KEY_SIZE} bayt bo'lishi kerak")
        
        # IV generatsiya
        iv = get_random_bytes(DESHandler.BLOCK_SIZE)
        
        # Cipher yaratish
        cipher = DES.new(key, DES.MODE_CBC, iv)
        
        # Padding va shifrlash
        padded_data = pad(data, DESHandler.BLOCK_SIZE)
        encrypted_data = cipher.encrypt(padded_data)
        
        result = AuthenticatedCBC.pack(
            DESHandler.MAGIC, key, iv, encrypted_data
        )
        iv_hex = binascii.hexlify(iv).decode('utf-8')
        
        return result, iv_hex
    
    @staticmethod
    def decrypt(encrypted_data, hex_key):
        """
        Ma'lumotni deshifrlash
        Args:
            encrypted_data: bytes - shifrlangan ma'lumot (IV + ciphertext)
            hex_key: str - hex formatdagi kalit
        Returns:
            bytes: deshifrlangan ma'lumot
        """
        # Kalitni bytes'ga aylantirish
        key = DESHandler.key_from_hex(hex_key)
        
        if len(key) != DESHandler.KEY_SIZE:
            raise ValueError(f"Kalit uzunligi {DESHandler.KEY_SIZE} bayt bo'lishi kerak")
        
        iv, ciphertext = AuthenticatedCBC.unpack(
            encrypted_data,
            DESHandler.MAGIC,
            key,
            DESHandler.BLOCK_SIZE,
            DESHandler.BLOCK_SIZE,
        )
        cipher = DES.new(key, DES.MODE_CBC, iv)
        decrypted_data = cipher.decrypt(ciphertext)
        
        # Padding olib tashlash
        try:
            unpadded_data = unpad(decrypted_data, DESHandler.BLOCK_SIZE)
            return unpadded_data
        except ValueError:
            raise ValueError("❌ Kalit noto'g'ri yoki fayl buzilgan.")
    
    @staticmethod
    def get_info():
        """Algoritm haqida ma'lumot"""
        return {
            'name': 'DES-CBC',
            'key_size': DESHandler.KEY_SIZE * 8,  # bit
            'block_size': DESHandler.BLOCK_SIZE * 8,  # bit
            'mode': 'CBC + HMAC-SHA-256',
            'description': 'DES-CBC with HMAC-SHA-256 integrity protection; educational use only',
            'warning': 'DES zaif algoritm, faqat o\'quv maqsadida'
        }
