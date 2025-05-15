# AutoMegaETH 🐍⚡️

[![Build](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/username/automegaeth)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Next.js](https://img.shields.io/badge/next.js-13%2B-blue?logo=next.js)](https://nextjs.org/)
[![Python](https://img.shields.io/badge/python-3.10+-yellow?logo=python)](https://python.org/)
[![WebSocket](https://img.shields.io/badge/socket.io-integrated-black?logo=socket.io)](https://socket.io)

A fullstack DApp + Python auto-trading bot integrated with **Next.js + Socket.IO + Uniswap + Python scripts**.

---

## 🧩 Project Structure
├── scripts/ # Python automation scripts
│ ├── auto_LP.py
│ ├── auto_swap.py
│ ├── auto_swap_lp.py
│ └── token_outs.py # Token output configuration
├── pages/
│ ├── api/
│ │ ├── run.ts # REST API to run python scripts
│ │ └── socket_io.ts # Socket.IO server to stream real-time output
├── cli.js # CLI tool to start/stop/status bot scripts
├── logs/ # Output logs from CLI (auto generated)
├── public/
├── .gitignore
├── README.md
├── next.config.js
└── tsconfig.json


---

## 🚀 Cara Menjalankan

### 1. Install dependency Node.js & Python
# dan pastikan node.js dan python3 sudah terinstall

npm install

✅ Melalui WEB Localhost
🧠 Jalankan server
npm run dev

# Buka http://localhost:3000

✅ Melalui CLI (terminal)
🧠 Jalankan Bot Auto-Trade
node cli.js auto swap       # auto swap
node cli.js auto lp         # auto LP
node cli.js auto swap_lp    # gabungan swap + LP
node cli.js stop            # hentikan proses berjalan
node cli.js status          # lihat status proses

