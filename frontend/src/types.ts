export interface Activation {
  id: string;
  park_reference: string;
  operator_callsign: string;
  start_time: string;
  created_at: string;
}

export interface ActivationDetail extends Activation {
  qsos: QSO[];
}

export interface QSO {
  id: string;
  activation_id: string;
  callsign: string;
  frequency: number;
  band: string;
  mode: string;
  rst_sent: string;
  rst_received: string;
  timestamp: string;
  created_at: string;
}

export interface QSOCreate {
  callsign: string;
  frequency: number;
  band: string;
  mode: string;
  rst_sent: string;
  rst_received: string;
  timestamp: string;
}
