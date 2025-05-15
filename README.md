# AutoMegaETH 🐍⚡

A fullstack DApp + Python auto-trading bot integrated with **Next.js** + **Socket.IO** + **Uniswap** + **Python scripts**.

[![Build](https://img.shields.io/badge/build-passing-brightgreen)]() [![License](https://img.shields.io/badge/license-MIT-blue.svg)]() [![Next.js](https://img.shields.io/badge/next.js-13%2B-black)]() [![Python](https://img.shields.io/badge/python-3.10%2B-blue)]() [![Socket.IO](https://img.shields.io/badge/socket.io-integrated-lightgrey)]()

---

## 🚀 Cara Menjalankan

### 1. Install dependency

Pastikan `Node.js` dan `Python 3` sudah terinstal di sistem kamu.

```bash
npm install
npm run dev

Lalu buka di browser:
👉 http://localhost:3000

🧠 Jalankan CLI (Terminal)
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

📄 .env File
Buat file .env di root:
PRIVATE_KEY=0x...
RPC_URL=https://...
CHAIN_ID=...
ROUTER_ADDRESS=0x...
