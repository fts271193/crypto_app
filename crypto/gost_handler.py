"""
GOST Kuznechik (GOST R 34.12-2015) CBC shifrlash va deshifrlash.
"""
import binascii
import secrets

import gostcrypto

from crypto.authenticated_cbc import AuthenticatedCBC


class GOSTHandler:
    """GOST Kuznechik handler."""

    KEY_SIZE = 32
    BLOCK_SIZE = 16
    MAGIC = b'GOST1'

    @staticmethod
    def generate_key():
        """Tasodifiy 256-bit kalitni hex formatda generatsiya qilish."""
        return secrets.token_bytes(GOSTHandler.KEY_SIZE).hex()

    @staticmethod
    def key_from_hex(hex_key):
        """Hex string'dan kalit olish."""
        try:
            return binascii.unhexlify(hex_key)
        except (binascii.Error, ValueError) as exc:
            raise ValueError(f"Noto'g'ri hex format: {exc}") from exc

    @staticmethod
    def _new_cipher(key, iv):
        return gostcrypto.gostcipher.new(
            'kuznechik',
            bytearray(key),
            gostcrypto.gostcipher.MODE_CBC,
            init_vect=bytearray(iv),
            pad_mode=gostcrypto.gostcipher.PAD_MODE_2,
        )

    @staticmethod
    def _remove_padding(data):
        marker = data.rfind(b'\x80')
        if marker < 0 or any(data[marker + 1:]):
            raise ValueError("Noto'g'ri padding")
        return data[:marker]

    @staticmethod
    def encrypt(data, hex_key):
        """
        Ma'lumotni Kuznechik-CBC bilan shifrlash.

        Returns:
            tuple: (authenticated envelope, IV hex)
        """
        key = GOSTHandler.key_from_hex(hex_key)
        if len(key) != GOSTHandler.KEY_SIZE:
            raise ValueError(
                f"Kalit uzunligi {GOSTHandler.KEY_SIZE} bayt bo'lishi kerak"
            )

        iv = secrets.token_bytes(GOSTHandler.BLOCK_SIZE)
        cipher = GOSTHandler._new_cipher(key, iv)
        encrypted_data = bytes(cipher.encrypt(bytearray(data)))
        envelope = AuthenticatedCBC.pack(
            GOSTHandler.MAGIC, key, iv, encrypted_data
        )
        return envelope, iv.hex()

    @staticmethod
    def decrypt(encrypted_data, hex_key):
        """Authenticate and decrypt a Kuznechik-CBC envelope."""
        key = GOSTHandler.key_from_hex(hex_key)
        if len(key) != GOSTHandler.KEY_SIZE:
            raise ValueError(
                f"Kalit uzunligi {GOSTHandler.KEY_SIZE} bayt bo'lishi kerak"
            )
        iv, ciphertext = AuthenticatedCBC.unpack(
            encrypted_data,
            GOSTHandler.MAGIC,
            key,
            GOSTHandler.BLOCK_SIZE,
            GOSTHandler.BLOCK_SIZE,
        )

        cipher = GOSTHandler._new_cipher(key, iv)
        try:
            decrypted_data = bytes(cipher.decrypt(bytearray(ciphertext)))
            return GOSTHandler._remove_padding(decrypted_data)
        except (ValueError, gostcrypto.gostcipher.GOSTCipherError) as exc:
            raise ValueError("Kalit noto'g'ri yoki fayl buzilgan.") from exc

    @staticmethod
    def get_info():
        """Algoritm haqida ma'lumot."""
        return {
            'name': 'GOST Kuznechik',
            'key_size': GOSTHandler.KEY_SIZE * 8,
            'block_size': GOSTHandler.BLOCK_SIZE * 8,
            'mode': 'CBC + HMAC-SHA-256',
            'standard': 'GOST R 34.12-2015',
            'description': 'GOST Kuznechik-CBC with HMAC-SHA-256 integrity protection',
        }
