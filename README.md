# netrecon

<p align="center">
  <img src="https://img.shields.io/badge/Language-Python%20%2F%20Bash-blue" alt="Language" />
  <img src="https://img.shields.io/badge/Platform-Linux-8A2BE2" alt="Platform" />
  <img src="https://img.shields.io/badge/Use-Local%20Network%20Recon-red" alt="Use" />
</p>

`netrecon` — bu mahalliy tarmoqdagi faol qurilmalarni, SSH xizmatlarini, qurilma tipini taxmin qilish va potentsial VM/bridged hostlarni aniqlash uchun mo‘ljallangan LAN va SSH skanerlash vositasi.

Loyiha ichida bir xil funksionalni qo‘llovchi ikki versiya mavjud:

- `netrecon.py` — Python asosidagi versiya, ko‘p ipli skaner, JSON eksporti va yanada batafsil tahlil imkoniyatlari bilan
- `netrecon.sh` — Bash asosidagi versiya, tezkor ishlash va shell muhitida qulay foydalanish uchun optimallashtirilgan

## Asosiy funktsiyalar

- Mahalliy subnetdagi faol hostlarni avtomatik aniqlash
- `nmap` yordamida tarmoqni skanerlash
- SSH portlarini tekshirish (`22`, `2222`, `22222`)
- SSH bannerlarini o‘qib xizmat versiyasi va ma’lumotni aniqlash
- TTL bo‘yicha operatsion tizim turini taxmin qilish
- Reverse DNS / Avahi orqali host nomini aniqlash
- Duplikat MAC manzillarini aniqlash orqali VM yoki bridged qurilmalarni ko‘rsatish
- Natijalarni terminalda ko‘rinadigan shaklda chiqarish
- Batafsil ma’lumotni JSON faylga eksport qilish (`scan_report.json`)

## Nima uchun kerak?

Ushbu vosita quyidagi vazifalar uchun foydali:

- LAN ichidagi faol qurilmalarni aniqlash
- SSH xizmatlarini tekshirish
- Tizimlar va qurilmalar haqida qisman taxminiy ma’lumot olish
- Tarmoqni sinovdan o‘tkazish va lab muhitida tekshirish
- Mudofaa maqsadidagi tarmoq tadqiqotlari

## Repozitoriy strukturasi

```text
netrecon/
├── netrecon.py
├── netrecon.sh
├── README.md
├── scan_report.json    # Python versiyasi ishlaganda yaratilib chiqadi
└── requirements.txt    # agar keyinchalik qo'shilsa
```

## Talablar

Skriptlar root huquqlarini talab qiladi, chunki ular ARP/MAC ma’lumotlarini va mahalliy tarmoqga kirishni ishlatadi.

Kerakli dasturlar:

- Linux asosidagi tizim
- `sudo` yoki root kirishi
- `nmap`
- `ip` buyrug‘i (`iproute2` odatda shu paketda bo‘ladi)
- `ping`
- Python 3 (Python versiyasi uchun)
- Bash (Bash versiyasi uchun)

## Tez boshlash

### 1) Python versiyasi

```bash
sudo python3 netrecon.py --help
sudo python3 netrecon.py -s 192.168.1.0/24
sudo python3 netrecon.py --all
sudo python3 netrecon.py -o custom_report.json
```

### 2) Bash versiyasi

```bash
sudo bash netrecon.sh
sudo bash netrecon.sh -a
sudo bash netrecon.sh -s 192.168.1.0/24
```

## Flaglar va parametrlari

### Python versiyasi (`netrecon.py`)

- `-s, --subnet` — maxsus subnetni ko‘rsatish
- `--all` — barcha hostlarni (hatto SSH yopiq bo‘lganlarni ham) ko‘rsatish
- `-o, --output` — JSON natijalarini saqlash fayli
- `--help` — buyruqlar haqida ma’lumot

### Bash versiyasi (`netrecon.sh`)

- `-a, --all` — barcha hostlarni qamrab olish
- `-s, --subnet` — maxsus subnetni belgilash

## Misol natija

```text
[+] Active hosts discovered:
192.168.1.10   SSH Open   Linux   00:11:22:33:44:55
192.168.1.15   SSH Closed  Windows  66:77:88:99:AA:BB
192.168.1.20   SSH Open   Router   00:AA:BB:CC:DD:EE

[+] Duplicate MACs detected: possible bridged/VM environment
```

## Xavfsizlik va etika

Ushbu loyiha faqat quyidagi holatlar uchun mo‘ljallangan:

- ruxsat berilgan ichki tarmoq baholashlari
- laboratoriya muhitidagi sinovlar
- ta’lim maqsadlari
- mudofaa ustuvorlikdagi tarmoq xavfsizligi tadqiqotlari

Muhim: ushbu vositani sizga tegishli bo‘lmagan tarmoqlar yoki qurilmalar ustida ishlatmang. Har doim egadan yozma ruxsat oling.

## Eslatmalar

- Skriptlar asosan LAN va mahalliy tarmoqlar uchun mos keladi.
- Natijalar firewall qoidalari, segmentatsiya, optimizatsiya va host konfiguratsiyasiga qarab farq qilishi mumkin.
- Band tarmoqlarda to‘liq ko‘rinishni olish uchun `--all` yoki kengroq skanerlash parametrlaridan foydalaning.

## Muallif / loyiha haqida

Ushbu repozitoriyada bir xil kontseptsiya bo‘yicha ikkita amalga oshirish qo‘shilgan: mahalliy tarmoqda faol qurilmalarni aniqlash va SSH xizmatlari mavjudligini tekshirish. Python versiyasi ko‘proq batafsil tahlil va JSON hisobotlarini ishlab chiqadi, Bash versiyasi esa tez va qulay CLI ishlatish uchun yaratilgan.

## Litsenziya

Hozircha loyiha uchun aniq litsenziya mavjud emas. Agar loyiha ommaga ochiq tarzda taqdim etilsa, quyidagi litsenziyalardan birini qo‘shishni tavsiya qilamiz:

- MIT
- GPL
- Apache 2.0

## Taklif etilayotgan yaxshilanishlar

- Portlar bo‘yicha filtrlarni qo‘shish
- CSV eksportini qo‘shish
- IPv6 va zamonaviy tarmoq konfiguratsiyalarini qo‘llab-quvvatlash
- `nmap -A` bilan batafsil xizmat identifikatsiyasi
- Ko‘proq operatsion tizim turlarini aniqlash
- O‘rnatish uchun kichik install skriptini tayyorlash

---

Ushbu README fayl `netrecon.py` va `netrecon.sh` kodlari asosida tayyorlandi.
