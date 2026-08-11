import React from 'react';

export const ReplayComparisonView = ({ actualStrategy = 'STAY_OUT', counterfactualStrategy = 'PIT_NOW_SOFT', simulationResult }) => {
  const evaluations = simulationResult?.evaluations || [];
  const actualEval = evaluations.find((e) => e.strategy_id === actualStrategy) || evaluations[0];
  const cfEval = evaluations.find((e) => e.strategy_id === counterfactualStrategy) || evaluations[1] || evaluations[0];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', fontFamily: 'var(--font-mono)' }}>
      <h3 style={{ fontSize: '1rem', color: '#00E5FF', letterSpacing: '1px' }}>
        DUAL RACE TRAJECTORY REPLAY COMPARISON
      </h3>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Left Side: Actual Historical Strategy */}
        <div
          style={{
            background: 'rgba(0, 0, 0, 0.4)',
            border: '1px solid rgba(255, 255, 255, 0.15)',
            borderRadius: '8px',
            padding: '16px',
          }}
        >
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>
            ACTUAL HISTORICAL TRAJECTORY
          </div>
          <h4 style={{ fontSize: '1.2rem', color: '#FFF', marginBottom: '12px' }}>
            {actualStrategy}
          </h4>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.85rem' }}>
            <div>EXPECTED FINISH: <strong style={{ color: '#00E5FF' }}>P{actualEval?.expected_finish_pos || 2.0}</strong></div>
            <div>EXPECTED UTILITY: <strong style={{ color: '#FFF200' }}>{actualEval?.expected_utility || 18.0} pts</strong></div>
            <div>WIN PROBABILITY: <strong style={{ color: '#10B981' }}>{((actualEval?.win_probability || 0.0) * 100).toFixed(1)}%</strong></div>
            <div>REGRET: <strong style={{ color: '#E10600' }}>+{actualEval?.utility_regret || 0.0} pts</strong></div>
          </div>
        </div>

        {/* Right Side: Counterfactual Recommended Strategy */}
        <div
          style={{
            background: 'linear-gradient(135deg, rgba(225, 6, 0, 0.2) 0%, rgba(16, 22, 34, 0.8) 100%)',
            border: '1px solid #E10600',
            borderRadius: '8px',
            padding: '16px',
          }}
        >
          <div style={{ fontSize: '0.75rem', color: '#E10600', fontWeight: 700, marginBottom: '4px' }}>
            COUNTERFACTUAL / MODEL REPLAY TRAJECTORY
          </div>
          <h4 style={{ fontSize: '1.2rem', color: '#FFF200', marginBottom: '12px' }}>
            {counterfactualStrategy}
          </h4>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.85rem' }}>
            <div>EXPECTED FINISH: <strong style={{ color: '#00E5FF' }}>P{cfEval?.expected_finish_pos || 1.0}</strong></div>
            <div>EXPECTED UTILITY: <strong style={{ color: '#FFF200' }}>{cfEval?.expected_utility || 24.5} pts</strong></div>
            <div>WIN PROBABILITY: <strong style={{ color: '#10B981' }}>{((cfEval?.win_probability || 0.85) * 100).toFixed(1)}%</strong></div>
            <div>STATISTICALLY DISTINCT: <strong>{cfEval?.is_statistically_distinct ? 'YES' : 'NO'}</strong></div>
          </div>
        </div>
      </div>
    </div>
  );
};
