#!/usr/bin/env bash

# Ranglar
BOLD='\033[1m'
DIM='\033[2m'
CYAN='\033[96m'
GREEN='\033[92m'
YELLOW='\033[93m'
RED='\033[91m'
MAGENTA='\033[95m'
NC='\033[0m'

SHOW_ALL=false
CUSTOM_SUBNET=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -a|--all) SHOW_ALL=true; shift ;;
        -s|--subnet) CUSTOM_SUBNET="$2"; shift 2 ;;
        *) shift ;;
    esac
done

if [[ "$EUID" -ne 0 ]]; then
    echo -e "${RED}[!] Skriptni sudo bilan ishga tushiring: sudo $0${NC}"
    exit 1
fi

# 1. Haqiqiy Wi-Fi/LAN subnetni ANIQ topish (ip route orqali)
if [[ -n "$CUSTOM_SUBNET" ]]; then
    SUBNET="$CUSTOM_SUBNET"
    MY_IP="Manual"
else
    # Internetga chiqadigan asosiy interfeysni aniqlash
    DEFAULT_IFACE=$(ip route show default | awk '/default/ {print $5; exit}')
    if [[ -n "$DEFAULT_IFACE" ]]; then
        # Kernel route jadvalidan aniq subnetni olish (masalan: 172.16.204.0/24)
        SUBNET=$(ip route show dev "$DEFAULT_IFACE" proto kernel scope link | awk '{print $1; exit}')
        MY_IP=$(ip route show dev "$DEFAULT_IFACE" proto kernel scope link | awk '{for(i=1;i<=NF;i++) if($i=="src") print $(i+1); exit}')
    fi
    # Agar topilmasa fallback:
    [[ -z "$SUBNET" ]] && SUBNET="172.16.204.0/24"
fi

echo -e "${CYAN}${BOLD}⚡ ANIQ LAN & SSH SKANER (Fixed Bash Edition)${NC}"
echo -e "${CYAN}[i] Interfeys:${NC} ${DEFAULT_IFACE:-Auto} | ${CYAN}Sizning IP:${NC} ${BOLD}${MY_IP}${NC} | ${CYAN}Subnet:${NC} ${BOLD}${SUBNET}${NC}"

TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

# 2. Nmap bilan faol qurilmalar VA 22, 2222 portlarni BIR VAQTDA skanerlash
# (/dev/tcp o'rniga Nmapning o'zi ishlatiladi — 10 barobar tez va aniq)
echo -e "${YELLOW}[*] Tarmoq va SSH portlar skanerlanmoqda...${NC}"
nmap -n -PS22,2222 -p 22,2222 --version-light -sV -T4 "$SUBNET" -oN "$TMP_DIR/nmap_norm.txt" >/dev/null 2>&1

# 3. Nmap natijasidan faqat HAQIQIY IP, MAC, Vendor va SSH holatini ajratib olish
awk '
/^Nmap scan report for / {
    if (ip != "") print ip "|" mac "|" vendor "|" ssh_open "|" ports "|" banner;
    ip = $NF; gsub(/[()]/, "", ip);
    mac = "LOCALHOST"; vendor = "O\x27z qurilmangiz";
    ssh_open = 0; ports = "Closed"; banner = "-";
}
/^22\/tcp[ \t]+open/ || /^2222\/tcp[ \t]+open/ {
    ssh_open = 1;
    split($1, p, "/");
    ports = (ports == "Closed" ? p[1] : ports "," p[1]);
    b = "";
    for (i=4; i<=NF; i++) b = b $i " ";
    if (b == "") b = "SSH Open";
    banner = (banner == "-" ? "[" p[1] "] " b : banner " | [" p[1] "] " b);
}
/^MAC Address:/ {
    mac = $3;
    vendor = "";
    for (i=4; i<=NF; i++) vendor = vendor $i (i==NF ? "" : " ");
    gsub(/^\(|\)$/, "", vendor);
}
END {
    if (ip != "") print ip "|" mac "|" vendor "|" ssh_open "|" ports "|" banner;
}
' "$TMP_DIR/nmap_norm.txt" > "$TMP_DIR/parsed_hosts.txt"

TOTAL_HOSTS=$(wc -l < "$TMP_DIR/parsed_hosts.txt")
if [[ "$TOTAL_HOSTS" -eq 0 ]]; then
    echo -e "${RED}[-] Hech qanday faol qurilma topilmadi!${NC}"
    exit 0
fi

# 4. Dublikat MAC manzillarni (Bridged VM) aniqlash
cut -d'|' -f2 "$TMP_DIR/parsed_hosts.txt" | grep -v "LOCALHOST" | sort | uniq -d > "$TMP_DIR/dup_macs.txt"
DUP_COUNT=$(wc -l < "$TMP_DIR/dup_macs.txt")

echo -e "${GREEN}[+] ${TOTAL_HOSTS} ta haqiqiy qurilma topildi. OS (TTL) tekshirilmoqda...${NC}\n"

