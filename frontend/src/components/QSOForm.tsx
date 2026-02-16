import React, { useState, useRef, useEffect } from "react";
import { createQSO, fetchParkInfo } from "../api";
import { QSOCreate } from "../types";

const FREQ_TO_BAND: Record<string, string> = {
  "1.8": "160m", "3.5": "80m", "5.3": "60m", "7": "40m",
  "10.1": "30m", "14": "20m", "18.1": "17m", "21": "15m",
  "24.9": "12m", "28": "10m", "50": "6m", "144": "2m",
};

function freqToBand(mhz: number): string {
  for (const [start, band] of Object.entries(FREQ_TO_BAND)) {
    const f = parseFloat(start);
    if (mhz >= f && mhz < f + 1) return band;
  }
  if (mhz >= 28 && mhz < 30) return "10m";
  if (mhz >= 50 && mhz < 54) return "6m";
  if (mhz >= 144 && mhz < 148) return "2m";
  return "";
}

function defaultRst(mode: string): string {
  const m = mode.toUpperCase();
  if (m === "CW" || m === "FT8" || m === "FT4" || m === "RTTY") return "599";
  return "59";
}

interface Props {
  sessionId: string;
  onCreated: () => void;
}

export default function QSOForm({ sessionId, onCreated }: Props) {
  const [parkRef, setParkRef] = useState("");
  const [parkName, setParkName] = useState("");
  const [callsign, setCallsign] = useState("");
  const [frequency, setFrequency] = useState("");
  const [band, setBand] = useState("20m");
  const [mode, setMode] = useState("SSB");
  const [rstSent, setRstSent] = useState("59");
  const [rstRecv, setRstRecv] = useState("59");
  const [error, setError] = useState("");
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();

  const handleParkRefChange = (val: string) => {
    setParkRef(val);
    setParkName("");
    if (debounceRef.current) clearTimeout(debounceRef.current);
    const upper = val.toUpperCase().trim();
    if (upper.length >= 3) {
      debounceRef.current = setTimeout(() => {
        fetchParkInfo(upper)
          .then((info) => setParkName(info.name))
          .catch(() => setParkName(""));
      }, 400);
    }
  };

  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, []);

  const handleFreqChange = (val: string) => {
    setFrequency(val);
    const f = parseFloat(val);
    if (!isNaN(f)) {
      const b = freqToBand(f);
      if (b) setBand(b);
    }
  };

  const handleModeChange = (val: string) => {
    setMode(val);
    const rst = defaultRst(val);
    setRstSent(rst);
    setRstRecv(rst);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    const data: QSOCreate = {
      park_reference: parkRef.toUpperCase().trim(),
      callsign: callsign.toUpperCase().trim(),
      frequency: parseFloat(frequency),
      band,
      mode: mode.toUpperCase(),
      rst_sent: rstSent,
      rst_received: rstRecv,
      timestamp: new Date().toISOString(),
    };
    try {
      await createQSO(sessionId, data);
      setCallsign("");
      setParkRef("");
      setParkName("");
      onCreated();
    } catch (err: any) {
      if (err.status === 409) {
        setError(err.message);
      } else {
        setError(err.message || "Failed to log QSO");
      }
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit} style={{ display: "flex", gap: "0.5rem", alignItems: "end", flexWrap: "wrap" }}>
        <label>
          Park Ref
          <div style={{ display: "flex", alignItems: "center", gap: "0.25rem" }}>
            <input
              value={parkRef}
              onChange={(e) => handleParkRefChange(e.target.value)}
              placeholder="K-0001"
              required
              autoFocus
              style={{ width: "6rem" }}
            />
            {parkName && <span style={{ fontSize: "0.8rem", color: "#16a34a" }}>{parkName}</span>}
          </div>
        </label>
        <label>
          Callsign
          <input
            value={callsign}
            onChange={(e) => setCallsign(e.target.value)}
            placeholder="W1XYZ"
            required
          />
        </label>
        <label>
          Freq (MHz)
          <input
            type="number"
            step="0.001"
            value={frequency}
            onChange={(e) => handleFreqChange(e.target.value)}
            placeholder="14.250"
            required
          />
        </label>
        <label>
          Band
          <select value={band} onChange={(e) => setBand(e.target.value)}>
            {["160m","80m","60m","40m","30m","20m","17m","15m","12m","10m","6m","2m"].map(b =>
              <option key={b} value={b}>{b}</option>
            )}
          </select>
        </label>
        <label>
          Mode
          <select value={mode} onChange={(e) => handleModeChange(e.target.value)}>
            {["SSB","CW","FT8","FT4","AM","FM","RTTY"].map(m =>
              <option key={m} value={m}>{m}</option>
            )}
          </select>
        </label>
        <label>
          RST Sent
          <input value={rstSent} onChange={(e) => setRstSent(e.target.value)} style={{ width: "4rem" }} />
        </label>
        <label>
          RST Rcvd
          <input value={rstRecv} onChange={(e) => setRstRecv(e.target.value)} style={{ width: "4rem" }} />
        </label>
        <button type="submit">Log QSO</button>
      </form>
      {error && <p style={{ color: "#dc2626", marginTop: "0.5rem" }}>{error}</p>}
    </div>
  );
}
