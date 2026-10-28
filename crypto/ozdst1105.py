"""
O'z DSt 1105:2009 — Ma'lumotlarni shifrlash algoritmi (AШД / "Алгоритм шифрования данных")
Python implementatsiyasi.

Blok: 256 bit (32 bayt), kalit k: 256 bit, funksional kalit kf: 256 bit (yoki 512 bitli kalit = k || kf),
bosqichlar soni e = 8. Rejimlar: ECB ("Elektron kod kitobi") va CBC ("ShifrBloklarni ilaktirish").

MUHIM: standart matnida bir nechta noaniqlik va xatolar bor. Ushbu kod standartning A-ilovasidagi
nazorat misoliga (test vector) BAYTMA-BAYT mos keladigan qilib yozilgan. Matndan farq qiladigan
joylar quyida "[TV]" belgisi bilan izohlangan.
"""

P = 256          # modul p
ROUNDS = 8       # e
BLOCK = 32       # bayt
KSE_BITS = 672
SHIFT = 83       # har bosqichda kse siljishi (bit)


# ----------------------------------------------------------------------------------------------
# 5.1.6  Parametrli algebra: X â Y = X + Y(1 + R X)  (mod p)
# ----------------------------------------------------------------------------------------------
def pmul(x, y, R, p):
    return (x + y * (1 + R * x)) % p


def ppow(x, d, R, p):
    """Parametrli darajaga ko'tarish X^\\d (mod p), kvadrat-ko'paytirish usulida (5.1.6)."""
    result, base = 0, x % p          # 0 — parametrli guruhning birlik elementi
    while d:
        if d & 1:
            result = pmul(result, base, R, p)
        base = pmul(base, base, R, p)   # X^\2 = X(2 + X R)
        d >>= 1
    return result


def _fix_exponent(b):
    """6.3.1.3, 1), 4), 5) qoidalar: d >= 3 va d ≡ 3 (mod 4)."""
    d = 3 if b < 3 else b
    if d % 2 == 0:
        d = d - 1 if d % 4 == 0 else d + 1
    elif (d - 1) % 4 == 0:
        d -= 2
    return d


def _effective_exponent(d):
    # [TV] Nazorat misolidagi almashtirish jadvallari qoidadan chiqadigan d (35 va 67) bilan emas,
    # balki 2^(floor(log2 d)) + 1 (33 va 65) bilan hosil bo'lgan. Ya'ni etalon dasturda daraja
    # faqat yuqori bit bo'yicha kvadratlash + bitta ko'paytirish sifatida hisoblangan.
    return (1 << (d.bit_length() - 1)) + 1


