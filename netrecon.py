#!/usr/bin/env python3
import os
import sys
import re
import json
import socket
import subprocess
import argparse
from datetime import datetime
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

# ANSI Ranglar va dizayn
class UI:
    BG_BLUE = '\033[44m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'

SSH_PORTS = [22, 2222, 22222]

def print_banner():
    banner = f"""{UI.CYAN}{UI.BOLD}
    ╔══════════════════════════════════════════════════════════════════════╗
    ║   ⚡ SMART LAN & SSH RECONNAISSANCE TOOL v2.0                        ║
    ║   Auto-Subnet • Multi-Port SSH • OS Fingerprinting • VM Detector     ║
    ╚══════════════════════════════════════════════════════════════════════╝{UI.RESET}"""
    print(banner)

def get_default_subnet():
    """Faol tarmoq interfeysi va subnetni avtomatik aniqlash"""
    try:
        out = subprocess.check_output(["ip", "-o", "-f", "inet", "addr", "show"], text=True)
        for line in out.splitlines():
            if "scope global" in line and not any(x in line for x in ["docker", "br-", "veth", "virbr", "tun"]):
                match = re.search(r'inet\s+(\d+\.\d+\.\d+\.\d+/\d+)', line)
                if match:
                    ip_cidr = match.group(1)
                    ip_parts = ip_cidr.split('/')[0].split('.')
                    cidr = ip_cidr.split('/')[1]
                    return f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/{cidr}", ip_cidr.split('/')[0]
    except Exception:
        pass
    return "172.16.204.0/24", "Unknown"

def discover_hosts(subnet):
    """Nmap ARP skaneri orqali barcha faol qurilmalarni tezda topish"""
    print(f"{UI.YELLOW}[*] Tarmoq skanerlanmoqda:{UI.RESET} {UI.BOLD}{subnet}{UI.RESET} ...")
    cmd = ["nmap", "-sn", "-n", "-T4", subnet]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    hosts = []
    current_ip = None
    for line in result.stdout.splitlines():
        if "Nmap scan report for" in line:
            current_ip = line.split()[-1].strip("()")
            hosts.append({"ip": current_ip, "mac": "LOCALHOST", "vendor": "O'z qurilmangiz"})
        elif "MAC Address:" in line and current_ip:
            parts = line.split("MAC Address: ")[1].split(" ", 1)
            mac = parts[0].strip()
            vendor = parts[1].strip("()") if len(parts) > 1 else "Unknown"
            hosts[-1]["mac"] = mac
            hosts[-1]["vendor"] = vendor
    return hosts

def get_ttl_and_os(ip):
    """Ping TTL orqali Operatsion Tizim oilasini aniqlash"""
    try:
        res = subprocess.run(["ping", "-c", "1", "-W", "1", ip], capture_output=True, text=True)
        match = re.search(r'ttl=(\d+)', res.stdout, re.IGNORECASE)
        if match:
            ttl = int(match.group(1))
            if ttl <= 64:
                return ttl, "Linux/Unix"
            elif ttl <= 128:
                return ttl, "Windows"
            else:
                return ttl, "Network/Router"
    except Exception:
        pass
    return 0, "Unknown"

def resolve_hostname(ip):
    """Reverse DNS va mDNS (kali.local kabi) nomlarni aniqlash"""
    try:
        host, _, _ = socket.gethostbyaddr(ip)
        return host
    except Exception:
        pass
    try:
        res = subprocess.run(["avahi-resolve", "-a", ip], capture_output=True, text=True, timeout=1.2)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.split()[-1]
    except Exception:
        pass
    return "-"

def probe_ssh_port(ip, port, timeout=1.5):
    """Socket orqali SSH portni va uning bannerini o'qish"""
    try:
        with socket.create_connection((ip, port), timeout=timeout) as s:
            s.settimeout(timeout)
            try:
                banner = s.recv(1024).decode('utf-8', errors='ignore').strip()
            except Exception:
                banner = "SSH Open (No Banner)"
            # Toza birinchi qatorni olish
            banner = banner.splitlines()[0] if banner else "SSH Open"
            return True, banner
    except Exception:
        return False, ""

