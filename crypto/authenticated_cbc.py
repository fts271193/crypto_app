"""Authenticated envelope helpers for CBC-based educational ciphers."""
import hashlib
import hmac


class AuthenticatedCBC:
    TAG_SIZE = hashlib.sha256().digest_size

    @staticmethod
    def _mac_key(key, magic):
        return hmac.new(
            key,
            b'crypto-app-authenticated-cbc-v1:' + magic,
            hashlib.sha256,
        ).digest()

    @classmethod
    def pack(cls, magic, key, iv, ciphertext):
        body = magic + iv + ciphertext
        tag = hmac.new(cls._mac_key(key, magic), body, hashlib.sha256).digest()
        return body + tag

    @classmethod
    def unpack(cls, envelope, magic, key, iv_size, block_size):
        if not envelope.startswith(magic):
            raise ValueError(
                'Eski yoki noma’lum format: autentifikatsiyalangan ciphertext talab qilinadi.'
            )

        minimum_size = len(magic) + iv_size + block_size + cls.TAG_SIZE
        if len(envelope) < minimum_size:
            raise ValueError('Shifrlangan ma’lumot to‘liq emas yoki buzilgan.')

        body, tag = envelope[:-cls.TAG_SIZE], envelope[-cls.TAG_SIZE:]
        expected_tag = hmac.new(
            cls._mac_key(key, magic),
            body,
            hashlib.sha256,
        ).digest()
        if not hmac.compare_digest(tag, expected_tag):
            raise ValueError('Kalit noto‘g‘ri yoki fayl buzilgan.')

        ciphertext_end = len(body)
        iv_start = len(magic)
        ciphertext_start = iv_start + iv_size
        ciphertext = body[ciphertext_start:ciphertext_end]
        if not ciphertext or len(ciphertext) % block_size:
            raise ValueError('Shifrlangan ma’lumot to‘liq emas yoki buzilgan.')

        return body[iv_start:ciphertext_start], ciphertext
