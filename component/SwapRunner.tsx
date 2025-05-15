"use client";
import { useState } from "react";

export default function SwapRunner() {
  const [log, setLog] = useState<string[]>([]);
  const [running, setRunning] = useState(false);

  const startSwap = () => {
    setRunning(true);
    const eventSource = new EventSource("/api/stream-swap");

    eventSource.onmessage = (event) => {
      setLog((prev) => [...prev, event.data.replace(/\\n/g, "\n")]);
    };

    eventSource.onerror = () => {
      eventSource.close();
      setRunning(false);
    };
  };

  return (
    <div className="p-4">
      <button
        className="bg-blue-600 text-white px-4 py-2 rounded-lg"
        onClick={startSwap}
        disabled={running}
      >
        {running ? "Running..." : "Start Auto Swap"}
      </button>
      <pre className="mt-4 bg-gray-100 p-2 text-sm overflow-auto h-64 whitespace-pre-wrap">
        {log.join("\n")}
      </pre>
    </div>
  );
}
