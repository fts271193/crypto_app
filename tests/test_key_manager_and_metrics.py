import csv
import json
import os
import tempfile
import unittest
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad

from utils.key_manager import KeyManager
from utils.metrics import PerformanceMetrics
from utils.validator import Validator


class KeyManagerTests(unittest.TestCase):
    def test_key_store_uses_authenticated_encryption_and_unique_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            manager = KeyManager(directory)
            manager.add_key('AES', 'a' * 64, 'AES kalit')
            manager.add_key('AES', 'b' * 64, 'AES kalit')

            entries = manager.get_recent_keys('AES', 10)
            self.assertEqual(entries[0]['key'], 'b' * 64)
            self.assertNotEqual(entries[0]['id'], entries[1]['id'])
            self.assertEqual(
                manager.keys_file.read_bytes()[:len(manager.STORE_MARKER)],
                manager.STORE_MARKER,
            )

            contents = bytearray(manager.keys_file.read_bytes())
            contents[-1] ^= 1
            manager.keys_file.write_bytes(contents)
            with self.assertRaisesRegex(ValueError, 'buzilgan'):
                manager.load_keys()

            if os.name == 'nt':
                stored_master = (Path(directory) / '.master').read_bytes()
                self.assertTrue(stored_master.startswith(manager.MASTER_MARKER))
                self.assertNotEqual(stored_master, manager.master_key)

    def test_legacy_key_store_is_migrated_to_authenticated_format(self):
        with tempfile.TemporaryDirectory() as directory:
            manager = KeyManager(directory)
            old_keys = {'AES': [{'key': 'c' * 64, 'label': 'old', 'date': '2026-01-01'}]}
            cipher = AES.new(manager.master_key, AES.MODE_CBC)
            old_envelope = cipher.iv + cipher.encrypt(
                pad(json.dumps(old_keys).encode('utf-8'), AES.block_size)
            )
            manager.keys_file.write_bytes(old_envelope)

            self.assertEqual(manager.load_keys()['AES'][0]['label'], 'old')
            self.assertTrue(
                manager.keys_file.read_bytes().startswith(manager.STORE_MARKER)
            )

    def test_legacy_plain_master_key_is_protected_on_windows(self):
        if os.name != 'nt':
            self.skipTest('Windows DPAPI sinovi Windows tizimida bajariladi.')
        with tempfile.TemporaryDirectory() as directory:
            master_key = get_random_bytes(32)
            Path(directory, '.master').write_bytes(master_key)
            legacy_keys = {
                'AES': [{'key': 'd' * 64, 'label': 'saved', 'date': '2026-01-01'}]
            }
            cipher = AES.new(master_key, AES.MODE_CBC)
            legacy_store = cipher.iv + cipher.encrypt(
                pad(json.dumps(legacy_keys).encode('utf-8'), AES.block_size)
            )
            Path(directory, 'keys.json.enc').write_bytes(legacy_store)

            manager = KeyManager(directory)
            protected_master = Path(directory, '.master').read_bytes()

            self.assertTrue(protected_master.startswith(manager.MASTER_MARKER))
            self.assertNotEqual(protected_master, master_key)
            self.assertEqual(manager.master_key, master_key)
            self.assertEqual(manager.get_recent_keys('AES')[0]['key'], 'd' * 64)
            self.assertTrue(
                manager.keys_file.read_bytes().startswith(manager.STORE_MARKER)
            )


class PerformanceMetricsTests(unittest.TestCase):
    def test_operation_statistics_exclude_file_io_and_export_csv(self):
        metrics = PerformanceMetrics()
        metrics.file_size = 1024 * 1024
        metrics.read_time = 20.0
        metrics.write_time = 30.0
        metrics.record_operation_times([0.1, 0.2, 0.3, 0.4, 0.5], 'encrypt')

        self.assertAlmostEqual(metrics.encrypt_time, 0.3)
        self.assertAlmostEqual(metrics.operation_std, (0.02) ** 0.5)
        self.assertAlmostEqual(metrics.speed, 1 / 0.3)

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'metrics.csv'
            metrics.export_to_csv(path)
            with path.open(encoding='utf-8-sig', newline='') as csv_file:
                row = next(csv.DictReader(csv_file))
            self.assertEqual(row['Takrorlar'], '5')
            self.assertEqual(float(row['Kripto tezligi(MB/s)']), metrics.speed)


class ValidationTests(unittest.TestCase):
    def test_invalid_gost_key_returns_validation_error(self):
        valid, error = Validator.validate_key('0' * 62, 'GOST Kuznechik')
        self.assertFalse(valid)
        self.assertIn('64 hex belgi', error)


if __name__ == '__main__':
    unittest.main()
