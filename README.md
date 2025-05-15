# AutoMegaETH 🐍⚡

A fullstack DApp + Python auto-trading bot integrated with **Next.js** + **Socket.IO** + **Uniswap** + **Python scripts**.

[![Build](https://img.shields.io/badge/build-passing-brightgreen)]() [![License](https://img.shields.io/badge/license-MIT-blue.svg)]() [![Next.js](https://img.shields.io/badge/next.js-13%2B-black)]() [![Python](https://img.shields.io/badge/python-3.10%2B-blue)]() [![Socket.IO](https://img.shields.io/badge/socket.io-integrated-lightgrey)]()

---

## 🚀 Cara Menjalankan

### 1. Install dependency

Pastikan `Node.js` dan `Python 3` sudah terinstal di sistem kamu.

✅ macOS (pakai Homebrew – disarankan)
```bash
brew install node
```
```bash
brew install pyhton3
```
✅ Windows
Buka: https://nodejs.org
Download LTS version
Klik install seperti biasa (next-next).

Buka: https://www.python.org/downloads/
Download dan install.
Centang "Add Python to PATH" saat instalasi.

✅ Ubuntu / Linux
```bash
sudo apt update
sudo apt install nodejs npm
```
```bash
sudo apt update
sudo apt install python3 python3-pip
```

✅ Setelah Install Node.js dan pyhton3
copy project ke local directory
```bash
https://github.com/thomasalfa12/automegaeth.git
```
or
```bash
gh repo clone thomasalfa12/automegaeth
```
setelah terinstal, di root cli run:
```bash
npm install
```
---

### ✅ Jalankan Web (UI)

Untuk membuka dashboard bot auto-trading:

```bash
npm run dev
```

Lalu buka di browser:  
👉 [http://localhost:3000](http://localhost:3000)

---

### 🧠 Jalankan CLI (Terminal)

Menjalankan bot Python secara manual via command line:

```bash
# Menjalankan bot swap
node cli.js auto swap

# Menjalankan bot LP
node cli.js auto lp

# Gabungan swap + LP
node cli.js auto swap_lp

# Hentikan proses yang sedang berjalan
node cli.js stop

# Lihat status proses
node cli.js status
```

> Semua perintah di atas akan menjalankan script Python di folder `scripts/`.

---

## 📁 Struktur Project (Singkat)

- `scripts/` — Bot Python: swap, LP, dan kombinasi  
- `cli.js` — CLI tool untuk start/stop bot  
- `run.ts` — API untuk menjalankan script dari Web  
- `socket_io.ts` — WebSocket untuk real-time logs  
- `logs/` — Auto-generated CLI logs  
- `pages/`, `public/`, `api/` — Next.js Web Interface

---

## 📄 .env File

Buat file `.env` di root:

```env
PRIVATE_KEY=0x...
RPC_URL="https://carrot.megaeth.com/rpc"
CHAIN_ID=6342
ROUTER_ADDRESS="0xa6b579684e943f7d00d616a48cf99b5147fc57a5"
```

---

Jika kamu butuh live log dari bot ke UI, pastikan server `npm run dev` sedang berjalan.

## UNTUK MENAMBAH JENIS TOKEN YANG AKAN DI TRADE, 
/script/token_outs.py => add sc token, hindari token low liquidity
---
### 🚀 Roadmap Fitur AutoMegaETH

Fitur-fitur yang sedang direncanakan & dikembangkan untuk memperkuat ekosistem trading otomatis ini:

#### ✅ Fitur Selesai

* [x] **Auto LP**: Tambah liquidity otomatis ke token tertentu.
* [x] **Auto Swap**: Swap token tertentu secara otomatis.
* [x] **Gabungan Swap + LP** (`auto_swap_lp`).
* [x] CLI start/stop/status untuk menjalankan bot via terminal.
* [x] Integrasi realtime log dengan Socket.IO dan antarmuka Next.js.

#### 🔄 Dalam Progres

* [ ] **Auto-Remove LP**: Secara otomatis menarik liquidity pool berdasarkan kondisi tertentu (misalnya target profit).
* [ ] **Auto-Sell Trending Token**: Pantau token trending (via Dextools, GeckoTerminal API) & auto-sell saat pump terdeteksi.
* [ ] **Auto-Pump Detector**: Deteksi volume naik signifikan dan eksekusi buy/sell.
* [ ] **Limit/Stop-Loss Auto Swap**: Eksekusi swap jika token mencapai harga tertentu (limit order).
* [ ] **Log Viewer Web UI**: Antarmuka real-time untuk melihat hasil log langsung dari browser.

#### 🧠 Eksperimen & Ide Masa Depan

* [ ] **Sniper Bot (gas boost)**: Otomatis beli token segera setelah liquidity ditambahkan.
* [ ] **Auto Telegram Alerts**: Kirim notifikasi ke Telegram untuk setiap aksi (buy, sell, remove LP).
* [ ] **Web Dashboard Bot Controller**: Jalankan & monitor semua bot langsung dari UI web.
* [ ] **Profit Tracker**: Hitung dan tampilkan keuntungan total dari seluruh aktivitas.

