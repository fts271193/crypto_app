# 🔐 Fayl Shifrlash Dasturi

Turli xil kriptografik algoritmlar yordamida fayllarni shifrlash va deshifrlash uchun zamonaviy desktop dastur.

## 📋 Xususiyatlar

### Qo'llab-quvvatlanadigan Algoritmlar

#### Simmetrik Shifrlash
- **AES-256-GCM**: authenticated encryption; ciphertext o'zgartirilsa yoki kalit noto'g'ri bo'lsa, deshifrlash rad etiladi
- **DES-CBC + HMAC-SHA-256**: yaxlitlik tekshiruvi bilan, faqat o'quv maqsadida (DES eskirgan va zaif)
- **GOST Kuznechik**: Rossiya milliy standarti (GOST R 34.12-2015)
  - Haqiqiy Kuznechik shifri, CBC rejimi, GOST padding usuli #2 va HMAC-SHA-256 yaxlitlik tekshiruvi
  - `gostcrypto==1.2.5` kutubxonasi orqali ishlaydi
- **O'z DSt 1105:2009**: CBC + HMAC-SHA-256 yaxlitlik tekshiruvi

#### Assimmetrik Shifrlash
- **ECC (ECIES)**: Elliptic Curve Integrated Encryption Scheme
  - Egri chiziq: secp256r1 (P-256)
  - Hybrid: ECC + AES-256-GCM

Shifrlangan fayllar yaxlitlik tekshiruvi bilan versiyalangan formatda saqlanadi.
Avvalgi autentifikatsiyasiz CBC/ECC fayllari xavfsizlik sababli deshifrlanmaydi.

### Qo'llab-quvvatlanadigan Fayl Turlari
- ✅ Matnli fayllar: `.txt`, `.doc`, `.docx`, `.pdf`
- ✅ Jadval fayllar: `.xlsx`, `.xls`, `.csv`
- ✅ Prezentatsiya: `.ppt`, `.pptx`
- ✅ Kod fayllar: `.py`, `.java`, `.cpp`, `.js`, `.html`, `.css`
- ✅ Ma'lumotlar bazasi: `.db`, `.sql`
- ✅ Arxiv fayllar: `.zip`, `.rar`, `.7z`
- ✅ JSON/XML: `.json`, `.xml`

**Maksimal fayl hajmi**: 500 MB

## 🚀 O'rnatish

### 1. Repository'ni klonlash
```bash
git clone https://github.com/yourusername/crypto-app.git
cd crypto-app
```

