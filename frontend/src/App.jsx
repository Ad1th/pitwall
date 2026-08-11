import React, { useState } from 'react';
import { Header } from './components/common/Header';
import { GlassCard } from './components/common/GlassCard';
import { TyreBadge } from './components/common/TyreBadge';

export function App() {
  const [mode, setMode] = useState('decision_time');
  const [selectedRace, setSelectedRace] = useState('2021-abu-dhabi');

  const demoRaces = [
    { race_id: '2021-abu-dhabi', name: 'Abu Dhabi Grand Prix', year: 2021 },
    { race_id: '2022-monaco', name: 'Monaco Grand Prix', year: 2022 },
    { race_id: '2022-silverstone', name: 'British Grand Prix', year: 2022 },
    { race_id: '2023-zandvoort', name: 'Dutch Grand Prix', year: 2023 },
  ];

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-dark)' }}>
      <Header
        mode={mode}
        onModeChange={setMode}
        selectedRace={selectedRace}
        onRaceChange={setSelectedRace}
        races={demoRaces}
      />

      <main style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
          <GlassCard title="F1 PIT WALL TELEMETRY">
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              Reconstructing historical race state for <strong>{selectedRace}</strong> under{' '}
              <span style={{ color: mode === 'decision_time' ? '#E10600' : '#00E5FF', fontWeight: 600 }}>
                {mode.toUpperCase()}
              </span>{' '}
              mode.
            </p>
          </GlassCard>

          <GlassCard title="TYRE COMPOUND TOKENS">
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginTop: '8px' }}>
              <TyreBadge compound="SOFT" age={12} />
              <TyreBadge compound="MEDIUM" age={18} />
              <TyreBadge compound="HARD" age={39} />
              <TyreBadge compound="INTERMEDIATE" age={5} />
              <TyreBadge compound="WET" age={2} />
            </div>
          </GlassCard>
        </div>
      </main>
    </div>
  );
}

export default App;
