import unittest

from crypto.aes_handler import AESHandler
from crypto.des_handler import DESHandler
from crypto.ecc_handler import ECCHandler
from crypto.gost_handler import GOSTHandler
from crypto.uzbek_standard_handler import UzbekStandardHandler


class AuthenticatedEncryptionTests(unittest.TestCase):
    PLAINTEXT = b'Integrity must be checked before plaintext is returned.'

    def test_symmetric_handlers_reject_tampering_and_wrong_keys(self):
        for handler in (
            AESHandler,
            DESHandler,
            GOSTHandler,
            UzbekStandardHandler,
        ):
            with self.subTest(handler=handler.__name__):
                key = handler.generate_key()
                encrypted, _ = handler.encrypt(self.PLAINTEXT, key)
                self.assertEqual(handler.decrypt(encrypted, key), self.PLAINTEXT)

                changed = bytearray(encrypted)
                ciphertext_offset = len(handler.MAGIC)
                if handler is AESHandler:
                    ciphertext_offset += handler.NONCE_SIZE
                else:
                    ciphertext_offset += handler.BLOCK_SIZE
                changed[ciphertext_offset] ^= 1
                with self.assertRaises(ValueError):
                    handler.decrypt(bytes(changed), key)

                wrong_key = handler.generate_key()
                with self.assertRaises(ValueError):
                    handler.decrypt(encrypted, wrong_key)

    def test_symmetric_handlers_reject_legacy_unauthenticated_envelopes(self):
        for handler in (
            AESHandler,
            DESHandler,
            GOSTHandler,
            UzbekStandardHandler,
        ):
            with self.subTest(handler=handler.__name__):
                key = handler.generate_key()
                with self.assertRaisesRegex(ValueError, 'Eski yoki noma'):
                    handler.decrypt(b'\x00' * 128, key)

    def test_symmetric_handlers_round_trip_empty_plaintext(self):
        for handler in (
            AESHandler,
            DESHandler,
            GOSTHandler,
            UzbekStandardHandler,
        ):
            with self.subTest(handler=handler.__name__):
                key = handler.generate_key()
                encrypted, _ = handler.encrypt(b'', key)
                self.assertEqual(handler.decrypt(encrypted, key), b'')

    def test_ecc_rejects_tampering_wrong_keys_and_legacy_envelopes(self):
        private_pem, public_pem = ECCHandler.generate_keypair()
        encrypted = ECCHandler.encrypt(self.PLAINTEXT, public_pem)
        self.assertEqual(ECCHandler.decrypt(encrypted, private_pem), self.PLAINTEXT)
        empty_envelope = ECCHandler.encrypt(b'', public_pem)
        self.assertEqual(ECCHandler.decrypt(empty_envelope, private_pem), b'')

        changed = bytearray(encrypted)
        changed[-1] ^= 1
        with self.assertRaisesRegex(ValueError, 'buzilgan'):
            ECCHandler.decrypt(bytes(changed), private_pem)

        other_private_pem, _ = ECCHandler.generate_keypair()
        with self.assertRaisesRegex(ValueError, 'buzilgan'):
            ECCHandler.decrypt(encrypted, other_private_pem)

        with self.assertRaisesRegex(ValueError, 'Eski yoki noma'):
            ECCHandler.decrypt(b'\x00' * 128, private_pem)


if __name__ == '__main__':
    unittest.main()
