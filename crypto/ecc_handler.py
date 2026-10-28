"""
ECC (Elliptic Curve Cryptography) - ECIES hybrid shifrlash
"""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import struct

class ECCHandler:
    CURVE = ec.SECP256R1()  # P-256
    KEY_SIZE = 32  # AES-256
    BLOCK_SIZE = 16
    
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
            bytes: ephemeral_public_key + iv + encrypted_data
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
        
        # AES-256-CBC bilan shifrlash
        iv = get_random_bytes(ECCHandler.BLOCK_SIZE)
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        padded_data = pad(data, ECCHandler.BLOCK_SIZE)
        encrypted_data = cipher.encrypt(padded_data)
        
        # Ephemeral public key'ni serialize qilish
        ephemeral_public_bytes = ephemeral_public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )
        
        # Natija: [ephemeral_pub_key_len(2)] + ephemeral_pub_key + iv + encrypted_data
        result = struct.pack('H', len(ephemeral_public_bytes))
        result += ephemeral_public_bytes
        result += iv
        result += encrypted_data
        
        return result
    
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
        
        # Ephemeral public key'ni ajratish
        offset = 0
        ephemeral_pub_len = struct.unpack('H', encrypted_data[offset:offset+2])[0]
        offset += 2
        
        ephemeral_public_bytes = encrypted_data[offset:offset+ephemeral_pub_len]
        offset += ephemeral_pub_len
        
        # Ephemeral public key'ni deserialize qilish
        ephemeral_public_key = ec.EllipticCurvePublicKey.from_encoded_point(
            ECCHandler.CURVE,
            ephemeral_public_bytes
        )
        
        # ECDH: shared secret hisoblash
        shared_key = private_key.exchange(
            ec.ECDH(),
            ephemeral_public_key
        )
        
        # KDF: AES kalitni hosil qilish
        aes_key = HKDF(
            algorithm=hashes.SHA256(),
            length=ECCHandler.KEY_SIZE,
            salt=None,
            info=b'encryption',
            backend=default_backend()
        ).derive(shared_key)
        
        # IV va ciphertext ajratish
        iv = encrypted_data[offset:offset+ECCHandler.BLOCK_SIZE]
        offset += ECCHandler.BLOCK_SIZE
        ciphertext = encrypted_data[offset:]
        
        # AES bilan deshifrlash
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        decrypted_padded = cipher.decrypt(ciphertext)
        
        try:
            decrypted_data = unpad(decrypted_padded, ECCHandler.BLOCK_SIZE)
            return decrypted_data
        except ValueError:
            raise ValueError("❌ Private key noto'g'ri yoki fayl buzilgan.")
    
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
