import React from 'react';

export const RegretTimeline = ({ decisions = [], selectedDecisionIndex = 0, onSelectDecision }) => {
  if (!decisions || decisions.length === 0) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontFamily: 'var(--font-mono)' }}>
      <h4 style={{ fontSize: '0.85rem', color: '#E10600', letterSpacing: '1px' }}>
        HISTORICAL STRATEGIC DECISION TIMELINE (RANKED BY REGRET)
      </h4>

      <div style={{ display: 'flex', gap: '12px', overflowX: 'auto', paddingBottom: '8px' }}>
        {decisions.map((dec, idx) => {
          const isSelected = selectedDecisionIndex === idx;
          const hasHighRegret = dec.utility_regret > 0.5;

          return (
            <div
              key={idx}
              onClick={() => onSelectDecision && onSelectDecision(idx)}
              style={{
                minWidth: '220px',
                padding: '12px',
                borderRadius: '8px',
                cursor: 'pointer',
                background: isSelected ? 'rgba(225, 6, 0, 0.25)' : 'rgba(0, 0, 0, 0.4)',
                border: isSelected
                  ? '1px solid #E10600'
                  : hasHighRegret
                  ? '1px solid rgba(225, 6, 0, 0.5)'
                  : '1px solid rgba(255, 255, 255, 0.1)',
                transition: 'all 0.2s ease',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.75rem', color: '#FFF200', fontWeight: 700 }}>
                  LAP {dec.lap_number}
                </span>
                {hasHighRegret && (
                  <span style={{ background: '#E10600', color: '#FFF', padding: '1px 6px', borderRadius: '3px', fontSize: '0.65rem', fontWeight: 700 }}>
                    HIGH REGRET
                  </span>
                )}
              </div>

              <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#FFF', marginBottom: '4px' }}>
                {dec.driver_id} — {dec.actual_decision}
              </div>

              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                REGRET: <strong style={{ color: dec.utility_regret > 0 ? '#E10600' : '#10B981' }}>+{dec.utility_regret} pts</strong>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
