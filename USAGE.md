# FOYDALANISH QO'LLANMASI

## O'RNATISH

### 1. Talablar
```bash
Python 3.8 yoki undan yuqori versiya
```

### 2. Dependencies o'rnatish
```bash
pip install -r requirements.txt
```

Agar internet yo'q bo'lsa, quyidagi kutubxonalarni offline o'rnatish kerak:
- pycryptodome (AES, DES uchun)
- cryptography (ECC uchun) 
- gostcrypto (GOST uchun)
- customtkinter (GUI uchun)
- matplotlib (grafiklar uchun)

### 3. CLI versiyasidan foydalanish
```bash
python cli.py
```

## TEZKOR BOSHLASH

### Misol 1: AES bilan faylni shifrlash

```bash
# CLI orqali
python cli.py

# Menyudan tanlang:
# 1. AES-256 shifrlash
# Faylni kiriting
# Kalitni yarating yoki kiriting
# Natija: file.encrypted
```

### Misol 2: ECC bilan shifrlash

```bash
python cli.py

# Menyudan:
# 4. ECC shifrlash
# Kalit juftligini yarating
# Public key bilan shifrlang
# Private key bilan deshifrlang
```

## KALIT FORMATLARI

### AES-256
```
Uzunlik: 64 hex belgi (256 bit)
Misol: a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2
```

### DES
```
Uzunlik: 16 hex belgi (64 bit)
Misol: a1b2c3d4e5f6a7b8
```

### GOST Kuznechik
```
Uzunlik: 64 hex belgi (256 bit)
Misol: a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2
```

### ECC
```
Format: PEM
Public key: -----BEGIN PUBLIC KEY-----...
Private key: -----BEGIN PRIVATE KEY-----...
```

## ALGORITMLAR TAQQOSLASH

| Algoritm | Kalit | Tezlik | Xavfsizlik | Tavsiya |
|----------|-------|--------|------------|---------|
| AES-256  | 256 bit | Juda tez | Juda yuqori | ✅ Tavsiya etiladi |
| DES      | 64 bit | Tez | Past | ⚠️ Faqat o'quv |
| GOST     | 256 bit | O'rtacha | Yuqori | ✅ RF standart |
| ECC      | 256 bit | O'rtacha | Juda yuqori | ✅ Assimmetrik |

## XAVFSIZLIK MASLAHATLARI

1. **Kalitlarni xavfsiz saqlang**
   - Kalitlarni parollar bilan himoyalang
   - Maxfiy kalitlarni ulashmang

2. **Kalit uzunligi**
   - Minimal AES-256 ishlatling
   - DES ishlatmang (zaif)

3. **Backup oling**
   - Muhim fayllarni shifrlashdan oldin backup oling
   - Kalitlarni yo'qotmang!

4. **Transport xavfsizligi**
   - Kalitlarni xavfsiz kanallar orqali yuboring
   - E-mail orqali kalit yubormang

## MUAMMOLARNI HAL QILISH

### Kalit noto'g'ri
```
Sabab: Kalit formati noto'g'ri
Yechim: Kalit uzunligini tekshiring
- AES: 64 hex
- DES: 16 hex
- GOST: 64 hex
```

### Fayl buzilgan
```
Sabab: Noto'g'ri kalit yoki fayl shikastlangan
Yechim: To'g'ri kalitni ishlatganingizni tekshiring
```

### Xotira yetishmaydi
```
Sabab: Fayl juda katta
Yechim: 500 MB dan kichik fayllarni ishlating
```

## MISOLLAR

### 1. Test fayl yaratish
```bash
echo "Bu test fayli" > test.txt
```

### 2. AES bilan shifrlash
```python
from crypto.aes_handler import AESHandler
from utils.file_manager import FileManager

# Kalit yaratish
key = AESHandler.generate_key()
print(f"Kalit: {key}")

# Faylni o'qish
fm = FileManager()
data = fm.read_file("test.txt")

# Shifrlash
encrypted, iv = AESHandler.encrypt(data, key)

# Saqlash
fm.write_file("test.txt.encrypted", encrypted)
```

### 3. Deshifrlash
```python
# O'qish
encrypted = fm.read_file("test.txt.encrypted")

# Deshifrlash
decrypted = AESHandler.decrypt(encrypted, key)

# Saqlash
fm.write_file("test.txt.decrypted", decrypted)
```

### 4. ECC misol
```python
from crypto.ecc_handler import ECCHandler

handler = ECCHandler()

# Kalit yaratish
private, public = handler.generate_keypair()

# Shifrlash
data = b"Test message"
encrypted = handler.encrypt(data, public)

# Deshifrlash
decrypted = handler.decrypt(encrypted, private)
```

## FAQ

**S: Kalitni unutsam nima qilaman?**
J: Afsuski, faylni tiklash mumkin emas. Shuning uchun kalitlarni xavfsiz joyda saqlang.

**S: Qaysi algoritm eng yaxshi?**
J: Simmetrik uchun AES-256, assimmetrik uchun ECC tavsiya etiladi.

**S: Video fayllarni shifrlash mumkinmi?**
J: Hozircha yo'q. Faqat 500 MB gacha fayllar qo'llab-quvvatlanadi.

**S: Internet kerakmi?**
J: Yo'q, dastur to'liq offline ishlaydi.

**S: Kalitlarni qaerda saqlash kerak?**
J: Xavfsiz joyda, masalan parol manager'da yoki shifrlangan USB'da.

## VERSIYA TARIXI

### v1.0 (2026-01-24)
- ✅ AES-256 qo'llab-quvvatlash
- ✅ DES qo'llab-quvvatlash
- ✅ GOST Kuznechik qo'llab-quvvatlash
- ✅ ECC (ECIES) qo'llab-quvvatlash
- ✅ CLI interfeys
- ✅ Kalit boshqaruvi
- ✅ Performance o'lchash

## MUALLIF

Claude - 2026

Savollar yoki takliflar: GitHub Issues
