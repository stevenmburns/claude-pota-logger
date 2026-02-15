import { Activation, ActivationDetail, QSO, QSOCreate } from "./types";

const BASE = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function createActivation(data: {
  park_reference: string;
  operator_callsign: string;
  start_time: string;
}): Promise<Activation> {
  return request("/activations", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function listActivations(): Promise<Activation[]> {
  return request("/activations");
}

export async function getActivation(id: string): Promise<ActivationDetail> {
  return request(`/activations/${id}`);
}

export async function createQSO(
  activationId: string,
  data: QSOCreate
): Promise<QSO> {
  return request(`/activations/${activationId}/qsos`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function deleteQSO(
  activationId: string,
  qsoId: string
): Promise<void> {
  await fetch(`${BASE}/activations/${activationId}/qsos/${qsoId}`, {
    method: "DELETE",
  });
}

export function exportUrl(activationId: string): string {
  return `${BASE}/activations/${activationId}/export`;
}
