"""
AES-256-CBC shifrlash va deshifrlash
"""
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import binascii

class AESHandler:
    KEY_SIZE = 32  # 256 bit
    BLOCK_SIZE = 16  # 128 bit
    
    @staticmethod
    def generate_key():
        """Tasodifiy kalit generatsiya"""
        key = get_random_bytes(AESHandler.KEY_SIZE)
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
            hex_key: str - hex formatdagi kalit (64 belgi)
        Returns:
            tuple: (encrypted_data, iv_hex)
        """
        # Kalitni bytes'ga aylantirish
        key = AESHandler.key_from_hex(hex_key)
        
        if len(key) != AESHandler.KEY_SIZE:
            raise ValueError(f"Kalit uzunligi {AESHandler.KEY_SIZE} bayt bo'lishi kerak")
        
        # IV generatsiya
        iv = get_random_bytes(AESHandler.BLOCK_SIZE)
        
        # Cipher yaratish
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Padding va shifrlash
        padded_data = pad(data, AESHandler.BLOCK_SIZE)
        encrypted_data = cipher.encrypt(padded_data)
        
        # IV + encrypted_data
        result = iv + encrypted_data
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
        key = AESHandler.key_from_hex(hex_key)
        
        if len(key) != AESHandler.KEY_SIZE:
            raise ValueError(f"Kalit uzunligi {AESHandler.KEY_SIZE} bayt bo'lishi kerak")
        
        # IV ni ajratish
        iv = encrypted_data[:AESHandler.BLOCK_SIZE]
        ciphertext = encrypted_data[AESHandler.BLOCK_SIZE:]
        
        # Deshifrlash
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_data = cipher.decrypt(ciphertext)
        
        # Padding olib tashlash
        try:
            unpadded_data = unpad(decrypted_data, AESHandler.BLOCK_SIZE)
            return unpadded_data
        except ValueError as e:
            raise ValueError("❌ Kalit noto'g'ri yoki fayl buzilgan.")
    
    @staticmethod
    def get_info():
        """Algoritm haqida ma'lumot"""
        return {
            'name': 'AES-256-CBC',
            'key_size': AESHandler.KEY_SIZE * 8,  # bit
            'block_size': AESHandler.BLOCK_SIZE * 8,  # bit
            'mode': 'CBC',
            'description': 'Advanced Encryption Standard - eng xavfsiz simmetrik algoritm'
        }
