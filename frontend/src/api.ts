/**
 * frontend/src/api.ts
 * API client for PXN Custom Manager backend.
 * Handles fetching settings and sending updates with 200ms debounce.
 */

const BASE_URL = "http://127.0.0.1:8120/api";

export interface SettingsState {
  Spring?: number;
  Inertia?: number;
  Friction?: number;
  Center_Force?: number;
  Mechanical_Damper?: number;
  Game_Force?: number;
  FFB_Gain?: number;
  Rotation_Angle?: number;
  Wind_Speed_Switch?: number;
  Two_Pick_Status?: number;
  LED_Profile?: number[];
  Map_Profile?: number[];
  Calibration_Active?: boolean;
  [key: string]: any;
}

export interface ReadData {
  rotation_angle_raw?: number;
  rotation_angle_norm?: number;
  game_force?: number;
  ic?: number;
  iq_voltage?: number;
  speed?: number;
  raw?: string;
}

let debounceTimer: ReturnType<typeof setTimeout> | null = null;

export async function fetchSettings(): Promise<{ data: SettingsState; connected: boolean }> {
  const res = await fetch(`${BASE_URL}/settings`);
  if (!res.ok) throw new Error("Failed to fetch settings");
  return res.json();
}

export async function sendUpdate(settingName: string, value: any): Promise<{ status: string; sent: boolean }> {
  const res = await fetch(`${BASE_URL}/settings`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ setting_name: settingName, value }),
  });
  if (!res.ok) throw new Error("Failed to send update");
  return res.json();
}

export async function readWheelData(): Promise<{ data: ReadData | null }> {
  const res = await fetch(`${BASE_URL}/read`);
  if (!res.ok) throw new Error("Failed to read wheel data");
  return res.json();
}

export async function connectWheel(): Promise<{ connected: boolean }> {
  const res = await fetch(`${BASE_URL}/connect`, { method: "POST" });
  return res.json();
}

export async function disconnectWheel(): Promise<{ connected: boolean }> {
  const res = await fetch(`${BASE_URL}/disconnect`, { method: "POST" });
  return res.json();
}

/**
 * Debounced update: waits 200ms after slider stops before sending USB packet.
 */
export function debouncedUpdate(
  settingName: string,
  value: any,
  onSent?: (ok: boolean) => void
): void {
  if (debounceTimer) clearTimeout(debounceTimer);
  debounceTimer = setTimeout(async () => {
    try {
      const result = await sendUpdate(settingName, value);
      onSent?.(result.sent);
    } catch (e) {
      onSent?.(false);
    }
  }, 200);
}
