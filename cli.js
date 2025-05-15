#!/usr/bin/env node

const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

const [,, command, arg] = process.argv;

const scriptMap = {
  lp: "scripts/auto_LP.py",
  swap: "scripts/auto_swap.py",
  swap_lp: "scripts/auto_swap_lp.py",
};

const pidFile = ".pid";
const logsDir = "logs";

// Utility: cek apakah proses masih hidup
function isRunning(pid) {
  try {
    process.kill(pid, 0);
    return true;
  } catch (e) {
    return false;
  }
}

function showHelp() {
  console.log(`
❌ Perintah tidak dikenal.

✅ Gunakan:
  auto swap       - Menjalankan auto swap
  auto lp         - Menjalankan auto LP
  auto swap_lp    - Menjalankan gabungan swap dan LP
  stop            - Menghentikan proses yang sedang berjalan
  status          - Cek status proses yang sedang berjalan
`);
}

function ensureLogsDir() {
  if (!fs.existsSync(logsDir)) {
    fs.mkdirSync(logsDir);
  }
}

// Jalankan proses auto trading
if (command === "auto" && scriptMap[arg]) {
  if (fs.existsSync(pidFile)) {
    const existingPid = parseInt(fs.readFileSync(pidFile).toString(), 10);
    if (isRunning(existingPid)) {
      console.log("⚠️ Masih ada proses berjalan. Jalankan 'stop' dulu.");
      process.exit(1);
    } else {
      fs.unlinkSync(pidFile); // bersihkan pid file lama
    }
  }

  ensureLogsDir();

  const script = scriptMap[arg];
  const outLog = fs.openSync(path.join(logsDir, `${arg}.out.log`), 'a');
  const errLog = fs.openSync(path.join(logsDir, `${arg}.err.log`), 'a');

  const child = spawn("python3", ["-u", script], {
    detached: true,
    stdio: ['ignore', outLog, errLog],
  });

  fs.writeFileSync(pidFile, child.pid.toString());
  console.log(`🚀 Menjalankan ${arg} (PID: ${child.pid})`);
  console.log(`📄 Log output: ${logsDir}/${arg}.out.log`);

  child.unref();

} else if (command === "stop") {
  if (fs.existsSync(pidFile)) {
    const pid = parseInt(fs.readFileSync(pidFile).toString(), 10);
    try {
      process.kill(pid);
      console.log(`🛑 Proses (PID: ${pid}) berhasil dihentikan`);
      fs.unlinkSync(pidFile);
    } catch (err) {
      console.error("❌ Gagal menghentikan proses:", err.message);
    }
  } else {
    console.log("ℹ️ Tidak ada proses yang sedang berjalan.");
  }

} else if (command === "status") {
  if (fs.existsSync(pidFile)) {
    const pid = parseInt(fs.readFileSync(pidFile).toString(), 10);
    if (isRunning(pid)) {
      console.log(`✅ Proses sedang berjalan (PID: ${pid})`);
    } else {
      console.log("⚠️ PID tersimpan tapi proses sudah mati. Menghapus .pid.");
      fs.unlinkSync(pidFile);
    }
  } else {
    console.log("ℹ️ Tidak ada proses yang sedang berjalan.");
  }

} else {
  showHelp();
}
