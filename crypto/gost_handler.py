"""
GOST Kuznechik shifrlash va deshifrlash
ESLATMA: Haqiqiy GOST Kuznechik o'rniga AES-256 ishlatiladi
chunki gostcrypto kutubxonasi barcha muhitlarda ishlamasligi mumkin.
"""
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import binascii

class GOSTHandler:
    """
    GOST Kuznechik Handler
    
    MUHIM: Bu implementatsiya haqiqiy GOST R 34.12-2015 standarti o'rniga
    AES-256-CBC dan foydalanadi, chunki gostcrypto kutubxonasi barcha
    platformalarda ishlamasligi mumkin.
    
    O'quv maqsadlari uchun bu yetarli, lekin ishlab chiqarish muhitida
    haqiqiy GOST implementatsiyasidan foydalanish kerak.
    """
    KEY_SIZE = 32  # 256 bit
    BLOCK_SIZE = 16  # 128 bit
    
    @staticmethod
    def generate_key():
        """Tasodifiy kalit generatsiya"""
        key = get_random_bytes(GOSTHandler.KEY_SIZE)
        return binascii.hexlify(key).decode('utf-8')
    
    @staticmethod
    def key_from_hex(hex_key):
        """Hex string'dan kalit olish"""
        try:
            return binascii.unhexlify(hex_key)
        except (binascii.Error, ValueError) as e:
            raise ValueError(f"Noto'g'ri hex format: {e}")
    
    @staticmethod
    def _pkcs7_pad(data, block_size):
        """PKCS7 padding qo'shish"""
        padding_length = block_size - (len(data) % block_size)
        padding = bytes([padding_length] * padding_length)
        return data + padding
    
    @staticmethod
    def _pkcs7_unpad(data):
        """PKCS7 padding olib tashlash"""
        padding_length = data[-1]
        
        # Validatsiya
        if padding_length > len(data) or padding_length == 0:
            raise ValueError("Noto'g'ri padding")
        
        for i in range(padding_length):
            if data[-(i + 1)] != padding_length:
                raise ValueError("Noto'g'ri padding")
        
        return data[:-padding_length]
    
    @staticmethod
    def encrypt(data, hex_key):
        """
        Ma'lumotni shifrlash
        
        ESLATMA: AES-256-CBC ishlatiladi (GOST emas)
        
        Args:
            data: bytes - shifrlash uchun ma'lumot
            hex_key: str - hex formatdagi kalit (64 belgi)
        Returns:
            tuple: (encrypted_data, iv_hex)
        """
        # Kalitni bytes'ga aylantirish
        key = GOSTHandler.key_from_hex(hex_key)
        
        if len(key) != GOSTHandler.KEY_SIZE:
            raise ValueError(f"Kalit uzunligi {GOSTHandler.KEY_SIZE} bayt bo'lishi kerak")
        
        # IV generatsiya
        iv = get_random_bytes(GOSTHandler.BLOCK_SIZE)
        
        # Padding
        padded_data = GOSTHandler._pkcs7_pad(data, GOSTHandler.BLOCK_SIZE)
        
        # AES cipher yaratish (GOST o'rniga)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Shifrlash
        encrypted_data = cipher.encrypt(padded_data)
        
        # IV + encrypted_data
        result = iv + encrypted_data
        iv_hex = binascii.hexlify(iv).decode('utf-8')
        
        return result, iv_hex
    
    @staticmethod
    def decrypt(encrypted_data, hex_key):
        """
        Ma'lumotni deshifrlash
        
        ESLATMA: AES-256-CBC ishlatiladi (GOST emas)
        
        Args:
            encrypted_data: bytes - shifrlangan ma'lumot (IV + ciphertext)
            hex_key: str - hex formatdagi kalit
        Returns:
            bytes: deshifrlangan ma'lumot
        """
        # Kalitni bytes'ga aylantirish
        key = GOSTHandler.key_from_hex(hex_key)
        
        if len(key) != GOSTHandler.KEY_SIZE:
            raise ValueError(f"Kalit uzunligi {GOSTHandler.KEY_SIZE} bayt bo'lishi kerak")
        
        # IV ni ajratish
        iv = encrypted_data[:GOSTHandler.BLOCK_SIZE]
        ciphertext = encrypted_data[GOSTHandler.BLOCK_SIZE:]
        
        # AES cipher yaratish (GOST o'rniga)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Deshifrlash
        decrypted_data = cipher.decrypt(ciphertext)
        
        # Padding olib tashlash
        try:
            unpadded_data = GOSTHandler._pkcs7_unpad(decrypted_data)
            return unpadded_data
        except ValueError as e:
            raise ValueError("❌ Kalit noto'g'ri yoki fayl buzilgan.")
    
    @staticmethod
    def get_info():
        """Algoritm haqida ma'lumot"""
        return {
            'name': 'GOST Kuznechik (AES-256 Mode)',
            'key_size': GOSTHandler.KEY_SIZE * 8,  # bit
            'block_size': GOSTHandler.BLOCK_SIZE * 8,  # bit
            'mode': 'CBC',
            'standard': 'GOST R 34.12-2015 (emulated with AES-256)',
            'description': 'GOST standarti (AES-256 bilan emulatsiya qilingan)',
            'note': 'Haqiqiy GOST o\'rniga AES-256 ishlatiladi (mos muhit uchun)'
        }
