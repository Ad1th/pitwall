import React from 'react';
import { ModeToggle } from './ModeToggle';

export const Header = ({ mode, onModeChange, selectedRace, onRaceChange, races = [] }) => {
  return (
    <header
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '12px 24px',
        background: 'rgba(16, 22, 34, 0.9)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(12px)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div
          style={{
            width: '10px',
            height: '10px',
            borderRadius: '50%',
            background: '#E10600',
            boxShadow: '0 0 10px #E10600',
          }}
        />
        <h1 style={{ fontSize: '1.25rem', fontWeight: 700, letterSpacing: '1px', fontFamily: 'var(--font-mono)' }}>
          PITWALL <span style={{ color: '#E10600', fontSize: '0.85rem' }}>// RE-RUN THE RACE</span>
        </h1>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {races.length > 0 && (
          <select
            value={selectedRace}
            onChange={(e) => onRaceChange && onRaceChange(e.target.value)}
            style={{
              background: 'rgba(0,0,0,0.5)',
              color: '#F8FAFC',
              border: '1px solid rgba(255,255,255,0.15)',
              padding: '6px 12px',
              borderRadius: '6px',
              fontSize: '0.85rem',
              fontFamily: 'var(--font-mono)',
            }}
          >
            {races.map((r) => (
              <option key={r.race_id} value={r.race_id}>
                {r.name} ({r.year})
              </option>
            ))}
          </select>
        )}

        <ModeToggle mode={mode} onChange={onModeChange} />
      </div>
    </header>
  );
};
