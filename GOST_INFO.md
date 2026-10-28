# GOST Kuznechik

Loyiha GOST R 34.12-2015 Kuznechik shifrini `gostcrypto==1.2.5` yordamida
bevosita qo'llaydi; AES bilan almashtirmaydi.

## Amalga oshirish

- Blok shifr: Kuznechik, 128-bit blok
- Kalit: 256 bit
- Ishlash rejimi: CBC, GOST padding method 2
- Integrity: ciphertext va IV uchun HMAC-SHA-256 (Encrypt-then-MAC)
- Konvert: versiya belgisi + IV + ciphertext + HMAC tag

Deshifrlashdan oldin HMAC tekshiriladi. Kalit noto'g'ri yoki konvert baytlari
o'zgargan bo'lsa, ochiq matn qaytarilmaydi.

## Test

`tests/test_gost_handler.py` Kuznechik standart known-answer vektorini hamda
turli uzunlikdagi ma'lumotlar uchun shifrlash/deshifrlash testlarini o'z ichiga oladi.

## Eski fayllar

Oldingi IV + CBC ciphertext formatidagi fayllarda HMAC yo'q. O'zgarishni
ishonchli aniqlab bo'lmagani sababli yangi handler bunday fayllarni rad etadi.
