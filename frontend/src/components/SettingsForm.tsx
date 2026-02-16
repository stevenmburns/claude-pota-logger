import React, { useState } from "react";
import { updateSettings } from "../api";

interface Props {
  onSaved: (callsign: string) => void;
}

export default function SettingsForm({ onSaved }: Props) {
  const [callsign, setCallsign] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const upper = callsign.toUpperCase().trim();
    if (!upper) return;
    await updateSettings(upper);
    onSaved(upper);
  };

  return (
    <div>
      <h2>Welcome to POTA Hunter Logger</h2>
      <p>Enter your operator callsign to get started.</p>
      <form onSubmit={handleSubmit} style={{ display: "flex", gap: "0.5rem", alignItems: "end" }}>
        <label>
          Operator Callsign
          <input
            value={callsign}
            onChange={(e) => setCallsign(e.target.value)}
            placeholder="W1ABC"
            required
            autoFocus
          />
        </label>
        <button type="submit">Save</button>
      </form>
    </div>
  );
}
