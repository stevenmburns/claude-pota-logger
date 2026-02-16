import { useState, useEffect, useRef } from "react";
import { getActiveSpots } from "../api";
import { Spot } from "../types";

const BANDS = ["All", "160m", "80m", "60m", "40m", "30m", "20m", "17m", "15m", "12m", "10m", "6m", "2m"];
const MODES = ["All", "SSB", "CW", "FT8", "FT4", "AM", "FM", "RTTY"];

const FREQ_TO_BAND: Record<string, string> = {
  "1.8": "160m", "3.5": "80m", "5.3": "60m", "7": "40m",
  "10.1": "30m", "14": "20m", "18.1": "17m", "21": "15m",
  "24.9": "12m", "28": "10m", "50": "6m", "144": "2m",
};

function kHzToBand(kHz: string): string {
  const mhz = parseFloat(kHz) / 1000;
  if (isNaN(mhz)) return "";
  for (const [start, band] of Object.entries(FREQ_TO_BAND)) {
    const f = parseFloat(start);
    if (mhz >= f && mhz < f + 1) return band;
  }
  if (mhz >= 28 && mhz < 30) return "10m";
  if (mhz >= 50 && mhz < 54) return "6m";
  if (mhz >= 144 && mhz < 148) return "2m";
  return "";
}

function kHzToMHz(kHz: string): string {
  const val = parseFloat(kHz);
  if (isNaN(val)) return kHz;
  return (val / 1000).toFixed(4);
}

interface Props {
  onSelect: (spot: Spot) => void;
}

export default function SpotsList({ onSelect }: Props) {
  const [spots, setSpots] = useState<Spot[]>([]);
  const [loading, setLoading] = useState(true);
  const [bandFilter, setBandFilter] = useState("All");
  const [modeFilter, setModeFilter] = useState("All");
  const intervalRef = useRef<ReturnType<typeof setInterval>>();

  const fetchSpots = () => {
    getActiveSpots()
      .then(setSpots)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchSpots();
    intervalRef.current = setInterval(fetchSpots, 60000);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  const filtered = spots.filter((s) => {
    if (bandFilter !== "All" && kHzToBand(s.frequency) !== bandFilter) return false;
    if (modeFilter !== "All" && s.mode.toUpperCase() !== modeFilter) return false;
    return true;
  });

  return (
    <div style={{ marginBottom: "1.5rem" }}>
      <div style={{ display: "flex", gap: "1rem", alignItems: "center", marginBottom: "0.5rem" }}>
        <h3 style={{ margin: 0 }}>Active Spots</h3>
        <label>
          Band{" "}
          <select value={bandFilter} onChange={(e) => setBandFilter(e.target.value)}>
            {BANDS.map((b) => <option key={b} value={b}>{b}</option>)}
          </select>
        </label>
        <label>
          Mode{" "}
          <select value={modeFilter} onChange={(e) => setModeFilter(e.target.value)}>
            {MODES.map((m) => <option key={m} value={m}>{m}</option>)}
          </select>
        </label>
        <span style={{ fontSize: "0.8rem", color: "#666" }}>
          {filtered.length} spot{filtered.length !== 1 ? "s" : ""}
        </span>
      </div>
      {loading ? (
        <p>Loading spots...</p>
      ) : (
        <div style={{ maxHeight: "300px", overflow: "auto", border: "1px solid #ddd", borderRadius: "4px" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
            <thead>
              <tr style={{ background: "#f5f5f5", position: "sticky", top: 0 }}>
                <th style={thStyle}>Time</th>
                <th style={thStyle}>Freq (MHz)</th>
                <th style={thStyle}>Mode</th>
                <th style={thStyle}>Activator</th>
                <th style={thStyle}>Location</th>
                <th style={thStyle}>Park</th>
                <th style={thStyle}>Name</th>
                <th style={thStyle}></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((spot) => (
                <tr key={spot.spotId} style={{ borderBottom: "1px solid #eee" }}>
                  <td style={tdStyle}>{new Date(spot.spotTime).toLocaleTimeString()}</td>
                  <td style={tdStyle}>{kHzToMHz(spot.frequency)}</td>
                  <td style={tdStyle}>{spot.mode}</td>
                  <td style={tdStyle}>{spot.activator}</td>
                  <td style={tdStyle}>{spot.locationDesc}</td>
                  <td style={tdStyle}>{spot.reference}</td>
                  <td style={tdStyle}>{spot.name}</td>
                  <td style={tdStyle}>
                    <button
                      type="button"
                      onClick={() => onSelect(spot)}
                      style={{ padding: "0.15rem 0.5rem", fontSize: "0.8rem" }}
                    >
                      Select
                    </button>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr><td colSpan={8} style={{ padding: "1rem", textAlign: "center", color: "#999" }}>No spots found</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

const thStyle: React.CSSProperties = { textAlign: "left", padding: "0.35rem 0.5rem", borderBottom: "2px solid #ddd" };
const tdStyle: React.CSSProperties = { padding: "0.3rem 0.5rem" };