### 2. Virtual environment yaratish
```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Dependencies o'rnatish
```bash
pip install -r requirements.txt
```

### 4. Dasturni ishga tushirish
```bash
python main.py
```

## 📖 Foydalanish Qo'llanmasi

### Simmetrik Shifrlash

1. **Algoritmni tanlash**: AES, DES yoki GOST
2. **Faylni tanlash**: "Tanlash" tugmasi orqali
3. **Kalit kiritish**: 
   - Qo'lda kiritish yoki
   - 🔑 tugmasi orqali avtomatik yaratish
4. **Shifrlash**: "Shifrlash" tugmasini bosish
5. **Deshifrlash**: Xuddi shu kalit bilan "Deshifrlash"

### ECC Shifrlash

1. **Kalit juftligi yaratish**: 
   - "🔑 Kalit juftligini yaratish" tugmasini bosing
   - Public va Private kalitlar avtomatik yaratiladi
2. **Shifrlash**: Public key bilan
3. **Deshifrlash**: Private key bilan

### Kalit Formatlari

- **AES-256**: 64 hex belgi (256 bit)
  ```
  Misol: a1b2c3d4e5f6...  (jami 64 belgi)
  ```

- **DES**: 16 hex belgi (64 bit)
  ```
  Misol: a1b2c3d4e5f6a7b8
  ```

- **GOST**: 64 hex belgi (256 bit)
  ```
  Misol: a1b2c3d4e5f6...  (jami 64 belgi)
  ```

## 🎯 Klaviatura Shortcut'lari

- `Ctrl+Q` - Dasturdan chiqish
- `Ctrl+H` - Yordam oynasi

## 📊 Performance Ko'rsatkichlari

Dastur har bir shifrlash/deshifrlash amalini besh marta takrorlab, kriptografik
amalning o'rtacha vaqtini va standart og'ishini ko'rsatadi. Tezlik faqat
shifrlash/deshifrlash vaqtiga qarab hisoblanadi; diskka o'qish-yozish vaqti
alohida ko'rsatiladi. Umumiy vaqt disk amallarini ham o'z ichiga oladi.

- Kalit formatini tayyorlash vaqti
- Fayl hajmi
- O'qish vaqti
- Kriptografik amalning o'rtacha vaqti hamda standart og'ishi
- Yozish vaqti
- Umumiy vaqt
- Kripto amali tezligi (MB/s)
- O'lchovlarni CSV fayliga eksport qilish

## 🔒 Xavfsizlik

- Saqlangan kalitlar AES-GCM bilan himoyalanadi; Windows'da master kalit DPAPI bilan joriy foydalanuvchiga bog'lanadi.
- AES-GCM, ECC va CBC + HMAC formatlari o'zgartirilgan ciphertext yoki noto'g'ri kalitni aniqlaydi.
- Eski autentifikatsiyasiz CBC/ECC fayllari ataylab ochilmaydi.
- DES faqat o'quv maqsadida; maxfiy ma'lumotlar uchun ishlatmang.
- Kalit ishlov vaqtida dastur xotirasida bo'ladi; xotiradan ishonchli o'chirildi deb kafolat berilmaydi.

## 📁 Loyiha Strukturasi

```
crypto_app/
│
├── main.py                 # Asosiy fayl
├── requirements.txt        # Kutubxonalar
├── README.md              # Hujjat
│
├── gui/                   # Interfeys
│   ├── symmetric_window.py
│   ├── ecc_window.py
│   └── components.py
│
├── crypto/                # Kriptografiya
│   ├── aes_handler.py
│   ├── des_handler.py
│   ├── gost_handler.py
│   └── ecc_handler.py
│
├── utils/                 # Yordamchi modullar
│   ├── file_manager.py
│   ├── key_manager.py
│   ├── validator.py
│   └── metrics.py
│
└── data/                  # Ma'lumotlar
    └── keys.json.enc      # Saqlangan kalitlar
```

## ⚙️ Texnik Stack

- **GUI**: CustomTkinter
- **Kriptografiya**: 
  - PyCryptodome (AES, DES)
  - Cryptography (ECC)
  - GostCrypto (GOST Kuznechik)
- **Vizualizatsiya**: Matplotlib

## 🐛 Muammolarni Hal Qilish

### Xatolik: Module not found
```bash
pip install -r requirements.txt
```

### Xatolik: Permission denied
- Windows: Dasturni Administrator sifatida ishga tushiring
- Linux/Mac: Fayl ruxsatlarini tekshiring

### Kalit formati noto'g'ri
- Faqat 0-9 va a-f (yoki A-F) belgilar
- AES/GOST: 64 belgi
- DES: 16 belgi

## 📝 Kelajakda Qo'shilishi Mumkin

- [ ] Video va rasm fayllar qo'llab-quvvatlash
- [ ] Multi-threading (parallel shifrlash)
- [ ] Cloud integration (Google Drive, Dropbox)
- [ ] Digital signature (ECDSA)
- [ ] Batch processing
- [ ] Ko'p tillilik (O'zbek, Rus, Ingliz)
- [ ] Dark/Light mode

## 📄 Litsenziya

MIT License

## 👨‍💻 Muallif

Claude - 2026

## 🤝 Hissa Qo'shish

Pull request'lar qabul qilinadi. Katta o'zgarishlar uchun avval issue oching.

## 📞 Aloqa

Savollar yoki takliflar bo'lsa, issue oching.

---

**Eslatma**: Bu dastur o'quv maqsadida yaratilgan. Muhim ma'lumotlarni shifrlashdan oldin backup oling!
