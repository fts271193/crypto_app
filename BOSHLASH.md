# 🚀 TEZKOR BOSHLASH

## 1️⃣ YUKLAB OLISH

ZIP faylni yuklab olib, ochib oling:
```bash
unzip crypto_app.zip
cd crypto_app
```

## 2️⃣ DARHOL ISHLATISH (CLI)

Kutubxonalar o'rnatmasdan CLI versiyasini sinab ko'ring:

```bash
# Dasturni ishga tushiring
python3 cli.py
```

Menyudan tanlang:
- `1` - AES-256 shifrlash
- `2` - DES shifrlash  
- `3` - GOST Kuznechik shifrlash
- `4` - ECC shifrlash
- `5` - Faylni deshifrlash
- `6` - Kalit generatsiya
- `7` - Chiqish

## 3️⃣ DEMO KO'RISH

```bash
python3 demo.py
```

Bu sizga:
- AES shifrlashni ko'rsatadi
- ECC shifrlashni ko'rsatadi
- Avtomatik test fayllar yaratadi

## 4️⃣ TO'LIQ O'RNATISH (GUI uchun)

Agar grafik interfeys kerak bo'lsa:

```bash
# Virtual environment yaratish
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki
venv\Scripts\activate     # Windows

# Kutubxonalarni o'rnatish
pip install -r requirements.txt

# GUI ni ishga tushirish
python main.py
```

## 5️⃣ TEZKOR MISOLLAR

### Fayl shifrlash (AES):
```bash
python3 cli.py
# 1 tanlang
# Fayl yo'lini kiriting: test.txt
# 1 (yangi kalit)
# Enter...
```

### Kalit yaratish:
```bash
python3 cli.py
# 6 tanlang
# 1 (AES kalit)
# Kalitni nusxalang!
```

## ⚠️ MUHIM

1. **Kalitni saqlang!** - Kalit yo'qolsa, faylni tiklash mumkin emas
2. **Backup oling** - Muhim fayllarni shifrlashdan oldin
3. **Test qiling** - Avval test fayl bilan sinab ko'ring

## 📚 QOSHIMCHA

- `README.md` - To'liq dokumentatsiya
- `USAGE.md` - Batafsil qo'llanma
- `XULOSA.md` - Loyiha haqida ma'lumot

## 🆘 YORDAM

Muammo bo'lsa:
1. Python 3.8+ o'rnatilganligini tekshiring: `python3 --version`
2. Test dasturni ishga tushiring: `python3 test.py`
3. Demo ni ko'ring: `python3 demo.py`

## 📞 TEST QILISH

```bash
# Barcha algoritmlarni test qilish
python3 test.py
```

Bu test:
- ✅ AES-256
- ✅ DES
- ✅ GOST
- ✅ ECC

---

**Omad!** 🎉
