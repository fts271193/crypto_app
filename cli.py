#!/usr/bin/env python3
"""
Fayl Shifrlash Dasturi - CLI Versiya
"""
import os
import sys
from pathlib import Path

# Current directory'ni path'ga qo'shish
sys.path.insert(0, str(Path(__file__).parent))

from crypto.aes_handler import AESHandler
from crypto.des_handler import DESHandler
from crypto.gost_handler import GOSTHandler
from crypto.ecc_handler import ECCHandler
from utils.validator import Validator
from utils.file_manager import FileManager
from utils.metrics import PerformanceMetrics, Timer
from utils.key_manager import KeyManager


def print_banner():
    """Dastur banneri"""
    banner = """
╔═══════════════════════════════════════════════════════╗
║       FAYL SHIFRLASH DASTURI - CLI Versiya           ║
║                  Versiya 1.0                          ║
╚═══════════════════════════════════════════════════════╝
"""
    print(banner)


def print_menu():
    """Asosiy menu"""
    menu = """
┌─────────────────────────────────────────────────┐
│              ASOSIY MENU                        │
├─────────────────────────────────────────────────┤
│  1. AES-256 shifrlash                           │
│  2. DES shifrlash                               │
│  3. GOST Kuznechik shifrlash                    │
│  4. ECC shifrlash                               │
│  5. Faylni deshifrlash                          │
│  6. Kalit generatsiya                           │
│  7. Chiqish                                     │
└─────────────────────────────────────────────────┘
"""
    print(menu)


def symmetric_encrypt(algorithm_name, handler_class):
    """Simmetrik shifrlash"""
    print(f"\n{'='*60}")
    print(f" {algorithm_name} SHIFRLASH")
    print(f"{'='*60}\n")
    
    # Fayl tanlash
    file_path = input("Fayl yo'li: ").strip()
    if not file_path:
        print("❌ Fayl yo'li kiritilmadi!")
        return
    
    # Validatsiya
    validator = Validator()
    is_valid, error = validator.validate_file(file_path)
    if not is_valid:
        print(f"❌ {error}")
        return
    
    # Kalit
    print(f"\n{algorithm_name} kalit uzunligi:")
    info = handler_class.get_info()
    print(f"  • {info['key_size']} bit")
    
    choice = input("\n1. Yangi kalit yaratish\n2. Mavjud kalitni kiritish\nTanlang (1/2): ").strip()
    
    if choice == '1':
        key = handler_class.generate_key()
        print(f"\n✅ Kalit yaratildi: {key}")
    elif choice == '2':
        key = input("Kalitni kiriting (hex): ").strip()
    else:
        print("❌ Noto'g'ri tanlov!")
        return
    
    # Kalit validatsiya
    algo_key = algorithm_name.split('-')[0]
    is_valid, error = validator.validate_key(key, algo_key)
    if not is_valid:
        print(f"❌ {error}")
        return
    
    # Chiqish fayli
    file_manager = FileManager()
    output_path = file_manager.get_output_filename(file_path)
    custom_output = input(f"\nChiqish fayli [{output_path}]: ").strip()
    if custom_output:
        output_path = custom_output
    
    # Shifrlash
    print("\n🔄 Shifrlash boshlanmoqda...")
    
    try:
        metrics = PerformanceMetrics()
        metrics.algorithm = algorithm_name
        metrics.filename = Path(file_path).name
        metrics.output_filename = output_path
        metrics.start_timer()
        
        # O'qish
        with Timer() as t:
            file_data = file_manager.read_file(file_path)
        metrics.read_time = t.get_elapsed()
        metrics.file_size = len(file_data)
        
        print(f"  ✓ Fayl o'qildi: {metrics.format_size(metrics.file_size)}")
        
        # Shifrlash
        with Timer() as t:
            encrypted_data, iv = handler_class.encrypt(file_data, key)
        metrics.encrypt_time = t.get_elapsed()
        metrics.iv = iv
        
        print(f"  ✓ Shifrlandi: {metrics.encrypt_time:.3f} s")
        
        # Yozish
        with Timer() as t:
            file_manager.write_file(output_path, encrypted_data)
        metrics.write_time = t.get_elapsed()
        
        print(f"  ✓ Saqlandi: {output_path}")
        
        metrics.stop_timer()
        
        # Natijalar
        print(f"\n{'='*60}")
        print(metrics.get_detailed_report())
        print(f"{'='*60}")
        
        # Kalitni saqlash
        save = input("\nKalitni saqlaysizmi? (y/n): ").strip().lower()
        if save == 'y':
            key_manager = KeyManager()
            label = input("Kalit nomi: ").strip()
            key_manager.add_key(algo_key, key, label)
            print("✅ Kalit saqlandi!")
        
    except Exception as e:
        print(f"\n❌ Xato: {str(e)}")


