import { Server } from "socket.io";
import { spawn } from "child_process";

const pidMap: Record<string, any> = {};

export const config = {
  api: {
    bodyParser: false,
  },
};

export default function handler(req: any, res: any) {
  if (!res.socket.server.io) {
    const io = new Server(res.socket.server, {
      path: "/api/socket_io",
      // cors: { origin: "*" }, // Optional kalau perlu akses dari domain lain
    });

    res.socket.server.io = io;

    io.on("connection", (socket) => {
      console.log("✅ Socket connected", socket.id);

      socket.on("start-script", (type: string) => {
        const scriptMap = {
          swap: "scripts/auto_swap.py",
          lp: "scripts/auto_LP.py",
          swap_lp: "scripts/auto_swap_lp.py",
        };

        const scriptPath = scriptMap[type];
        if (!scriptPath) {
          socket.emit("output", `❌ Unknown script: ${type}`);
          return;
        }

        if (pidMap[type]) {
          socket.emit("output", `⚠️ Script '${type}' already running`);
          return;
        }

        const child = spawn("python3", ["-u", scriptPath], {
  env: { ...process.env, PYTHONPATH: process.cwd() }
});


        pidMap[type] = child;

        child.stdout.on("data", (data) => {
          socket.emit("output", data.toString());
        });

        child.stderr.on("data", (data) => {
          socket.emit("output", "⚠️ Error: " + data.toString());
        });

        child.on("close", (code) => {
          socket.emit("output", `👋 Script '${type}' finished with code ${code}`);
          delete pidMap[type];
        });
      });

      socket.on("stop-script", (type: string) => {
        if (pidMap[type]) {
          pidMap[type].kill();
          delete pidMap[type];
          socket.emit("output", `🛑 Script '${type}' stopped`);
        } else {
          socket.emit("output", `ℹ️ No running script for '${type}'`);
        }
      });
    });
  }

  res.end();
}
