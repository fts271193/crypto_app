"""AES-256-GCM authenticated encryption and decryption."""
import binascii
import secrets

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class AESHandler:
    KEY_SIZE = 32
    BLOCK_SIZE = 16
    NONCE_SIZE = 12
    MAGIC = b'AESG1'
    
    @staticmethod
    def generate_key():
        """Tasodifiy 256-bit kalit generatsiya."""
        key = secrets.token_bytes(AESHandler.KEY_SIZE)
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
        key = AESHandler.key_from_hex(hex_key)
        if len(key) != AESHandler.KEY_SIZE:
            raise ValueError(f"Kalit uzunligi {AESHandler.KEY_SIZE} bayt bo'lishi kerak")

        nonce = secrets.token_bytes(AESHandler.NONCE_SIZE)
        ciphertext = AESGCM(key).encrypt(nonce, data, AESHandler.MAGIC)
        return AESHandler.MAGIC + nonce + ciphertext, nonce.hex()
    
    @staticmethod
    def decrypt(encrypted_data, hex_key):
        key = AESHandler.key_from_hex(hex_key)
        if len(key) != AESHandler.KEY_SIZE:
            raise ValueError(f"Kalit uzunligi {AESHandler.KEY_SIZE} bayt bo'lishi kerak")

        minimum_size = len(AESHandler.MAGIC) + AESHandler.NONCE_SIZE + 16
        if not encrypted_data.startswith(AESHandler.MAGIC):
            raise ValueError(
                'Eski yoki noma’lum AES formati: autentifikatsiyalangan GCM fayli talab qilinadi.'
            )
        if len(encrypted_data) < minimum_size:
            raise ValueError('Shifrlangan ma’lumot to‘liq emas yoki buzilgan.')

        nonce_start = len(AESHandler.MAGIC)
        nonce_end = nonce_start + AESHandler.NONCE_SIZE
        nonce = encrypted_data[nonce_start:nonce_end]
        try:
            return AESGCM(key).decrypt(
                nonce,
                encrypted_data[nonce_end:],
                AESHandler.MAGIC,
            )
        except InvalidTag as exc:
            raise ValueError('Kalit noto‘g‘ri yoki fayl buzilgan.') from exc
    
    @staticmethod
    def get_info():
        """Algoritm haqida ma'lumot"""
        return {
            'name': 'AES-256-GCM',
            'key_size': AESHandler.KEY_SIZE * 8,  # bit
            'block_size': AESHandler.BLOCK_SIZE * 8,
            'nonce_size': AESHandler.NONCE_SIZE * 8,
            'mode': 'GCM',
            'description': 'AES-256-GCM authenticated encryption'
        }
