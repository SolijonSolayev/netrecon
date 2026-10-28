# netrecon

Smart LAN & SSH reconnaissance toolkit for discovering live devices, open SSH services, OS hints, and potential VM/bridged hosts on a local network.

Repository description:
"Smart LAN & SSH reconnaissance toolkit for live host discovery and SSH security checks."

## Overview

This repository contains two versions of the same network reconnaissance tool:

- `netrecon.py` — Python implementation with threaded scanning, JSON export, and richer analytics
- `netrecon.sh` — Bash implementation optimized for quick CLI usage in shell environments

Both tools are designed to detect active hosts on the local subnet, identify SSH ports, inspect banners, estimate operating system type via TTL, and flag duplicate MAC addresses that often indicate bridged virtual machines.

## What the scripts do

- Detect the active local network subnet automatically
- Find live hosts in the network using `nmap`
- Scan for SSH ports (`22`, `2222`, `22222`)
- Read SSH banners and identify service versions
- Estimate OS family (Linux/Unix, Windows, Router) via ping TTL
- Resolve hostnames with reverse DNS / Avahi where available
- Highlight possible bridged VM environments using duplicate MAC detection
- Display summarized results in the terminal
- Export detailed results to JSON (`scan_report.json` by default)

## Repository structure

```text
netrecon/
├── netrecon.py
├── netrecon.sh
├── README.md
└── scan_report.json   # generated when running the Python version
```

## Requirements

The scripts require root privileges because they rely on ARP/MAC detection and local network access.

Prerequisites:

- Linux-based system
- `sudo` / root access
- `nmap`
- `ip` command (typically from `iproute2`)
- `ping`
- Python 3 (for the Python version)
- Bash (for the Bash version)

## Python version (`netrecon.py`)

### Features

- Multi-threaded host inspection
- Automatic subnet detection
- ANSI colorized terminal output
- JSON report export
- More detailed host analysis and classification

### Usage

```bash
sudo python3 netrecon.py --help
sudo python3 netrecon.py -s 192.168.1.0/24
sudo python3 netrecon.py --all
sudo python3 netrecon.py -o custom_report.json
```

### Example output

- Live host listing
- SSH open/closed status
- MAC + vendor information
- OS detection by TTL
- Potential Kali/Debian/Linux candidates
- Bridged VM hints

## Bash version (`netrecon.sh`)

### Features

- Lightweight shell implementation
- Automatic subnet discovery from route table
- Fast `nmap` based discovery and filtering
- Host tagging and scoring logic
- Human-friendly output for quick local assessments

### Usage

```bash
sudo bash netrecon.sh
sudo bash netrecon.sh -a
sudo bash netrecon.sh -s 192.168.1.0/24
```

### Flags

- `-a, --all` — show all hosts, including closed SSH devices
- `-s, --subnet` — force a custom subnet

## Security and ethical use

This project is intended for:

- authorized internal network assessments
- lab testing
- educational purposes
- defensive security research

Do not run it against networks or devices you do not own or do not have explicit permission to test.

## Notes

- The scripts are best suited for local networks and LAN environments.
- Results may vary depending on firewall rules, network segmentation, and host configuration.
- For full scanning visibility in busy networks, use `--all` or larger scan windows when appropriate.

## Author / project context

This repository combines two implementations of the same concept: a fast reconnaissance utility for identifying reachable devices and SSH-enabled hosts on a local network. The Python version is more feature-rich and suitable for automation and JSON reporting, while the shell version is simpler and faster to run from a terminal.

## License

This project does not currently declare a license. If you plan to distribute or publish it publicly, consider adding an appropriate open-source license such as MIT, GPL, or Apache 2.0.

## Suggested next improvements

- Add command-line filtering for specific ports or vendor names
- Add CSV export support
- Improve host detection for IPv6 and modern network setups
- Add optional service fingerprinting using `nmap -A`
- Add detection for more OS families and network appliances
- Create a small install script for dependencies

---

This README was prepared based on the code in both `netrecon.py` and `netrecon.sh`.
