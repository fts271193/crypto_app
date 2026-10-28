#!/usr/bin/env python3
"""
DEMO SKRIPT - Dasturning asosiy funksiyalarini ko'rsatish
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from crypto.aes_handler import AESHandler
from crypto.ecc_handler import ECCHandler
from utils.file_manager import FileManager
from utils.metrics import Timer
import time


def print_header(text):
    """Sarlavha chiqarish"""
    print("\n" + "="*70)
    print(f" {text}")
    print("="*70)


def demo_aes():
    """AES demo"""
    print_header("DEMO 1: AES-256 SHIFRLASH")
    
    print("\n📝 1. Test fayl yaratish...")
    test_data = """
Bu test fayli.
AES-256-GCM algoritmi bilan shifrlanadi.
Kalit uzunligi: 256 bit (64 hex belgi)
    """.strip()
    
    with open("demo_test.txt", "w") as f:
        f.write(test_data)
    print(f"   ✓ Yaratildi: demo_test.txt ({len(test_data)} bayt)")
    time.sleep(1)
    
    print("\n🔑 2. AES-256 kalit generatsiya...")
    key = AESHandler.generate_key()
    print(f"   ✓ Kalit: {key[:32]}...{key[-16:]}")
    time.sleep(1)
    
    print("\n📂 3. Faylni o'qish...")
    fm = FileManager()
    file_data = fm.read_file("demo_test.txt")
    print(f"   ✓ O'qildi: {len(file_data)} bayt")
    time.sleep(1)
    
    print("\n🔐 4. Shifrlash jarayoni...")
    with Timer() as t:
        encrypted_data, iv = AESHandler.encrypt(file_data, key)
    print(f"   ✓ Shifrlandi: {t.get_elapsed():.6f} soniya")
    print(f"   ✓ IV: {iv}")
    print(f"   ✓ Shifrlangan hajm: {len(encrypted_data)} bayt")
    time.sleep(1)
    
    print("\n💾 5. Shifrlangan faylni saqlash...")
    fm.write_file("demo_test.txt.encrypted", encrypted_data)
    print("   ✓ Saqlandi: demo_test.txt.encrypted")
    time.sleep(1)
    
    print("\n🔓 6. Deshifrlash jarayoni...")
    with Timer() as t:
        decrypted_data = AESHandler.decrypt(encrypted_data, key)
    print(f"   ✓ Deshifrlandi: {t.get_elapsed():.6f} soniya")
    time.sleep(1)
    
    print("\n💾 7. Deshifrlangan faylni saqlash...")
    fm.write_file("demo_test.txt.decrypted", decrypted_data)
    print("   ✓ Saqlandi: demo_test.txt.decrypted")
    time.sleep(1)
    
    print("\n✅ 8. Validatsiya...")
    if decrypted_data == file_data:
        print("   ✓ MUVAFFAQIYAT: Asl va deshifrlangan fayllar bir xil!")
    else:
        print("   ✗ XATO: Fayllar mos kelmadi!")
    
    print("\n" + "="*70)
    print(" AES DEMO TUGADI")
    print("="*70)


def demo_ecc():
    """ECC demo"""
    print_header("DEMO 2: ECC (ECIES) SHIFRLASH")
    
    handler = ECCHandler()
    
    print("\n🔑 1. ECC kalit juftligini yaratish...")
    with Timer() as t:
        private_pem, public_pem = handler.generate_keypair()
    print(f"   ✓ Vaqt: {t.get_elapsed():.6f} soniya")
    print(f"   ✓ Public key: {len(public_pem)} belgi")
    print(f"   ✓ Private key: {len(private_pem)} belgi")
    time.sleep(1)
    
    print("\n💾 2. Kalitlarni saqlash...")
    with open("demo_public.pem", "w") as f:
        f.write(public_pem)
    with open("demo_private.pem", "w") as f:
        f.write(private_pem)
    print("   ✓ Saqlandi: demo_public.pem, demo_private.pem")
    time.sleep(1)
    
    print("\n📝 3. Test ma'lumot...")
    test_data = b"ECC hybrid shifrlash - Public key bilan shifrlash, Private key bilan deshifrlash"
    print(f"   ✓ Hajm: {len(test_data)} bayt")
    time.sleep(1)
    
    print("\n🔐 4. Public key bilan shifrlash...")
    with Timer() as t:
        encrypted_data = handler.encrypt(test_data, public_pem)
    print(f"   ✓ Vaqt: {t.get_elapsed():.6f} soniya")
    print(f"   ✓ Shifrlangan hajm: {len(encrypted_data)} bayt")
    time.sleep(1)
    
    print("\n🔓 5. Private key bilan deshifrlash...")
    with Timer() as t:
        decrypted_data = handler.decrypt(encrypted_data, private_pem)
    print(f"   ✓ Vaqt: {t.get_elapsed():.6f} soniya")
    time.sleep(1)
    
    print("\n✅ 6. Validatsiya...")
    if decrypted_data == test_data:
        print("   ✓ MUVAFFAQIYAT: Ma'lumot to'g'ri tiklandi!")
    else:
        print("   ✗ XATO: Ma'lumot mos kelmadi!")
    
    print("\n" + "="*70)
    print(" ECC DEMO TUGADI")
    print("="*70)


def main():
    """Asosiy demo"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*20 + "FAYL SHIFRLASH DASTURI" + " "*26 + "║")
    print("║" + " "*28 + "DEMO" + " "*36 + "║")
    print("╚" + "="*68 + "╝")
    
    input("\nDavom etish uchun Enter bosing...")
    
    # AES demo
    demo_aes()
    
    input("\n\nKeyingi demoga o'tish uchun Enter bosing...")
    
    # ECC demo
    demo_ecc()
    
    print("\n\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*22 + "DEMO YAKUNLANDI" + " "*31 + "║")
    print("║" + " "*68 + "║")
    print("║" + "  Yaratilgan fayllar:" + " "*47 + "║")
    print("║" + "    • demo_test.txt.encrypted" + " "*40 + "║")
    print("║" + "    • demo_test.txt.decrypted" + " "*40 + "║")
    print("║" + "    • demo_public.pem" + " "*49 + "║")
    print("║" + "    • demo_private.pem" + " "*48 + "║")
    print("╚" + "="*68 + "╝")
    print("\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo to'xtatildi.\n")
    except Exception as e:
        print(f"\n❌ Xato: {e}\n")
        import traceback
        traceback.print_exc()
