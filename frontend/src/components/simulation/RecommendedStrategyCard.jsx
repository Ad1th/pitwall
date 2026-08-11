import React from 'react';

export const RecommendedStrategyCard = ({ evaluation }) => {
  if (!evaluation) return null;

  const {
    strategy_id,
    expected_utility,
    expected_finish_pos,
    expected_finish_pos_ci95,
    outcome_prediction_quantiles,
    win_probability,
    podium_probability,
  } = evaluation;

  return (
    <div
      style={{
        background: 'linear-gradient(135deg, rgba(225, 6, 0, 0.25) 0%, rgba(16, 22, 34, 0.9) 100%)',
        border: '1px solid #E10600',
        borderRadius: '12px',
        padding: '20px',
        boxShadow: '0 0 25px rgba(225, 6, 0, 0.25)',
        fontFamily: 'var(--font-mono)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
        <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#E10600', letterSpacing: '1.5px' }}>
          RECOMMENDED OPTIMAL STRATEGY (PITWALL MODEL)
        </span>
        <span style={{ background: '#E10600', color: '#FFF', padding: '2px 8px', borderRadius: '4px', fontSize: '0.7rem', fontWeight: 700 }}>
          OPTIMAL a*
        </span>
      </div>

      <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#FFF', marginBottom: '16px' }}>
        {strategy_id.replace('_', ' ')}
      </h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>EXPECTED UTILITY U(a*)</div>
          <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#FFF200' }}>{expected_utility} pts</div>
        </div>

        <div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>EXPECTED FINISH (CI 95%)</div>
          <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#00E5FF' }}>
            P{expected_finish_pos}{' '}
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              [{expected_finish_pos_ci95?.[0]} - {expected_finish_pos_ci95?.[1]}]
            </span>
          </div>
        </div>

        <div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>OUTCOME QUANTILES [q05 - q95]</div>
          <div style={{ fontSize: '1.1rem', fontWeight: 600, color: '#F8FAFC' }}>
            P{outcome_prediction_quantiles?.[0]} - P{outcome_prediction_quantiles?.[1]}
          </div>
        </div>

        <div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>WIN / PODIUM PROBABILITY</div>
          <div style={{ fontSize: '1.1rem', fontWeight: 600, color: '#10B981' }}>
            {(win_probability * 100).toFixed(1)}% / {(podium_probability * 100).toFixed(1)}%
          </div>
        </div>
      </div>
    </div>
  );
};