def analyze_host(host, dup_macs):
    """Har bir hostni chuqur tahlil qilish (Thread worker)"""
    ip = host["ip"]
    mac = host["mac"]
    vendor = host["vendor"]
    
    ttl, os_guess = get_ttl_and_os(ip)
    hostname = resolve_hostname(ip)
    
    open_ssh = []
    banners = []
    for port in SSH_PORTS:
        is_open, banner = probe_ssh_port(ip, port)
        if is_open:
            open_ssh.append(str(port))
            banners.append(f"[{port}] {banner}")
            
    banner_str = " | ".join(banners) if banners else "-"
    
    # Kali Linux / VM ehtimolini hisoblash (Smart Scoring)
    tags = []
    score = 0
    
    if mac in dup_macs and mac != "LOCALHOST":
        tags.append("BRIDGED-VM?")
        score += 2
    if os_guess == "Linux/Unix":
        score += 1
    if open_ssh:
        score += 2
    if any(k in banner_str.lower() for k in ["debian", "kali"]):
        tags.append("DEBIAN/KALI-SSH")
        score += 3
    elif "ubuntu" in banner_str.lower():
        tags.append("UBUNTU-SSH")
    if "kali" in hostname.lower():
        tags.append("KALI-HOST!")
        score += 4

    host.update({
        "ttl": ttl,
        "os": os_guess,
        "hostname": hostname,
        "ssh_ports": ", ".join(open_ssh) if open_ssh else "Closed",
        "ssh_open": bool(open_ssh),
        "banner": banner_str,
        "tags": tags,
        "score": score
    })
    return host

def ip_sort_key(host):
    return [int(x) for x in host["ip"].split(".")]