def ecc_encrypt():
    """ECC shifrlash"""
    print(f"\n{'='*60}")
    print(" ECC (ECIES) SHIFRLASH")
    print(f"{'='*60}\n")
    
    handler = ECCHandler()
    
    # Fayl
    file_path = input("Fayl yo'li: ").strip()
    if not file_path:
        print("❌ Fayl yo'li kiritilmadi!")
        return
    
    validator = Validator()
    is_valid, error = validator.validate_file(file_path)
    if not is_valid:
        print(f"❌ {error}")
        return
    
    # Kalit juftligi
    choice = input("\n1. Yangi kalit juftligi yaratish\n2. Mavjud public key'dan yuklash\nTanlang (1/2): ").strip()
    
    if choice == '1':
        print("\n🔑 Kalit juftligi yaratilmoqda...")
        with Timer() as t:
            private_pem, public_pem = handler.generate_keypair()
        print(f"✅ Kalit juftligi yaratildi ({t.get_elapsed():.3f} s)")
        
        # Saqlash
        save = input("\nKalitlarni faylga saqlaysizmi? (y/n): ").strip().lower()
        if save == 'y':
            pub_file = input("Public key fayl nomi [public.pem]: ").strip() or "public.pem"
            priv_file = input("Private key fayl nomi [private.pem]: ").strip() or "private.pem"
            
            with open(pub_file, 'w') as f:
                f.write(public_pem)
            with open(priv_file, 'w') as f:
                f.write(private_pem)
            
            print(f"✅ Public key: {pub_file}")
            print(f"✅ Private key: {priv_file}")
    
    elif choice == '2':
        pub_file = input("Public key fayli: ").strip()
        try:
            with open(pub_file, 'r') as f:
                public_pem = f.read()
        except Exception as e:
            print(f"❌ Xato: {e}")
            return
    else:
        print("❌ Noto'g'ri tanlov!")
        return
    
    # Chiqish
    file_manager = FileManager()
    output_path = file_manager.get_output_filename(file_path, '.ecc')
    custom_output = input(f"\nChiqish fayli [{output_path}]: ").strip()
    if custom_output:
        output_path = custom_output
    
    # Shifrlash
    print("\n🔄 Shifrlash boshlanmoqda...")
    
    try:
        # O'qish
        file_data = file_manager.read_file(file_path)
        print(f"  ✓ Fayl o'qildi: {len(file_data)} bayt")
        
        # Shifrlash
        with Timer() as t:
            encrypted_data = handler.encrypt(file_data, public_pem)
        print(f"  ✓ Shifrlandi: {t.get_elapsed():.3f} s")
        
        # Yozish
        file_manager.write_file(output_path, encrypted_data)
        print(f"  ✓ Saqlandi: {output_path}")
        
        print("\n✅ Muvaffaqiyat!")
        
    except Exception as e:
        print(f"\n❌ Xato: {str(e)}")


