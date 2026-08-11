import React, { useState } from 'react';

export const StrategyBuilder = ({ currentLap = 53, totalLaps = 58, drivers = [], onAddStrategy, onSimulate, loading }) => {
  const [pitLap, setPitLap] = useState(currentLap);
  const [targetCompound, setTargetCompound] = useState('SOFT');
  const [selectedDriver, setSelectedDriver] = useState('HAM');

  const handleAdd = () => {
    const stratId = `PIT_L${pitLap}_${targetCompound}`;
    onAddStrategy &&
      onAddStrategy({
        strategy_id: stratId,
        pit_laps: [pitLap],
        target_compound: targetCompound,
      });
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
        background: 'rgba(0,0,0,0.4)',
        padding: '16px',
        borderRadius: '8px',
        border: '1px solid rgba(255,255,255,0.1)',
        fontFamily: 'var(--font-mono)',
      }}
    >
      <h4 style={{ fontSize: '0.85rem', color: '#00E5FF', letterSpacing: '1px' }}>CONFIGURE CANDIDATE STRATEGY</h4>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
        <div>
          <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>
            TARGET DRIVER
          </label>
          <select
            value={selectedDriver}
            onChange={(e) => setSelectedDriver(e.target.value)}
            style={{
              width: '100%',
              background: '#0A0D14',
              color: '#FFF',
              border: '1px solid rgba(255,255,255,0.2)',
              padding: '6px 10px',
              borderRadius: '6px',
            }}
          >
            {drivers.map((d) => (
              <option key={d.driver_id} value={d.driver_id}>
                {d.driver_id} (P{d.position})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>
            PIT LAP (L{currentLap} - L{totalLaps})
          </label>
          <input
            type="number"
            min={currentLap}
            max={totalLaps}
            value={pitLap}
            onChange={(e) => setPitLap(Number(e.target.value))}
            style={{
              width: '100%',
              background: '#0A0D14',
              color: '#FFF',
              border: '1px solid rgba(255,255,255,0.2)',
              padding: '6px 10px',
              borderRadius: '6px',
            }}
          />
        </div>

        <div>
          <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>
            TYRE COMPOUND
          </label>
          <select
            value={targetCompound}
            onChange={(e) => setTargetCompound(e.target.value)}
            style={{
              width: '100%',
              background: '#0A0D14',
              color: '#FFF',
              border: '1px solid rgba(255,255,255,0.2)',
              padding: '6px 10px',
              borderRadius: '6px',
            }}
          >
            <option value="SOFT">SOFT (#FF1801)</option>
            <option value="MEDIUM">MEDIUM (#FFF200)</option>
            <option value="HARD">HARD (#FFFFFF)</option>
          </select>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '12px' }}>
        <button
          type="button"
          onClick={handleAdd}
          style={{
            background: 'rgba(255,255,255,0.1)',
            color: '#FFF',
            border: '1px solid rgba(255,255,255,0.2)',
            borderRadius: '6px',
            padding: '8px 16px',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          + ADD STRATEGY
        </button>

        <button
          type="button"
          onClick={() => onSimulate && onSimulate(selectedDriver)}
          disabled={loading}
          style={{
            flex: 1,
            background: loading ? '#475569' : '#E10600',
            color: '#FFF',
            border: 'none',
            borderRadius: '6px',
            padding: '8px 16px',
            fontWeight: 700,
            cursor: loading ? 'not-allowed' : 'pointer',
            letterSpacing: '1px',
          }}
        >
          {loading ? 'SIMULATING 1,000 FUTURES...' : '⚡ RUN MONTE CARLO SIMULATION'}
        </button>
      </div>
    </div>
  );
};
