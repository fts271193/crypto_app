"""
ECC (Elliptic Curve Cryptography) - ECIES hybrid shifrlash
"""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
from Crypto.Random import get_random_bytes
import struct

class ECCHandler:
    CURVE = ec.SECP256R1()  # P-256
    KEY_SIZE = 32  # AES-256
    NONCE_SIZE = 12
    MAGIC = b'ECC1'
    
    @staticmethod
    def generate_keypair():
        """
        ECC kalit juftligini yaratish
        Returns:
            tuple: (private_key_pem, public_key_pem)
        """
        # Private key generatsiya
        private_key = ec.generate_private_key(
            ECCHandler.CURVE,
            default_backend()
        )
        
        # Public key olish
        public_key = private_key.public_key()
        
        # PEM formatga o'tkazish
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        return private_pem, public_pem
    
    @staticmethod
    def load_public_key(pem_data):
        """PEM formatdan public key yuklash"""
        try:
            if isinstance(pem_data, str):
                pem_data = pem_data.encode('utf-8')
            
            public_key = serialization.load_pem_public_key(
                pem_data,
                backend=default_backend()
            )
            return public_key
        except Exception as e:
            raise ValueError(f"Public key yuklashda xatolik: {e}")
    
    @staticmethod
    def load_private_key(pem_data):
        """PEM formatdan private key yuklash"""
        try:
            if isinstance(pem_data, str):
                pem_data = pem_data.encode('utf-8')
            
            private_key = serialization.load_pem_private_key(
                pem_data,
                password=None,
                backend=default_backend()
            )
            return private_key
        except Exception as e:
            raise ValueError(f"Private key yuklashda xatolik: {e}")
    
    @staticmethod
    def encrypt(data, public_key_pem):
        """
        ECIES hybrid shifrlash
        1. Ephemeral ECC kalit juftligini yaratish
        2. ECDH bilan shared secret hisoblash
        3. Shared secret'dan AES kalit hosil qilish
        4. AES bilan ma'lumotni shifrlash
        
        Args:
            data: bytes - shifrlash uchun ma'lumot
            public_key_pem: str - public key (PEM format)
        Returns:
            bytes: version marker + ephemeral key + nonce + authenticated ciphertext
        """
        # Recipient public key yuklash
        recipient_public_key = ECCHandler.load_public_key(public_key_pem)
        
        # Ephemeral kalit juftligini yaratish
        ephemeral_private_key = ec.generate_private_key(
            ECCHandler.CURVE,
            default_backend()
        )
        ephemeral_public_key = ephemeral_private_key.public_key()
        
        # ECDH: shared secret hisoblash
        shared_key = ephemeral_private_key.exchange(
            ec.ECDH(),
            recipient_public_key
        )
        
        # KDF: AES kalitni hosil qilish
        aes_key = HKDF(
            algorithm=hashes.SHA256(),
            length=ECCHandler.KEY_SIZE,
            salt=None,
            info=b'encryption',
            backend=default_backend()
        ).derive(shared_key)
        
        # Ephemeral public key'ni serialize qilish
        ephemeral_public_bytes = ephemeral_public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )
        nonce = get_random_bytes(ECCHandler.NONCE_SIZE)
        header = ECCHandler.MAGIC + struct.pack('>H', len(ephemeral_public_bytes)) + ephemeral_public_bytes
        ciphertext = AESGCM(aes_key).encrypt(nonce, data, ECCHandler.MAGIC)
        return header + nonce + ciphertext
    
    @staticmethod
    def decrypt(encrypted_data, private_key_pem):
        """
        ECIES hybrid deshifrlash
        
        Args:
            encrypted_data: bytes - shifrlangan ma'lumot
            private_key_pem: str - private key (PEM format)
        Returns:
            bytes: deshifrlangan ma'lumot
        """
        # Private key yuklash
        private_key = ECCHandler.load_private_key(private_key_pem)

        if not isinstance(private_key, ec.EllipticCurvePrivateKey):
            raise ValueError('ECC private key talab qilinadi.')

        if not encrypted_data.startswith(ECCHandler.MAGIC):
            raise ValueError(
                'Eski yoki noma’lum ECC format: autentifikatsiyalangan GCM fayli talab qilinadi.'
            )
        if len(encrypted_data) < 6:
            raise ValueError('ECC shifrlangan fayl formati noto‘g‘ri.')
        ephemeral_pub_len = struct.unpack('>H', encrypted_data[4:6])[0]
        offset = 6 + ephemeral_pub_len
        if len(encrypted_data) < offset + ECCHandler.NONCE_SIZE + 16:
            raise ValueError('ECC shifrlangan fayl to‘liq emas.')
        ephemeral_public_bytes = encrypted_data[6:offset]
        ephemeral_public_key = ec.EllipticCurvePublicKey.from_encoded_point(
            private_key.curve,
            ephemeral_public_bytes
        )
        shared_key = private_key.exchange(ec.ECDH(), ephemeral_public_key)
        aes_key = HKDF(
            algorithm=hashes.SHA256(),
            length=ECCHandler.KEY_SIZE,
            salt=None,
            info=b'encryption',
            backend=default_backend()
        ).derive(shared_key)
        nonce = encrypted_data[offset:offset + ECCHandler.NONCE_SIZE]
        ciphertext = encrypted_data[offset + ECCHandler.NONCE_SIZE:]
        try:
            return AESGCM(aes_key).decrypt(nonce, ciphertext, ECCHandler.MAGIC)
        except InvalidTag as exc:
            raise ValueError('Private key noto‘g‘ri yoki fayl buzilgan.') from exc
    
    @staticmethod
    def get_info():
        """Algoritm haqida ma'lumot"""
        return {
            'name': 'ECIES (ECC + AES-256)',
            'curve': 'secp256r1 (P-256)',
            'key_size': 256,  # bit
            'protocol': 'Elliptic Curve Integrated Encryption Scheme',
            'description': 'Hybrid: ECC asimmetrik + AES simmetrik shifrlash'
        }