def decrypt_file():
    """Faylni deshifrlash"""
    print(f"\n{'='*60}")
    print(" FAYLNI DESHIFRLASH")
    print(f"{'='*60}\n")
    
    # Fayl
    file_path = input("Shifrlangan fayl yo'li: ").strip()
    if not file_path:
        print("❌ Fayl yo'li kiritilmadi!")
        return
    
    # Algoritm
    print("\n1. Simmetrik (AES/DES/GOST)")
    print("2. ECC")
    algo_choice = input("Algoritm turi (1/2): ").strip()
    
    file_manager = FileManager()
    
    if algo_choice == '1':
        # Simmetrik
        print("\n1. AES-256")
        print("2. DES")
        print("3. GOST Kuznechik")
        sym_choice = input("Tanlang (1-3): ").strip()
        
        handlers = {
            '1': ('AES', AESHandler),
            '2': ('DES', DESHandler),
            '3': ('GOST', GOSTHandler)
        }
        
        if sym_choice not in handlers:
            print("❌ Noto'g'ri tanlov!")
            return
        
        algo_name, handler = handlers[sym_choice]
        
        # Kalit
        key = input(f"\n{algo_name} kalit (hex): ").strip()
        
        # Deshifrlash
        print("\n🔄 Deshifrlash...")
        try:
            encrypted_data = file_manager.read_file(file_path)
            decrypted_data = handler.decrypt(encrypted_data, key)
            
            output_path = file_manager.get_decrypted_filename(file_path)
            custom_output = input(f"\nChiqish [{output_path}]: ").strip()
            if custom_output:
                output_path = custom_output
            
            file_manager.write_file(output_path, decrypted_data)
            print(f"\n✅ Deshifrlandi: {output_path}")
            
        except Exception as e:
            print(f"\n❌ Xato: {str(e)}")
    
    elif algo_choice == '2':
        # ECC
        priv_file = input("\nPrivate key fayli: ").strip()
        try:
            with open(priv_file, 'r') as f:
                private_pem = f.read()
        except Exception as e:
            print(f"❌ Xato: {e}")
            return
        
        print("\n🔄 Deshifrlash...")
        try:
            handler = ECCHandler()
            encrypted_data = file_manager.read_file(file_path)
            decrypted_data = handler.decrypt(encrypted_data, private_pem)
            
            output_path = file_manager.get_decrypted_filename(file_path)
            custom_output = input(f"\nChiqish [{output_path}]: ").strip()
            if custom_output:
                output_path = custom_output
            
            file_manager.write_file(output_path, decrypted_data)
            print(f"\n✅ Deshifrlandi: {output_path}")
            
        except Exception as e:
            print(f"\n❌ Xato: {str(e)}")


def generate_key():
    """Kalit generatsiya"""
    print(f"\n{'='*60}")
    print(" KALIT GENERATSIYA")
    print(f"{'='*60}\n")
    
    print("1. AES-256 (64 hex belgi)")
    print("2. DES (16 hex belgi)")
    print("3. GOST (64 hex belgi)")
    print("4. ECC kalit juftligi")
    
    choice = input("\nTanlang (1-4): ").strip()
    
    if choice == '1':
        key = AESHandler.generate_key()
        print(f"\n✅ AES-256 kalit:\n{key}")
    elif choice == '2':
        key = DESHandler.generate_key()
        print(f"\n✅ DES kalit:\n{key}")
    elif choice == '3':
        key = GOSTHandler.generate_key()
        print(f"\n✅ GOST kalit:\n{key}")
    elif choice == '4':
        handler = ECCHandler()
        with Timer() as t:
            private_pem, public_pem = handler.generate_keypair()
        
        print(f"\n✅ Kalit juftligi yaratildi ({t.get_elapsed():.3f} s)")
        
        save = input("\nFaylga saqlash? (y/n): ").strip().lower()
        if save == 'y':
            pub_file = input("Public key [public.pem]: ").strip() or "public.pem"
            priv_file = input("Private key [private.pem]: ").strip() or "private.pem"
            
            with open(pub_file, 'w') as f:
                f.write(public_pem)
            with open(priv_file, 'w') as f:
                f.write(private_pem)
            
            print(f"✅ Saqlandi: {pub_file}, {priv_file}")
    else:
        print("❌ Noto'g'ri tanlov!")


def main():
    """Asosiy funksiya"""
    print_banner()
    
    while True:
        print_menu()
        choice = input("Tanlang (1-7): ").strip()
        
        if choice == '1':
            symmetric_encrypt("AES-256", AESHandler)
        elif choice == '2':
            symmetric_encrypt("DES", DESHandler)
        elif choice == '3':
            symmetric_encrypt("GOST Kuznechik", GOSTHandler)
        elif choice == '4':
            ecc_encrypt()
        elif choice == '5':
            decrypt_file()
        elif choice == '6':
            generate_key()
        elif choice == '7':
            print("\n👋 Xayr! Dasturdan chiqdingiz.\n")
            break
        else:
            print("\n❌ Noto'g'ri tanlov! Qaytadan urinib ko'ring.\n")
        
        input("\nDavom etish uchun Enter bosing...")
        print("\n" * 2)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Dastur to'xtatildi.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Xatolik: {e}\n")
        sys.exit(1)