def main():
    parser = argparse.ArgumentParser(description="Smart LAN & SSH Scanner")
    parser.add_argument("-s", "--subnet", help="Tarmoq diapazoni (masalan: 172.16.204.0/24)")
    parser.add_argument("-t", "--threads", type=int, default=40, help="Parallel oqimlar soni (default: 40)")
    parser.add_argument("--all", action="store_true", help="SSH yopiq qurilmalarni ham to'liq jadvalda ko'rsatish")
    parser.add_argument("-o", "--output", default="scan_report.json", help="Natijani JSON faylga saqlash")
    args = parser.parse_args()

    if os.geteuid() != 0:
        print(f"{UI.RED}[!] Diqqat: ARP va MAC manzillarni aniqlash uchun skriptni sudo bilan ishga tushiring!{UI.RESET}")
        print(f"    Ishga tushirish: {UI.BOLD}sudo python3 {sys.argv[0]}{UI.RESET}")
        sys.exit(1)

    print_banner()
    
    auto_subnet, my_ip = get_default_subnet()
    subnet = args.subnet if args.subnet else auto_subnet
    print(f"{UI.CYAN}[i] Sizning IP manzilingiz:{UI.RESET} {my_ip} | {UI.CYAN}Oqimlar (Threads):{UI.RESET} {args.threads}")

    start_time = datetime.now()
    raw_hosts = discover_hosts(subnet)
    
    if not raw_hosts:
        print(f"{UI.RED}[-] Tarmoqda faol qurilmalar topilmadi.{UI.RESET}")
        sys.exit(0)

    # Dublikat MAC manzillarni topish (VirtualBox/VMware Bridged rejimi uchun)
    mac_counts = Counter(h["mac"] for h in raw_hosts if h["mac"] != "LOCALHOST")
    dup_macs = {mac for mac, count in mac_counts.items() if count > 1}

    print(f"{UI.GREEN}[+] {len(raw_hosts)} ta faol qurilma topildi.{UI.RESET} Chuqur tahlil (SSH, TTL, OS, VM) boshlandi...\n")

    analyzed_hosts = []
    completed = 0
    total = len(raw_hosts)

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {executor.submit(analyze_host, h, dup_macs): h for h in raw_hosts}
        for future in as_completed(futures):
            completed += 1
            analyzed_hosts.append(future.result())
            # Jonli Progress Bar
            pct = int((completed / total) * 100)
            bar = "█" * (pct // 4) + "░" * (25 - (pct // 4))
            sys.stdout.write(f"\r{UI.CYAN}[Jarayon] [{bar}] {pct}% ({completed}/{total} tekshirildi){UI.RESET}")
            sys.stdout.flush()

    print("\n\n" + "═" * 115)
    print(f"{UI.BOLD}{'IP MANZIL':<16} {'SSH PORT':<10} {'OS (TTL)':<15} {'MAC MANZIL':<19} {'VENDOR / HOSTNAME':<26} {'BANNER & MAXSUS BELGILAR'}{UI.RESET}")
    print("═" * 115)

    # IP bo'yicha tartiblash
    analyzed_hosts.sort(key=ip_sort_key)

    ssh_open_list = []
    kali_candidates = []

    for h in analyzed_hosts:
        if h["ssh_open"]:
            ssh_open_list.append(h)
        if h["score"] >= 3:
            kali_candidates.append(h)

        # Agar --all berilmagan bo'lsa, faqat SSH ochiqlarni yoki shubhali VM/Linuxlarni ko'rsatish
        if not args.all and not h["ssh_open"] and "BRIDGED-VM?" not in h["tags"]:
            continue

        ip_str = h["ip"]
        ssh_str = f"Port {h['ssh_ports']}" if h["ssh_open"] else "Closed"
        os_str = f"{h['os']} ({h['ttl']})" if h["ttl"] else h["os"]
        mac_str = h["mac"]
        
        vend_host = h["hostname"] if h["hostname"] != "-" else h["vendor"]
        vend_host = (vend_host[:23] + "..") if len(vend_host) > 25 else vend_host

        tag_str = " ".join([f"[{t}]" for t in h["tags"]])
        info_str = f"{h['banner']} {UI.MAGENTA}{tag_str}{UI.RESET}".strip()

        # Rangli ajratish
        if h["ssh_open"]:
            row_color = UI.GREEN
        elif "BRIDGED-VM?" in h["tags"]:
            row_color = UI.YELLOW
        else:
            row_color = UI.DIM

        print(f"{row_color}{ip_str:<16} {ssh_str:<10} {os_str:<15} {mac_str:<19} {vend_host:<26}{UI.RESET} {info_str}")

    print("═" * 115)

    # Xulosa va Analitika bo'limi
    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"\n{UI.BOLD}📊 SKANERLASH XULOSASI ({elapsed:.1f} soniyada yakunlandi):{UI.RESET}")
    print(f"  • Jami faol qurilmalar : {UI.BOLD}{len(analyzed_hosts)} ta{UI.RESET}")
    print(f"  • SSH yoqilganlari     : {UI.GREEN}{UI.BOLD}{len(ssh_open_list)} ta{UI.RESET}")
    print(f"  • Dublikat MAC (VM?)   : {UI.YELLOW}{UI.BOLD}{len(dup_macs)} ta juftlik{UI.RESET}")

    if dup_macs:
        print(f"\n{UI.YELLOW}{UI.BOLD}🔍 VIRTUAL MASHINA (BRIDGED MODE) EHTIMOLI BO'LGAN QURILMALAR:{UI.RESET}")
        for mac in dup_macs:
            same_mac_hosts = [x for x in analyzed_hosts if x["mac"] == mac]
            ips_info = ", ".join([f"{x['ip']} ({x['os']}, SSH:{x['ssh_ports']})" for x in same_mac_hosts])
            print(f"  └── MAC: {UI.CYAN}{mac}{UI.RESET} ({same_mac_hosts[0]['vendor']}) ➔  {ips_info}")

    if kali_candidates:
        print(f"\n{UI.GREEN}{UI.BOLD}🎯 NISHON (KALI / DEBIAN LINUX) BO'LISHI MUMKIN BO'LGAN ENG KUCHLI NOMZODLAR:{UI.RESET}")
        for kc in sorted(kali_candidates, key=lambda x: x["score"], reverse=True):
            print(f"  ★ {UI.BOLD}{kc['ip']:<15}{UI.RESET} | SSH: {kc['ssh_ports']:<6} | OS: {kc['os']:<10} | Banner: {UI.CYAN}{kc['banner']}{UI.RESET} {' '.join(kc['tags'])}")

    # JSON faylga saqlash
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(analyzed_hosts, f, indent=4, ensure_ascii=False)
        print(f"\n{UI.DIM}[✓] To'liq hisobot '{args.output}' fayliga saqlandi. (Barcha 80+ qurilmani ko'rish uchun '--all' qo'shib ishga tushiring){UI.RESET}")
    except Exception as e:
        print(f"{UI.RED}[!] Faylga saqlashda xatolik: {e}{UI.RESET}")

if __name__ == "__main__":
    main()