# ----------------------------------------------------------------------------------------------
# 6.3.1  ShaklSeansKalitBayt(k, kf)
# ----------------------------------------------------------------------------------------------
def compute_kse(k: bytes, kf: bytes) -> bytes:
    """kse = k + k'(1 + kf*k), chapdan 672 bit; k' — kf ning o'ngdagi 192 biti."""
    ki = int.from_bytes(k, "big")
    kfi = int.from_bytes(kf, "big")
    kp = kfi & ((1 << 192) - 1)
    v = ki + kp * (1 + kfi * ki)
    if v.bit_length() < KSE_BITS:
        raise ValueError("kse 672 bitdan qisqa chiqdi — bunday kalit juftligi yaroqsiz")
    v >>= v.bit_length() - KSE_BITS
    return v.to_bytes(KSE_BITS // 8, "big")


def _sbox(d, R, L, swap_param):
    """6.3.1.4: bsA[i] = (((i+L) mod 256)+1)^\\d (mod 257) (mod 256) + takrorlanishlarni tuzatish."""
    d_eff = _effective_exponent(d)
    a = [ppow(((i + L) % 256) + 1, d_eff, R, 257) % 256 for i in range(256)]
    for i in range(1, 256):
        # [TV] Shart: element 0 ga teng yoki oldingisiga juda yaqin (|farq| < 8) bo'lsa — almashtirish.
        if a[i] == 0 or abs(a[i - 1] - a[i]) < 8:
            j = (i - swap_param) % 256
            a[i], a[j] = a[j], a[i]
            swap_param = (swap_param - 5) % 256
    return a


def _invert_perm(s):
    inv = [0] * 256
    for i, v in enumerate(s):
        inv[v] = i
    return inv


def make_sboxes(kst: bytes):
    """B massivi -> (d1,R1,L1),(d2,R2,L2) -> B1A, B2A va teskarilari."""
    # [TV] B massivi Kst ning 20..27-baytlari (Kss dan keyingi 8 bayt).
    b = list(kst[20:28])
    d1, d2 = _fix_exponent(b[0]), _fix_exponent(b[4])
    R1, R2 = b[1] or 1, b[5] or 1
    L1, L2 = b[2] or 1, b[6] or 1
    b3, b7 = b[3] or 1, b[7] or 1
    s1 = _sbox(d1, R1, L1, b3)
    s2 = _sbox(d2, R2, L2, b7)
    return s1, s2, _invert_perm(s1), _invert_perm(s2)


# ----------------------------------------------------------------------------------------------
# 5.1.3 / 6.3.2  Maxsus tuzilishli diamatritsalar
# ----------------------------------------------------------------------------------------------
def _adjust(kss):
    """6.3.2.1 — diamatritsa teskarilanuvchi bo'lishi uchun tuzatishlar (10 elementli yarim uchun)."""
    k = [(x - 1) % P if x == 0 else x for x in kss]
    if k[6] % 2 == 0:
        k[6] = (k[6] - 1) % P
    # [TV] 1-shartda kss[5] o'zgartiriladi (matnda kss[8]),
    # 3-shartda yig'indi kss[4] bilan olinadi (matnda kss[9] — bosmaxona xatosi).
    if (k[6] + k[0] + k[8] + k[3] + k[5]) % 2 == 0:
        k[5] = (k[5] - 1) % P
    if (k[6] + k[1] + k[3] + k[9] + k[4]) % 2 == 0:
        k[9] = (k[9] - 1) % P
    if (k[6] + k[2] + k[3] + k[4] + k[7]) % 2 == 0:
        k[7] = (k[7] - 1) % P
    return k


def make_diamatrix(k):
    """6.3.2.2: 10 element -> 4x4 maxsus tuzilishli diamatritsa."""
    return [[k[6], k[0], k[1], k[2]],
            [k[3], k[6], k[3], k[3]],
            [k[4], k[5], k[6], k[4]],
            [k[7], k[8], k[9], k[6]]]


def dia_mul(h, k):
    """6.3.3: diamatritsaviy ko'paytirish H â2 K (mod p)."""
    cs = [sum(k[i][u] for i in range(4)) for u in range(4)]   # K ustun yig'indilari
    hs = [sum(h[i][s] for i in range(4)) for s in range(4)]   # H ustun yig'indilari
    out = [[0] * 4 for _ in range(4)]
    for s in range(4):
        for u in range(4):
            if s == u:
                v = h[u][u] * cs[u] - sum(h[i][i] * k[i][u] for i in range(4) if i != u)
            else:
                v = (h[s][u] * cs[u] + hs[s] * k[s][u]
                     - sum(h[s][i] * k[i][u] for i in range(4) if i not in (s, u)))
            out[s][u] = v % P
    return out


def _solve_mod256(A, b):
    """A x = b (mod 256), A — teskarilanuvchi (determinant toq)."""
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        p = next((r for r in range(c, n) if M[r][c] % 2), None)
        if p is None:
            raise ValueError("diamatritsa teskarilanmaydi")
        M[c], M[p] = M[p], M[c]
        iv = pow(M[c][c], -1, 256)
        M[c] = [x * iv % 256 for x in M[c]]
        for r in range(n):
            if r != c and M[r][c]:
                f = M[r][c]
                M[r] = [(x - f * y) % 256 for x, y in zip(M[r], M[c])]
    return [M[i][n] for i in range(n)]


def dia_inverse(k):
    """K â2 X = I tenglamani yechib, teskari diamatritsani topadi (u ham maxsus tuzilishli)."""
    A = [[0] * 16 for _ in range(16)]
    for j in range(16):
        e = [[0] * 4 for _ in range(4)]
        e[j // 4][j % 4] = 1
        o = dia_mul(k, e)
        for i in range(16):
            A[i][j] = o[i // 4][i % 4]
    ident = [1 if i % 5 == 0 else 0 for i in range(16)]
    x = _solve_mod256(A, ident)
    return [x[4 * i:4 * i + 4] for i in range(4)]


# ----------------------------------------------------------------------------------------------
# Holat (8x4) bilan ishlash: qator r = baytlar 4r..4r+3; H1 = 0..3-qatorlar, H2 = 4..7-qatorlar
# ----------------------------------------------------------------------------------------------
def _to_state(block):
    return [list(block[4 * r:4 * r + 4]) for r in range(8)]


def _from_state(st):
    return bytes(x for row in st for x in row)


def _xor(st, key: bytes):
    """Qo'shBosqichKalit / Qo'shHolat."""
    return [[st[r][c] ^ key[4 * r + c] for c in range(4)] for r in range(8)]


def _sur(st):
    """6.3.7 (sh): c-ustun (c+1) ga pastga, so'ng r-qator (r+1) mod 4 ga o'ngga siklik suriladi."""
    t = [row[:] for row in st]
    for c in range(4):
        colv = [st[r][c] for r in range(8)]
        sh = (c + 1) % 8
        for r in range(8):
            t[(r + sh) % 8][c] = colv[r]
    out = []
    for r in range(8):
        sh = (r + 1) % 4
        out.append([t[r][(c - sh) % 4] for c in range(4)])
    return out


def _sur_inv(st):
    """6.3.7 (dsh): avval qatorlar chapga, so'ng ustunlar yuqoriga."""
    t = []
    for r in range(8):
        sh = (r + 1) % 4
        t.append([st[r][(c + sh) % 4] for c in range(4)])
    out = [row[:] for row in t]
    for c in range(4):
        sh = (c + 1) % 8
        for r in range(8):
            out[r][c] = t[(r + sh) % 8][c]
    return out


def _sub(st, box):
    return [[box[x] for x in row] for row in st]


class OzDSt1105:
    """
    Foydalanish:
        c = OzDSt1105(k, kf)          # k, kf — 32 baytdan
        c = OzDSt1105(key64)          # 64 bayt: birinchi 32 — k, keyingi 32 — kf
    """

    def __init__(self, key: bytes, kf: bytes = None):
        if kf is None:
            if len(key) != 64:
                raise ValueError("kf berilmasa, kalit 64 bayt (512 bit) bo'lishi kerak")
            key, kf = key[:32], key[32:]
        if len(key) != 32 or len(kf) != 32:
            raise ValueError("k va kf 32 baytdan bo'lishi kerak")
        self.k, self.kf = bytes(key), bytes(kf)

        # ShaklSeansKalitBayt
        self.kse = compute_kse(self.k, self.kf)
        kst = self.kse[:32]                          # [TV] Kst = kse ning chap 256 biti
        self.s1, self.s2, self.s1_inv, self.s2_inv = make_sboxes(kst)

        # ShaklSeansKalit
        kss = list(kst[:20])
        self.Ka = make_diamatrix(_adjust(kss[:10]))
        self.Kb = make_diamatrix(_adjust(kss[10:]))
        self.Ka_inv = dia_inverse(self.Ka)
        self.Kb_inv = dia_inverse(self.Kb)

        # ShaklBosqichKalit: 9 ta 256-bitli kalit (8 bosqich + yakuniy)
        v = int.from_bytes(self.kse, "big")
        mask = (1 << KSE_BITS) - 1
        self.round_keys = []
        for t in range(ROUNDS + 1):
            s = (SHIFT * t) % KSE_BITS
            rv = ((v << s) | (v >> (KSE_BITS - s))) & mask if s else v
            self.round_keys.append(rv.to_bytes(KSE_BITS // 8, "big")[:32])

    # [TV] Aralash: bosqichlar ichida faqat H1 (Ka bilan), yakunda faqat H2 (Kb^-1 bilan) aralashadi.
    def _aralash_h1(self, st, K):
        st[:4] = dia_mul(st[:4], K)
        return st

    def _aralash_h2(self, st, K):
        st[4:] = dia_mul(st[4:], K)
        return st

    # ---------------------------------- bitta blok ----------------------------------
    def encrypt_block(self, block: bytes) -> bytes:
        if len(block) != BLOCK:
            raise ValueError("blok 32 bayt bo'lishi kerak")
        st = _to_state(block)
        for t in range(ROUNDS):
            st = _xor(st, self.round_keys[t])
            st = self._aralash_h1(st, self.Ka)
            st = _sur(st)
            st = _sub(st, self.s1 if t % 2 == 0 else self.s2)   # toq bosqich — B1A, juft — B2A
        st = _xor(st, self.round_keys[ROUNDS])
        st = self._aralash_h2(st, self.Kb_inv)
        return _from_state(st)

    def decrypt_block(self, block: bytes) -> bytes:
        if len(block) != BLOCK:
            raise ValueError("blok 32 bayt bo'lishi kerak")
        st = _to_state(block)
        st = self._aralash_h2(st, self.Kb)
        st = _xor(st, self.round_keys[ROUNDS])
        for t in reversed(range(ROUNDS)):
            st = _sub(st, self.s1_inv if t % 2 == 0 else self.s2_inv)
            st = _sur_inv(st)
            st = self._aralash_h1(st, self.Ka_inv)
            st = _xor(st, self.round_keys[t])
        return _from_state(st)

    # ---------------------------------- rejimlar ----------------------------------
    @staticmethod
    def _pad(data, padding):
        if padding is None:
            if len(data) % BLOCK:
                raise ValueError("padding=None bo'lsa, ma'lumot uzunligi 32 ga karrali bo'lishi kerak")
            return data
        if padding == "pkcs7":
            n = BLOCK - len(data) % BLOCK
            return data + bytes([n]) * n
        if padding == "zero":
            return data + b"\x00" * (-len(data) % BLOCK)
        raise ValueError("padding: None, 'pkcs7' yoki 'zero'")

    @staticmethod
    def _unpad(data, padding):
        if padding == "pkcs7":
            n = data[-1]
            if not 1 <= n <= BLOCK or data[-n:] != bytes([n]) * n:
                raise ValueError("noto'g'ri padding")
            return data[:-n]
        if padding == "zero":
            return data.rstrip(b"\x00")
        return data

    def encrypt(self, data: bytes, mode="cbc", iv: bytes = None, padding="pkcs7") -> bytes:
        data = self._pad(bytes(data), padding)
        out, prev = [], iv
        if mode == "cbc" and (iv is None or len(iv) != BLOCK):
            raise ValueError("CBC uchun 32 baytli IV kerak")
        for i in range(0, len(data), BLOCK):
            blk = data[i:i + BLOCK]
            if mode == "cbc":
                blk = bytes(a ^ b for a, b in zip(blk, prev))
            c = self.encrypt_block(blk)
            out.append(c)
            prev = c
        return b"".join(out)

    def decrypt(self, data: bytes, mode="cbc", iv: bytes = None, padding="pkcs7") -> bytes:
        if len(data) % BLOCK:
            raise ValueError("shifrmatn uzunligi 32 ga karrali bo'lishi kerak")
        if mode == "cbc" and (iv is None or len(iv) != BLOCK):
            raise ValueError("CBC uchun 32 baytli IV kerak")
        out, prev = [], iv
        for i in range(0, len(data), BLOCK):
            blk = data[i:i + BLOCK]
            p = self.decrypt_block(blk)
            if mode == "cbc":
                p = bytes(a ^ b for a, b in zip(p, prev))
            out.append(p)
            prev = blk
        return self._unpad(b"".join(out), padding)


# ----------------------------------------------------------------------------------------------
# A-ilova: nazorat misoli
# ----------------------------------------------------------------------------------------------
def self_test(verbose=True):
    h = bytes.fromhex
    K = h("37B60BBA0AB160CFDC18F50CDEE8E04530B3F8AF1432FE511FBB2029112F2143")
    KF = h("47E76946 69C546B6FE163A89B0D896D6238B231532C404349CB0C7AA813DF96D".replace(" ", ""))
    IV = h("2654BB5FA375D89854EA489F9AA88416FD4DEBBD9B3B40334829F9EE5234C37A")
    PT = h("30313233343536373839414243444546" * 2)
    CT = h("13BBDB34B5D635C0C1EEBD2A20A86A54A8F580C83248BEA5C3FEE3EED1386B4B")
    KSE0 = h("F87E98FFC6660C6406658BE729A81D65B9A626D922774 0C3".replace(" ", ""))

    c = OzDSt1105(K, KF)
    checks = {
        "kse": c.kse.startswith(KSE0),
        "B1A[0..3]": c.s1[:4] == [0x62, 0xE9, 0xA9, 0xE5],
        "B2A[0..3]": c.s2[:4] == [0xE9, 0x47, 0x0C, 0x68],
        "Kb[2]": c.round_keys[1].hex().upper().startswith("5F394D40"),
        "shifrlash": c.encrypt(PT, "cbc", IV, padding=None) == CT,
        "deshifrlash": c.decrypt(CT, "cbc", IV, padding=None) == PT,
    }
    if verbose:
        for name, ok in checks.items():
            print(f"{name:12s}: {'OK' if ok else 'XATO'}")
    return all(checks.values())


if __name__ == "__main__":
    ok = self_test()
    print("\nNazorat misoli:", "MOS KELDI ✓" if ok else "MOS KELMADI ✗")

    # Namuna
    import os
    key = os.urandom(64)           # 512 bit = k || kf
    iv = os.urandom(32)
    cipher = OzDSt1105(key)
    msg = "Salom, O'z DSt 1105:2009!".encode()
    ct = cipher.encrypt(msg, mode="cbc", iv=iv)
    print("\nShifrmatn:", ct.hex())
    print("Ochiq matn:", cipher.decrypt(ct, mode="cbc", iv=iv).decode())
