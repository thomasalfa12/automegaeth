import { useEffect, useRef, useState } from "react";
import { io } from "socket.io-client";

const socket = io(undefined!, {
  path: "/api/socket_io", // Path harus sesuai dengan backend WebSocket handler
});

export default function Home() {
  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState<string | null>(null);
  const logRef = useRef<HTMLDivElement>(null);

  const runScript = (type: string) => {
    setLoading(type);
    setLogs((prev) => [...prev, `⏳ Menjalankan auto_${type}.py...`]);
    socket.emit("start-script", type);
  };

  const stopScript = (type: string) => {
    socket.emit("stop-script", type);
    setLogs((prev) => [...prev, `🛑 Menghentikan auto_${type}.py...`]);
    setLoading(null);
  };

  useEffect(() => {
    socket.on("output", (data: string) => {
      setLogs((prev) => [...prev, data]);
    });

    return () => {
      socket.off("output");
    };
  }, []);

  useEffect(() => {
    logRef.current?.scrollTo(0, logRef.current.scrollHeight);
  }, [logs]);

  return (
    <main style={{ padding: 20, fontFamily: "sans-serif" }}>
      <h1>AutoMegaETH CLI Web UI (Real-Time)</h1>
      <div
        style={{ display: "flex", gap: 10, flexWrap: "wrap", marginBottom: 10 }}
      >
        <button onClick={() => runScript("swap")} disabled={loading === "swap"}>
          🔁 Jalankan auto_swap.py
        </button>
        <button onClick={() => runScript("lp")} disabled={loading === "lp"}>
          💧 Jalankan auto_LP.py
        </button>
        <button
          onClick={() => runScript("swap_lp")}
          disabled={loading === "swap_lp"}
        >
          🔀 Jalankan auto_swap_lp.py
        </button>
        <button
          onClick={() => stopScript("swap")}
          disabled={loading !== "swap"}
        >
          🛑 Stop Swap
        </button>
        <button onClick={() => stopScript("lp")} disabled={loading !== "lp"}>
          🛑 Stop LP
        </button>
        <button
          onClick={() => stopScript("swap_lp")}
          disabled={loading !== "swap_lp"}
        >
          🛑 Stop Swap + LP
        </button>
      </div>
      <div
        ref={logRef}
        style={{
          background: "#111",
          color: "#0f0",
          padding: 20,
          minHeight: 300,
          maxHeight: 400,
          overflowY: "auto",
          whiteSpace: "pre-wrap",
          border: "1px solid #333",
        }}
      >
        {logs.map((line, index) => (
          <div key={index}>{line}</div>
        ))}
      </div>
    </main>
  );
}
