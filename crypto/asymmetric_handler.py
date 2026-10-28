"""RSA, ElGamal va DSA amallari."""
import base64
import json
import secrets
import textwrap

from Crypto.PublicKey import ElGamal
from Crypto.Random import get_random_bytes
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import dh, dsa, padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class AsymmetricHandler:
    RSA_BITS = 3072
    ELGAMAL_BITS = 2048
    DSA_BITS = 2048
    AES_KEY_SIZE = 32
    NONCE_SIZE = 12

    @classmethod
    def generate_keypair(cls, algorithm):
        if algorithm == 'RSA':
            private_key = rsa.generate_private_key(public_exponent=65537, key_size=cls.RSA_BITS)
            private_pem, public_pem = cls._serialize_crypto_keypair(private_key)
        elif algorithm == 'DSA':
            private_key = dsa.generate_private_key(key_size=cls.DSA_BITS)
            private_pem, public_pem = cls._serialize_crypto_keypair(private_key)
        elif algorithm == 'ElGamal':
            parameters = dh.generate_parameters(generator=2, key_size=cls.ELGAMAL_BITS).parameter_numbers()
            p, g = parameters.p, parameters.g
            x = secrets.randbelow(p - 3) + 2
            key = ElGamal.construct((p, g, pow(g, x, p), x))
            private_pem = cls._serialize_elgamal(key, include_private=True)
            public_pem = cls._serialize_elgamal(key.publickey(), include_private=False)
        else:
            raise ValueError(f'Noma’lum algoritm: {algorithm}')
        return private_pem, public_pem

    @staticmethod
    def _serialize_crypto_keypair(private_key):
        private_pem = private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ).decode('ascii')
        public_pem = private_key.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode('ascii')
        return private_pem, public_pem

    @staticmethod
    def _serialize_elgamal(key, include_private):
        values = {'p': format(int(key.p), 'x'), 'g': format(int(key.g), 'x'), 'y': format(int(key.y), 'x')}
        if include_private:
            values['x'] = format(int(key.x), 'x')
        payload = json.dumps(values, separators=(',', ':')).encode('ascii')
        encoded = base64.b64encode(payload).decode('ascii')
        label = 'PRIVATE' if include_private else 'PUBLIC'
        body = '\n'.join(textwrap.wrap(encoded, 64))
        return f'-----BEGIN ELGAMAL {label} KEY-----\n{body}\n-----END ELGAMAL {label} KEY-----\n'

    @staticmethod
    def _load_elgamal(pem_data, private_required):
        if isinstance(pem_data, bytes):
            pem_data = pem_data.decode('ascii')
        label = 'PRIVATE' if private_required else 'PUBLIC'
        begin = f'-----BEGIN ELGAMAL {label} KEY-----'
        end = f'-----END ELGAMAL {label} KEY-----'
        if begin not in pem_data or end not in pem_data:
            raise ValueError(f'ElGamal {label.lower()} kaliti noto‘g‘ri formatda.')
        encoded = ''.join(pem_data.split(begin, 1)[1].split(end, 1)[0].split())
        values = json.loads(base64.b64decode(encoded, validate=True))
        p, g, y = (int(values[name], 16) for name in ('p', 'g', 'y'))
        if p.bit_length() < 2048 or not 1 < g < p or not 1 < y < p:
            raise ValueError('ElGamal kalit parametrlari yaroqsiz.')
        if private_required:
            x = int(values['x'], 16)
            if not 1 < x < p - 1 or pow(g, x, p) != y:
                raise ValueError('ElGamal private key yaroqsiz.')
            return ElGamal.construct((p, g, y, x))
        return ElGamal.construct((p, g, y))

    @classmethod
    def _load_key(cls, pem_data, algorithm, private_required):
        if algorithm == 'ElGamal':
            return cls._load_elgamal(pem_data, private_required)
        if isinstance(pem_data, str):
            pem_data = pem_data.encode('ascii')
        if private_required:
            key = serialization.load_pem_private_key(pem_data, password=None)
        else:
            key = serialization.load_pem_public_key(pem_data)
        expected = rsa.RSAPrivateKey if algorithm == 'RSA' and private_required else None
        if algorithm == 'RSA' and not private_required:
            expected = rsa.RSAPublicKey
        if algorithm == 'DSA' and private_required:
            expected = dsa.DSAPrivateKey
        if algorithm == 'DSA' and not private_required:
            expected = dsa.DSAPublicKey
        if expected is None or not isinstance(key, expected):
            raise ValueError(f'{algorithm} uchun mos kalit tanlanmagan.')
        return key

    @classmethod
    def encrypt(cls, data, public_pem, algorithm):
        public_key = cls._load_key(public_pem, algorithm, private_required=False)
        aes_key = get_random_bytes(cls.AES_KEY_SIZE)
        nonce = get_random_bytes(cls.NONCE_SIZE)

        if algorithm == 'RSA':
            wrapped_key = public_key.encrypt(
                aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
            if len(wrapped_key) > 65535:
                raise ValueError('RSA kalit hajmi qo‘llab-quvvatlanmaydi.')
            header = b'RSA1' + len(wrapped_key).to_bytes(2, 'big') + wrapped_key
        elif algorithm == 'ElGamal':
            p, g, y = int(public_key.p), int(public_key.g), int(public_key.y)
            exponent = secrets.randbelow(p - 2) + 1
            c1 = pow(g, exponent, p)
            shared = pow(y, exponent, p)
            wrapped_key = (int.from_bytes(aes_key, 'big') * shared) % p
            field_size = (p.bit_length() + 7) // 8
            header = b'ELG1' + c1.to_bytes(field_size, 'big') + wrapped_key.to_bytes(field_size, 'big')
        else:
            raise ValueError('DSA shifrlash uchun emas, elektron imzo uchun ishlatiladi.')

        ciphertext = AESGCM(aes_key).encrypt(nonce, data, header[:4])
        return header + nonce + ciphertext

    @classmethod
    def decrypt(cls, encrypted_data, private_pem, algorithm):
        private_key = cls._load_key(private_pem, algorithm, private_required=True)
        if algorithm == 'RSA':
            if not encrypted_data.startswith(b'RSA1') or len(encrypted_data) < 6:
                raise ValueError('RSA shifrlangan fayl formati noto‘g‘ri.')
            wrapped_size = int.from_bytes(encrypted_data[4:6], 'big')
            offset = 6 + wrapped_size
            if len(encrypted_data) < offset + cls.NONCE_SIZE + 16:
                raise ValueError('RSA shifrlangan fayl to‘liq emas.')
            aes_key = private_key.decrypt(
                encrypted_data[6:offset],
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
            marker = b'RSA1'
        elif algorithm == 'ElGamal':
            if not encrypted_data.startswith(b'ELG1'):
                raise ValueError('ElGamal shifrlangan fayl formati noto‘g‘ri.')
            p, x = int(private_key.p), int(private_key.x)
            field_size = (p.bit_length() + 7) // 8
            offset = 4 + 2 * field_size
            if len(encrypted_data) < offset + cls.NONCE_SIZE + 16:
                raise ValueError('ElGamal shifrlangan fayl to‘liq emas.')
            c1 = int.from_bytes(encrypted_data[4:4 + field_size], 'big')
            c2 = int.from_bytes(encrypted_data[4 + field_size:offset], 'big')
            if not 1 <= c1 < p or not 0 <= c2 < p:
                raise ValueError('ElGamal shifrlangan kalit yaroqsiz.')
            shared = pow(c1, x, p)
            aes_key_value = (c2 * pow(shared, -1, p)) % p
            try:
                aes_key = aes_key_value.to_bytes(cls.AES_KEY_SIZE, 'big')
            except OverflowError as exc:
                raise ValueError('ElGamal shifrlangan kalit yaroqsiz.') from exc
            marker = b'ELG1'
        else:
            raise ValueError('DSA shifrlash uchun emas, elektron imzo uchun ishlatiladi.')

        nonce = encrypted_data[offset:offset + cls.NONCE_SIZE]
        ciphertext = encrypted_data[offset + cls.NONCE_SIZE:]
        return AESGCM(aes_key).decrypt(nonce, ciphertext, marker)

    @classmethod
    def sign(cls, data, private_pem):
        private_key = cls._load_key(private_pem, 'DSA', private_required=True)
        return private_key.sign(data, hashes.SHA256())

    @classmethod
    def verify(cls, data, signature, public_pem):
        public_key = cls._load_key(public_pem, 'DSA', private_required=False)
        try:
            public_key.verify(signature, data, hashes.SHA256())
        except InvalidSignature:
            return False
        return True