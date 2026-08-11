"""
API Fetch Client for PITWALL Backend REST API.
"""

const API_BASE = 'http://localhost:8000/api/v1';

export async function fetchRaces() {
  const res = await fetch(`${API_BASE}/races`);
  if (!res.ok) throw new Error('Failed to fetch races');
  return res.json();
}

export async function fetchRaceState(raceId, lap, mode = 'decision_time') {
  const res = await fetch(`${API_BASE}/races/${raceId}/state/${lap}?mode=${mode}`);
  if (!res.ok) throw new Error(`Failed to fetch race state for lap ${lap}`);
  return res.json();
}

export async function runSimulation(raceId, lap, driverId, mode, candidateStrategies) {
  const res = await fetch(`${API_BASE}/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      race_id: raceId,
      decision_lap: lap,
      target_driver_id: driverId,
      mode: mode,
      num_simulations: 1000,
      candidate_strategies: candidateStrategies,
    }),
  });
  if (!res.ok) throw new Error('Simulation failed');
  return res.json();
}

export async function fetchAutopsy(raceId, mode = 'decision_time') {
  const res = await fetch(`${API_BASE}/races/${raceId}/autopsy?mode=${mode}`);
  if (!res.ok) throw new Error('Failed to fetch race autopsy');
  return res.json();
}
