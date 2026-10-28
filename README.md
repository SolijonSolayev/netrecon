# netrecon

Smart LAN va SSH ma'lumot olish (reconnaissance) uchun mo'ljallangan vosita. U mahalliy tarmoqdagi faol qurilmalarni topish, SSH xizmatlarini aniqlash, OS ko'rsatkichlarini baholash va potentsial VM/ko'priklangan hostlarni aniqlash imkonini beradi.

Repository description:
"Smart LAN & SSH reconnaissance toolkit for live host discovery and SSH security checks."

## Umumiy ma'lumot

Ushbu repositoriyada bir xil tarmoq skanerlash vositasining ikkita versiyasi mavjud:

- `netrecon.py` — Python asosidagi versiya, ko'p ipli skanerlash, JSON eksporti va kengroq tahlil imkoniyatlari bilan
- `netrecon.sh` — Bash asosidagi versiya, shell muhitida tezkor ishlatish uchun optimallashtirilgan

Ikkala skript ham mahalliy subnetdagi faol hostlarni aniqlash, SSH portlarini tekshirish, bannerlar o'qish, TTL orqali operatsion tizim turini taxmin qilish va duplikat MAC manzillarini aniqlash uchun ishlatiladi. Bu holatlar ko'pincha bridged VM yoki boshqa tarmoqdagi takroriy qurilmalarni ko'rsatadi.

## Skriptlar nima qiladi

- Avtomatik tarzda mahalliy tarmoq subnetini aniqlaydi
- `nmap` yordamida faol hostlarni qidiradi
- SSH portlarini skanerlaydi (`22`, `2222`, `22222`)
- SSH bannerlarini o'qib xizmat versiyalarini aniqlaydi
- Ping TTL bo'yicha OS turini taxmin qiladi (Linux/Unix, Windows, Router)
- Reverse DNS / Avahi orqali host nomlarini aniqlashga harakat qiladi
- Duplikat MAC aniqlash orqali potentsial bridged VM muhitlarini ko'rsatadi
- Natijalarni terminalda xulosali ko'rinishda chiqaradi
- Batafsil natijalarni JSON faylga (`scan_report.json` standart nom) eksport qiladi

## Repozitoriy strukturasi

```text
netrecon/
├── netrecon.py
├── netrecon.sh
├── README.md
└── scan_report.json   # Python versiyasi ishlaganda yaratiladi
```

## Talablar

Skriptlar root huquqlarini talab qiladi, chunki ular ARP/MAC aniqlash va mahalliy tarmoqga kirish imkoniyatlariga bog'liq.

Kerakli shartlar:

- Linux asosidagi tizim
- `sudo` / root kirishi
- `nmap`
- `ip` buyrug'i (odatda `iproute2` paketidan)
- `ping`
- Python 3 (Python versiyasi uchun)
- Bash (Bash versiyasi uchun)

## Python versiyasi (`netrecon.py`)

### Xususiyatlar

- Ko'p ipli host tekshiruvi
- Avtomatik subnet aniqlash
- ANSI rangli terminal chiqishi
- JSON hisobot eksporti
- Kengroq host tahlili va tasnifi

### Foydalanish

```bash
sudo python3 netrecon.py --help
sudo python3 netrecon.py -s 192.168.1.0/24
sudo python3 netrecon.py --all
sudo python3 netrecon.py -o custom_report.json
```

### Misol chiqishi

- Faol hostlar ro'yxati
- SSH ochiq/berkitilgan holat
- MAC va vendor ma'lumotlari
- TTL bo'yicha OS aniqlash
- Potentsial Kali/Debian/Linux nomzodlari
- Bridged VM ko'rsatkichlari

## Bash versiyasi (`netrecon.sh`)

### Xususiyatlar

- Yengil shell implementatsiyasi
- Route jadvalidan avtomatik subnet aniqlash
- Tez `nmap` asosidagi kashf etish va filtrlash
- Hostlarni taglash va ballar bilan baholash logikasi
- Tezkor mahalliy tarmoq baholash uchun qulay natijalar

### Foydalanish

```bash
sudo bash netrecon.sh
sudo bash netrecon.sh -a
sudo bash netrecon.sh -s 192.168.1.0/24
```

### Flaglar

- `-a, --all` — yopiq SSH xizmatlari bo'lgan barcha hostlarni ham ko'rsatadi
- `-s, --subnet` — maxsus subnetni majburlab belgilash

## Xavfsizlik va etika

Ushbu loyiha quyidagi maqsadlarda ishlatilishi uchun mo'ljallangan:

- ruxsat berilgan ichki tarmoq baholashlari
- laboratoriya sinovlari
- ta'lim maqsadlari
- mudofaa maqsadli xavfsizlik tadqiqotlari

Agar sizga tegishli bo'lmagan tarmoqlar yoki qurilmalar ustida unday skriptlarni ishlatmang. Avvalo ruxsat olish kerak.

## Eslatmalar

- Skriptlar asosan mahalliy tarmoqlar va LAN muhitlari uchun mos keladi.
- Natijalar firewall qoidalari, tarmoq segmentatsiyasi va host konfiguratsiyasiga qarab farq qilishi mumkin.
- Band tarmoqlarda to'liq ko'rinishga erishish uchun `--all` yoki kattaroq skanerlash oynalaridan foydalaning.

## Muallif / loyiha haqida

Ushbu repositoriyada bir xil konsepsiyaning ikki turdagi amaliyoti birlashtirilgan: mahalliy tarmoqda erishilgan qurilmalarni va SSH yoqilgan hostlarni aniqlash uchun tez skaner. Python versiyasi ko'proq keng tahlil hamda JSON xabarlarni taqdim etadi, Bash versiyasi esa tez va qulay CLI ishlatish uchun mo'ljallangan.

## Litsenziya

Ushbu loyiha hozircha litsenziya bayonini e'lon qilmagan. Agar siz uni ommaga tarqatmoqchi bo'lsangiz, MIT, GPL yoki Apache 2.0 kabi mos open-source litsenziyalarni qo'shishni ko'rib chiqing.

## Taklif etilayotgan keyingi yaxshilanishlar

- Ma'lum portlar yoki vendor nomlari bo'yicha buyruq satri filtrini qo'shish
- CSV eksportini qo'shish
- IPv6 va zamonaviy tarmoq sozlamalari uchun host aniqlashni yaxshilash
- `nmap -A` yordamida ixtiyoriy service fingerprinting qo'shish
- Ko'proq OS oilalari va tarmoq qurilmalari uchun aniqlashni kengaytirish
- Bog'liq dependency'lar uchun kichik o'rnatish skriptini yaratish

---

Ushbu README fayl `netrecon.py` va `netrecon.sh` kodlari asosida tayyorlandi.
