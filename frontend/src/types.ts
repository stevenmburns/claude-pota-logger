export interface HuntSession {
  id: string;
  session_date: string;
  created_at: string;
}

export interface HuntSessionDetail extends HuntSession {
  qsos: QSO[];
}

export interface QSO {
  id: string;
  hunt_session_id: string;
  park_reference: string;
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
  park_reference: string;
  callsign: string;
  frequency: number;
  band: string;
  mode: string;
  rst_sent: string;
  rst_received: string;
  timestamp: string;
}

export interface Settings {
  id: string;
  operator_callsign: string;
  flrig_host: string;
  flrig_port: number;
  created_at: string;
  updated_at: string;
}

export interface ParkInfo {
  reference: string;
  name: string;
  locationDesc: string;
}

export interface Spot {
  spotId: number;
  activator: string;
  reference: string;
  name: string;
  locationDesc: string;
  frequency: string;
  mode: string;
  spotTime: string;
  comments: string;
  hunted?: boolean;
}
