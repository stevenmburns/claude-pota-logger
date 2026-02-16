import { HuntSessionDetail, QSO, QSOCreate, Settings, ParkInfo } from "./types";

const BASE = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    const message = body?.detail || `${res.status} ${res.statusText}`;
    const err = new Error(message);
    (err as any).status = res.status;
    throw err;
  }
  return res.json();
}

export async function getTodaySession(): Promise<HuntSessionDetail> {
  return request("/hunt-sessions/today");
}

export async function getSession(id: string): Promise<HuntSessionDetail> {
  return request(`/hunt-sessions/${id}`);
}

export async function createQSO(
  sessionId: string,
  data: QSOCreate
): Promise<QSO> {
  return request(`/hunt-sessions/${sessionId}/qsos`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function deleteQSO(
  sessionId: string,
  qsoId: string
): Promise<void> {
  await fetch(`${BASE}/hunt-sessions/${sessionId}/qsos/${qsoId}`, {
    method: "DELETE",
  });
}

export function exportUrl(sessionId: string): string {
  return `${BASE}/hunt-sessions/${sessionId}/export`;
}

export async function getSettings(): Promise<Settings> {
  return request("/settings");
}

export async function updateSettings(operator_callsign: string): Promise<Settings> {
  return request("/settings", {
    method: "PUT",
    body: JSON.stringify({ operator_callsign }),
  });
}

export async function fetchParkInfo(parkRef: string): Promise<ParkInfo> {
  return request(`/parks/${parkRef}`);
}
