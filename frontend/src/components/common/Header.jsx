import React from 'react';
import { ModeToggle } from './ModeToggle';

export const Header = ({
  mode,
  onModeChange,
  selectedRace,
  onRaceChange,
  races = [],
  activeTab = 'command_center',
  onTabChange,
}) => {
  const tabs = [
    { id: 'command_center', label: 'COMMAND CENTER' },
    { id: 'strategy_simulator', label: 'STRATEGY SIMULATOR' },
    { id: 'race_autopsy', label: 'RACE AUTOPSY' },
    { id: 'counterfactual_replay', label: 'COUNTERFACTUAL REPLAY' },
  ];

  return (
    <header
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
        padding: '12px 24px 0 24px',
        background: 'rgba(16, 22, 34, 0.95)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(12px)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
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
          <h1 style={{ fontSize: '1.2rem', fontWeight: 700, letterSpacing: '1px', fontFamily: 'var(--font-mono)' }}>
            PITWALL <span style={{ color: '#E10600', fontSize: '0.8rem' }}>// COUNTERFACTUAL RACE STRATEGY ENGINE</span>
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
      </div>

      {/* Navigation Tabs */}
      <div style={{ display: 'flex', gap: '4px' }}>
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => onTabChange && onTabChange(tab.id)}
              style={{
                padding: '8px 16px',
                background: isActive ? 'rgba(225, 6, 0, 0.2)' : 'transparent',
                color: isActive ? '#FFF' : 'var(--text-secondary)',
                border: 'none',
                borderBottom: isActive ? '2px solid #E10600' : '2px solid transparent',
                fontSize: '0.8rem',
                fontWeight: 700,
                fontFamily: 'var(--font-mono)',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              {tab.label}
            </button>
          );
        })}
      </div>
    </header>
  );
};
