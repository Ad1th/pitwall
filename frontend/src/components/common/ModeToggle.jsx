import React from 'react';

export const ModeToggle = ({ mode = 'decision_time', onChange }) => {
  return (
    <div style={{ display: 'inline-flex', background: 'rgba(0,0,0,0.5)', borderRadius: '8px', padding: '3px', border: '1px solid rgba(255,255,255,0.1)' }}>
      <button
        type="button"
        onClick={() => onChange && onChange('decision_time')}
        style={{
          padding: '4px 12px',
          borderRadius: '6px',
          fontSize: '0.75rem',
          fontWeight: 600,
          border: 'none',
          cursor: 'pointer',
          background: mode === 'decision_time' ? '#E10600' : 'transparent',
          color: mode === 'decision_time' ? '#FFFFFF' : '#94A3B8',
          transition: 'all 0.2s ease',
        }}
      >
        DECISION-TIME
      </button>
      <button
        type="button"
        onClick={() => onChange && onChange('hindsight')}
        style={{
          padding: '4px 12px',
          borderRadius: '6px',
          fontSize: '0.75rem',
          fontWeight: 600,
          border: 'none',
          cursor: 'pointer',
          background: mode === 'hindsight' ? '#00E5FF' : 'transparent',
          color: mode === 'hindsight' ? '#0A0D14' : '#94A3B8',
          transition: 'all 0.2s ease',
        }}
      >
        HINDSIGHT
      </button>
    </div>
  );
};