# 5. TTL (Linux vs Windows) ni parallel tekshirish
check_ttl() {
    local line="$1"
    local ip mac vendor ssh_open ports banner
    IFS='|' read -r ip mac vendor ssh_open ports banner <<< "$line"

    local ping_out ttl os_str
    ping_out=$(ping -c 1 -W 1 "$ip" 2>/dev/null)
    ttl=$(echo "$ping_out" | grep -oEi 'ttl=[0-9]+' | cut -d= -f2 | head -n1)

    if [[ -z "$ttl" ]]; then
        os_str="Unknown"
    elif (( ttl <= 64 )); then
        os_str="Linux/Unix ($ttl)"
    elif (( ttl <= 128 )); then
        os_str="Windows ($ttl)"
    else
        os_str="Router ($ttl)"
    fi

    # Teglar va Ball (Kali/VM aniqlash)
    local tags=""
    local score=0

    if grep -qFx "$mac" "$TMP_DIR/dup_macs.txt" 2>/dev/null; then
        tags+="[BRIDGED-VM?] "
        ((score+=2))
    fi
    [[ "$os_str" == Linux* ]] && ((score+=1))
    (( ssh_open == 1 )) && ((score+=2))

    if echo "$banner" | grep -qiE "debian|kali"; then
        tags+="[DEBIAN/KALI!] "
        ((score+=3))
    elif echo "$banner" | grep -qi "ubuntu"; then
        tags+="[UBUNTU] "
    fi

    echo "${ip}|${ssh_open}|${ports}|${os_str}|${mac}|${vendor}|${banner}|${tags}|${score}" > "$TMP_DIR/host_${ip}.txt"
}

while IFS= read -r line; do
    check_ttl "$line" &
done < "$TMP_DIR/parsed_hosts.txt"
wait

# Natijalarni IP bo'yicha saralash
cat "$TMP_DIR"/host_*.txt | sort -t . -k 1,1n -k 2,2n -k 3,3n -k 4,4n > "$TMP_DIR/final.txt"

# 6. Jadvalni chiqarish
printf "═%.0s" {1..115}; echo ""
printf "${BOLD}%-16s %-10s %-17s %-19s %-24s %s${NC}\n" "IP MANZIL" "SSH PORT" "OS (TTL)" "MAC MANZIL" "VENDOR" "BANNER & BELGILAR"
printf "═%.0s" {1..115}; echo ""

SSH_COUNT=0
KALI_LIST=()

while IFS='|' read -r ip ssh_open ports os_str mac vendor banner tags score; do
    (( ssh_open == 1 )) && ((SSH_COUNT++))
    (( score >= 3 )) && KALI_LIST+=("${score}|${ip}|${ports}|${os_str}|${banner}|${tags}")

    if [[ "$SHOW_ALL" == false ]] && (( ssh_open == 0 )) && [[ "$tags" != *"BRIDGED-VM?"* ]]; then
        continue
    fi

    short_vendor="${vendor:0:22}"
    if (( ssh_open == 1 )); then
        COLOR="$GREEN"
        p_txt="Port $ports"
    elif [[ "$tags" == *"BRIDGED-VM?"* ]]; then
        COLOR="$YELLOW"
        p_txt="Closed"
    else
        COLOR="$DIM"
        p_txt="Closed"
    fi

    printf "${COLOR}%-16s %-10s %-17s %-19s %-24s${NC} %s ${MAGENTA}%s${NC}\n" \
        "$ip" "$p_txt" "$os_str" "$mac" "$short_vendor" "$banner" "$tags"
done < "$TMP_DIR/final.txt"

printf "═%.0s" {1..115}; echo ""

echo -e "\n${BOLD}📊 XULOSA:${NC} Jami faol: ${BOLD}${TOTAL_HOSTS} ta${NC} | SSH ochiq: ${GREEN}${BOLD}${SSH_COUNT} ta${NC} | Bridged VM juftliklar: ${YELLOW}${BOLD}${DUP_COUNT} ta${NC}"

if (( DUP_COUNT > 0 )); then
    echo -e "\n${YELLOW}${BOLD}🔍 DUBLIKAT MAC (VIRTUAL MASHINA EHTIMOLI):${NC}"
    while read -r dmac; do
        ips=$(grep "$dmac" "$TMP_DIR/final.txt" | awk -F'|' '{printf "%s (%s, SSH:%s)  ", $1, $4, $3}')
        echo -e "  └── MAC: ${CYAN}${dmac}${NC} ➔  ${ips}"
    done < "$TMP_DIR/dup_macs.txt"
fi

if (( ${#KALI_LIST[@]} > 0 )); then
    echo -e "\n${GREEN}${BOLD}🎯 ASOSIY NISHONLAR (KALI / LINUX):${NC}"
    while IFS='|' read -r sc ip prt ost bnr tgs; do
        echo -e "  ★ ${BOLD}${ip}${NC} | SSH: ${GREEN}${prt}${NC} | OS: ${ost} | ${CYAN}${bnr}${NC} ${MAGENTA}${tgs}${NC}"
    done < <(printf "%s\n" "${KALI_LIST[@]}" | sort -t'|' -k1,1nr)
fi
