import unittest

import gostcrypto

from crypto.gost_handler import GOSTHandler


class GOSTHandlerTests(unittest.TestCase):
    def test_kuznechik_known_answer_vector(self):
        key = bytes.fromhex(
            '8899aabbccddeeff0011223344556677'
            'fedcba98765432100123456789abcdef'
        )
        plaintext = bytes.fromhex('1122334455667700ffeeddccbbaa9988')
        expected = bytes.fromhex('7f679d90bebc24305a468d42b9d4edcd')
        cipher = gostcrypto.gostcipher.GOST34122015Kuznechik(bytearray(key))

        self.assertEqual(bytes(cipher.encrypt(bytearray(plaintext))), expected)

    def test_encrypt_decrypt_round_trip_for_various_lengths(self):
        key = GOSTHandler.generate_key()
        for size in (0, 1, 15, 16, 17, 32, 257):
            with self.subTest(size=size):
                plaintext = bytes(index % 256 for index in range(size))
                encrypted, iv_hex = GOSTHandler.encrypt(plaintext, key)

                self.assertEqual(len(bytes.fromhex(iv_hex)), GOSTHandler.BLOCK_SIZE)
                iv_start = len(GOSTHandler.MAGIC)
                self.assertEqual(encrypted[:iv_start], GOSTHandler.MAGIC)
                self.assertEqual(
                    encrypted[iv_start:iv_start + GOSTHandler.BLOCK_SIZE].hex(),
                    iv_hex,
                )
                self.assertEqual(
                    GOSTHandler.decrypt(encrypted, key),
                    plaintext,
                )

    def test_decrypt_rejects_truncated_ciphertext(self):
        with self.assertRaisesRegex(ValueError, 'buzilgan'):
            GOSTHandler.decrypt(
                GOSTHandler.MAGIC + b'\x00' * (GOSTHandler.BLOCK_SIZE * 2 - 1),
                '00' * GOSTHandler.KEY_SIZE,
            )

    def test_decrypt_rejects_tampering(self):
        key = GOSTHandler.generate_key()
        encrypted, _ = GOSTHandler.encrypt(b'authentic data', key)
        changed = bytearray(encrypted)
        changed[-1] ^= 1
        with self.assertRaisesRegex(ValueError, 'buzilgan'):
            GOSTHandler.decrypt(bytes(changed), key)


if __name__ == '__main__':
    unittest.main()
