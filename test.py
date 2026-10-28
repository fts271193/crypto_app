#!/usr/bin/env python3
"""
Test skripti - barcha kriptografik algoritmlarni test qilish
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from crypto.aes_handler import AESHandler
from crypto.des_handler import DESHandler
from crypto.gost_handler import GOSTHandler
from crypto.ecc_handler import ECCHandler
from utils.file_manager import FileManager
from utils.metrics import Timer


def test_symmetric(algorithm_name, handler_class):
    """Simmetrik algoritmni test qilish"""
    print(f"\n{'='*60}")
    print(f"TEST: {algorithm_name}")
    print(f"{'='*60}")
    
    try:
        # 1. Kalit generatsiya
        print("\n1. Kalit generatsiya...")
        key = handler_class.generate_key()
        print(f"   ✓ Kalit: {key[:32]}... ({len(key)} belgi)")
        
        # 2. Test ma'lumot
        test_data = b"Bu test ma'lumoti. Shifrlash va deshifrlash test qilinmoqda."
        print(f"\n2. Test ma'lumot: {len(test_data)} bayt")
        
        # 3. Shifrlash
        print("\n3. Shifrlash...")
        with Timer() as t:
            encrypted_data, iv = handler_class.encrypt(test_data, key)
        print(f"   ✓ Shifrlandi: {t.get_elapsed():.6f} s")
        print(f"   ✓ IV: {iv}")
        print(f"   ✓ Hajm: {len(encrypted_data)} bayt")
        
        # 4. Deshifrlash
        print("\n4. Deshifrlash...")
        with Timer() as t:
            decrypted_data = handler_class.decrypt(encrypted_data, key)
        print(f"   ✓ Deshifrlandi: {t.get_elapsed():.6f} s")
        
        # 5. Validatsiya
        print("\n5. Validatsiya...")
        if decrypted_data == test_data:
            print("   ✅ MUVAFFAQIYAT: Ma'lumot to'g'ri tiklandi!")
        else:
            print("   ❌ XATO: Ma'lumot mos kelmadi!")
            return False
        
        # 6. Fayl test
        print("\n6. Fayl bilan test...")
        file_manager = FileManager()
        
        # Test faylini yaratish
        test_file = "test.txt"
        with open(test_file, 'wb') as f:
            f.write(test_data)
        
        # Faylni o'qish
        file_data = file_manager.read_file(test_file)
        print(f"   ✓ Fayl o'qildi: {len(file_data)} bayt")
        
        # Shifrlash
        encrypted_file_data, _ = handler_class.encrypt(file_data, key)
        
        # Shifrlangan faylni saqlash
        encrypted_file = f"test_{algorithm_name.replace(' ', '_')}.encrypted"
        file_manager.write_file(encrypted_file, encrypted_file_data)
        print(f"   ✓ Shifrlangan fayl: {encrypted_file}")
        
        # Deshifrlash
        decrypted_file_data = handler_class.decrypt(encrypted_file_data, key)
        
        # Deshifrlangan faylni saqlash
        decrypted_file = f"test_{algorithm_name.replace(' ', '_')}.decrypted.txt"
        file_manager.write_file(decrypted_file, decrypted_file_data)
        print(f"   ✓ Deshifrlangan fayl: {decrypted_file}")
        
        # Validatsiya
        if decrypted_file_data == file_data:
            print("   ✅ FAYL TESTI MUVAFFAQIYATLI!")
        else:
            print("   ❌ FAYL TESTI MUVAFFAQIYATSIZ!")
            return False
        
        print(f"\n{'='*60}")
        print(f"✅ {algorithm_name} - BARCHA TESTLAR O'TDI!")
        print(f"{'='*60}")
        return True
        
    except Exception as e:
        print(f"\n❌ XATO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_ecc():
    """ECC algoritmni test qilish"""
    print(f"\n{'='*60}")
    print(f"TEST: ECC (ECIES)")
    print(f"{'='*60}")
    
    try:
        handler = ECCHandler()
        
        # 1. Kalit juftligi generatsiya
        print("\n1. Kalit juftligi generatsiya...")
        with Timer() as t:
            private_pem, public_pem = handler.generate_keypair()
        print(f"   ✓ Vaqt: {t.get_elapsed():.6f} s")
        print(f"   ✓ Public key: {len(public_pem)} bayt")
        print(f"   ✓ Private key: {len(private_pem)} bayt")
        
        # 2. Test ma'lumot
        test_data = b"ECC hybrid shifrlash testi. ECIES protokoli."
        print(f"\n2. Test ma'lumot: {len(test_data)} bayt")
        
        # 3. Shifrlash
        print("\n3. Shifrlash...")
        with Timer() as t:
            encrypted_data = handler.encrypt(test_data, public_pem)
        print(f"   ✓ Shifrlandi: {t.get_elapsed():.6f} s")
        print(f"   ✓ Hajm: {len(encrypted_data)} bayt")
        
        # 4. Deshifrlash
        print("\n4. Deshifrlash...")
        with Timer() as t:
            decrypted_data = handler.decrypt(encrypted_data, private_pem)
        print(f"   ✓ Deshifrlandi: {t.get_elapsed():.6f} s")
        
        # 5. Validatsiya
        print("\n5. Validatsiya...")
        if decrypted_data == test_data:
            print("   ✅ MUVAFFAQIYAT: Ma'lumot to'g'ri tiklandi!")
        else:
            print("   ❌ XATO: Ma'lumot mos kelmadi!")
            return False
        
        # 6. Fayl test
        print("\n6. Fayl bilan test...")
        file_manager = FileManager()
        
        test_file = "test.txt"
        file_data = file_manager.read_file(test_file)
        
        # Shifrlash
        encrypted_file_data = handler.encrypt(file_data, public_pem)
        encrypted_file = "test_ECC.encrypted"
        file_manager.write_file(encrypted_file, encrypted_file_data)
        print(f"   ✓ Shifrlangan fayl: {encrypted_file}")
        
        # Deshifrlash
        decrypted_file_data = handler.decrypt(encrypted_file_data, private_pem)
        decrypted_file = "test_ECC.decrypted.txt"
        file_manager.write_file(decrypted_file, decrypted_file_data)
        print(f"   ✓ Deshifrlangan fayl: {decrypted_file}")
        
        # Kalitlarni saqlash
        with open("test_public.pem", 'w') as f:
            f.write(public_pem)
        with open("test_private.pem", 'w') as f:
            f.write(private_pem)
        print(f"   ✓ Kalitlar saqlandi: test_public.pem, test_private.pem")
        
        print(f"\n{'='*60}")
        print(f"✅ ECC - BARCHA TESTLAR O'TDI!")
        print(f"{'='*60}")
        return True
        
    except Exception as e:
        print(f"\n❌ XATO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Asosiy test funksiyasi"""
    print("\n" + "="*60)
    print(" KRIPTOGRAFIK ALGORITMLAR TEST DASTURI")
    print("="*60)
    
    results = []
    
    # AES test
    results.append(("AES-256", test_symmetric("AES-256", AESHandler)))
    
    # DES test
    results.append(("DES", test_symmetric("DES", DESHandler)))
    
    # GOST test
    results.append(("GOST Kuznechik", test_symmetric("GOST Kuznechik", GOSTHandler)))
    
    # ECC test
    results.append(("ECC", test_ecc()))
    
    # Natijalar
    print("\n" + "="*60)
    print(" TEST NATIJALARI")
    print("="*60)
    
    for algo, success in results:
        status = "✅ O'TDI" if success else "❌ MUVAFFAQIYATSIZ"
        print(f"{algo:20} : {status}")
    
    print("="*60)
    
    all_passed = all(result[1] for result in results)
    if all_passed:
        print("\n🎉 BARCHA TESTLAR MUVAFFAQIYATLI O'TDI!")
        return 0
    else:
        print("\n⚠️  BA'ZI TESTLAR MUVAFFAQIYATSIZ!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
