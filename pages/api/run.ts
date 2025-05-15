// pages/api/run.ts
import type { NextApiRequest, NextApiResponse } from "next";
import { spawn } from "child_process";
import path from "path";

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") return res.status(405).end("Method Not Allowed");

  const { type } = req.body;

  const scriptMap: Record<string, string> = {
    swap: "scripts/auto_swap.py",
    lp: "scripts/auto_LP.py",
    swap_lp: "scripts/auto_swap_lp.py",
  };

  const script = scriptMap[type];
  if (!script) return res.status(400).json({ error: "Jenis tidak dikenali." });

  const fullPath = path.join(process.cwd(), script);
  const proc = spawn("python3", ["-u", fullPath], {
    env: { ...process.env, PYTHONPATH: process.cwd() }
  });


  let output = "";

  proc.stdout.on("data", (data) => {
    output += data.toString();
  });

  proc.stderr.on("data", (data) => {
    output += data.toString();
  });

  proc.on("close", (code) => {
    output += `\n👋 Proses selesai dengan kode: ${code}`;
    res.status(200).json({ output });
  });
}
