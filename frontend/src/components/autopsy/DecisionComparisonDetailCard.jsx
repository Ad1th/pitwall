import React from 'react';

export const DecisionComparisonDetailCard = ({ decision }) => {
  if (!decision) return null;

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '16px',
        fontFamily: 'var(--font-mono)',
      }}
    >
      {/* Actual Historical Decision */}
      <div
        style={{
          background: 'rgba(255, 255, 255, 0.03)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: '8px',
          padding: '16px',
        }}
      >
        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>
          ACTUAL HISTORICAL STRATEGY
        </div>
        <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#FFF', marginBottom: '12px' }}>
          {decision.actual_decision}
        </div>
        <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div>WHAT HAPPENED: Stayed out under Safety Car flag.</div>
          <div>EXPECTED POSITION DELTA: <strong style={{ color: '#E10600' }}>+{decision.expected_position_delta} pos</strong></div>
          <div>UTILITY REGRET: <strong style={{ color: '#E10600' }}>+{decision.utility_regret} pts</strong></div>
        </div>
      </div>

      {/* PITWALL Recommended Optimal Strategy */}
      <div
        style={{
          background: 'linear-gradient(135deg, rgba(225, 6, 0, 0.15) 0%, rgba(16, 22, 34, 0.8) 100%)',
          border: '1px solid #E10600',
          borderRadius: '8px',
          padding: '16px',
        }}
      >
        <div style={{ fontSize: '0.75rem', color: '#E10600', fontWeight: 700, marginBottom: '4px' }}>
          PITWALL RECOMMENDED STRATEGY
        </div>
        <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#FFF200', marginBottom: '12px' }}>
          {decision.recommended_decision}
        </div>
        <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div>WHAT WAS RECOMMENDED: Pit for fresh SOFT tyres under Safety Car.</div>
          <div>STATISTICALLY DISTINCT: <strong>{decision.is_statistically_distinct ? 'YES' : 'NO'}</strong></div>
          <div>MODEL UNCERTAINTY: <strong>Monte Carlo 95% Confidence Interval Evaluated</strong></div>
        </div>
      </div>
    </div>
  );
};
