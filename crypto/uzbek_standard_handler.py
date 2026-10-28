"""Adapter for the O'z DSt 1105:2009 block cipher implementation."""
from Crypto.Random import get_random_bytes

from crypto.ozdst1105 import BLOCK, OzDSt1105
from crypto.authenticated_cbc import AuthenticatedCBC


class UzbekStandardHandler:
    KEY_SIZE = 64
    BLOCK_SIZE = BLOCK
    MAGIC = b'OZD1'

    @staticmethod
    def generate_key():
        return get_random_bytes(UzbekStandardHandler.KEY_SIZE).hex()

    @staticmethod
    def key_from_hex(hex_key):
        try:
            key = bytes.fromhex(hex_key)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Kalit hex formatida bo'lishi kerak: {exc}") from exc
        if len(key) != UzbekStandardHandler.KEY_SIZE:
            raise ValueError('O‘z DSt 1105 uchun k || kf kaliti 64 bayt (128 hex belgi) bo‘lishi kerak.')
        return key

    @classmethod
    def encrypt(cls, data, hex_key):
        key = cls.key_from_hex(hex_key)
        iv = get_random_bytes(cls.BLOCK_SIZE)
        ciphertext = OzDSt1105(key).encrypt(data, mode='cbc', iv=iv, padding='pkcs7')
        envelope = AuthenticatedCBC.pack(
            cls.MAGIC, key, iv, ciphertext
        )
        return envelope, iv.hex()

    @classmethod
    def decrypt(cls, encrypted_data, hex_key):
        key = cls.key_from_hex(hex_key)
        iv, ciphertext = AuthenticatedCBC.unpack(
            encrypted_data,
            cls.MAGIC,
            key,
            cls.BLOCK_SIZE,
            cls.BLOCK_SIZE,
        )
        return OzDSt1105(key).decrypt(ciphertext, mode='cbc', iv=iv, padding='pkcs7')

    @staticmethod
    def get_info():
        return {
            'name': "O'z DSt 1105:2009",
            'key_size': 512,
            'block_size': 256,
            'mode': 'CBC + HMAC-SHA-256',
            'description': 'O‘zbekiston milliy blok shifri; k va kf kalitlari birlashtirilgan.',
        }
