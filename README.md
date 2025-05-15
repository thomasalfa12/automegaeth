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

✅ Setelah Install Node

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
RPC_URL=https://...
CHAIN_ID=...
ROUTER_ADDRESS=0x...
```

---

Jika kamu butuh live log dari bot ke UI, pastikan server `npm run dev` sedang berjalan.
