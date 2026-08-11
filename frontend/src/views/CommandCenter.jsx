import React, { useState, useEffect } from 'react';
import { fetchRaces, fetchRaceState } from '../api/client';
import { Header } from '../components/common/Header';
import { GlassCard } from '../components/common/GlassCard';
import { LapScrubber } from '../components/scrubber/LapScrubber';
import { LiveStandings } from '../components/standings/LiveStandings';

export const CommandCenter = () => {
  const [races, setRaces] = useState([]);
  const [selectedRace, setSelectedRace] = useState('2021-abu-dhabi');
  const [mode, setMode] = useState('decision_time');
  const [currentLap, setCurrentLap] = useState(53);
  const [raceState, setRaceState] = useState(null);
  const [selectedDriver, setSelectedDriver] = useState('HAM');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 1. Fetch available races on mount
  useEffect(() => {
    fetchRaces()
      .then((data) => {
        if (data && data.length > 0) {
          setRaces(data);
        }
      })
      .catch((err) => {
        logger.warning?.(err) || console.warn(err);
      });
  }, []);

  // 2. Fetch RaceState telemetry whenever race, lap, or mode changes
  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchRaceState(selectedRace, currentLap, mode)
      .then((state) => {
        setRaceState(state);
        setLoading(false);
      })
      .catch((err) => {
        setError(`Could not load telemetry for ${selectedRace} lap ${currentLap}. Make sure backend is running.`);
        setLoading(false);
      });
  }, [selectedRace, currentLap, mode]);

  const targetDriverState = raceState?.drivers?.find((d) => d.driver_id === selectedDriver);
  const leaderState = raceState?.drivers?.[0];

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-dark)' }}>
      <Header
        mode={mode}
        onModeChange={setMode}
        selectedRace={selectedRace}
        onRaceChange={(rId) => {
          setSelectedRace(rId);
          setCurrentLap(1);
        }}
        races={races.length > 0 ? races : [{ race_id: '2021-abu-dhabi', name: 'Abu Dhabi Grand Prix', year: 2021 }]}
      />

      <main style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {/* Lap Scrubber Toolbar */}
        <LapScrubber
          currentLap={currentLap}
          totalLaps={raceState?.total_laps || 58}
          onLapChange={setCurrentLap}
          trackStatus={raceState?.track_status || '1'}
        />

        {/* Telemetry Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px' }}>
          {/* Main Live Leaderboard */}
          <GlassCard title={`LIVE DRIVER STANDINGS — LAP ${currentLap}`}>
            {loading ? (
              <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>
                LOADING TELEMETRY DATA...
              </div>
            ) : error ? (
              <div style={{ padding: '24px', color: '#E10600', fontFamily: 'var(--font-mono)' }}>
                ⚠️ {error}
              </div>
            ) : (
              <LiveStandings
                drivers={raceState?.drivers || []}
                selectedDriver={selectedDriver}
                onSelectDriver={setSelectedDriver}
              />
            )}
          </GlassCard>

          {/* Sidebar Telemetry Summary */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <GlassCard title="TRACK CONDITIONS">
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div>
                  <span style={{ color: 'var(--text-secondary)' }}>TRACK TEMP:</span>{' '}
                  <strong style={{ color: '#FFF200' }}>{raceState?.weather?.track_temp_c || 30.0}°C</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--text-secondary)' }}>AIR TEMP:</span>{' '}
                  <strong>{raceState?.weather?.air_temp_c || 22.0}°C</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--text-secondary)' }}>PRECIPITATION:</span>{' '}
                  <strong>{raceState?.weather?.rainfall ? 'RAIN' : 'DRY'}</strong>
                </div>
              </div>
            </GlassCard>

            <GlassCard title="SELECTED DRIVER STATE">
              {targetDriverState ? (
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <div>
                    <span style={{ color: 'var(--text-secondary)' }}>DRIVER:</span>{' '}
                    <strong style={{ color: '#E10600', fontSize: '1rem' }}>{targetDriverState.driver_id}</strong>
                  </div>
                  <div>
                    <span style={{ color: 'var(--text-secondary)' }}>POSITION:</span>{' '}
                    <strong>P{targetDriverState.position}</strong>
                  </div>
                  <div>
                    <span style={{ color: 'var(--text-secondary)' }}>COMPOUND:</span>{' '}
                    <strong>{targetDriverState.compound} (L{targetDriverState.tyre_age})</strong>
                  </div>
                  <div>
                    <span style={{ color: 'var(--text-secondary)' }}>GAP TO LEADER:</span>{' '}
                    <strong>{targetDriverState.position === 1 ? 'LEADER' : `+${targetDriverState.gap_to_leader_sec.toFixed(3)}s`}</strong>
                  </div>
                </div>
              ) : (
                <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Select a driver from the standings table.</div>
              )}
            </GlassCard>
          </div>
        </div>
      </main>
    </div>
  );
};
