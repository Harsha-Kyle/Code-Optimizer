import type { CompileResponse, HardwareProfile } from './types';

const API_BASE = "http://127.0.0.1:8000/api";

export async function getHardwareProfiles(): Promise<HardwareProfile[]> {
  const res = await fetch(`${API_BASE}/hardware`);
  if (!res.ok) throw new Error("Failed to fetch hardware profiles");
  return res.json();
}

export async function compileCode(source: string, target: string, passes: Record<string, boolean>): Promise<CompileResponse> {
  const res = await fetch(`${API_BASE}/compile`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ source, target, passes })
  });
  if (!res.ok) throw new Error("Compilation request failed");
  return res.json();
}
