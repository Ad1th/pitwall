import React from 'react';

export const StrategyComparisonTable = ({ evaluations = [] }) => {
  if (!evaluations || evaluations.length === 0) return null;

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem', fontFamily: 'var(--font-mono)' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.15)', color: 'var(--text-secondary)', textAlign: 'left' }}>
            <th style={{ padding: '8px 12px' }}>RANK</th>
            <th style={{ padding: '8px 12px' }}>STRATEGY</th>
            <th style={{ padding: '8px 12px' }}>EXPECTED UTILITY</th>
            <th style={{ padding: '8px 12px' }}>EXP FINISH (CI 95%)</th>
            <th style={{ padding: '8px 12px' }}>QUANTILES [q05-q95]</th>
            <th style={{ padding: '8px 12px' }}>WIN PROB</th>
            <th style={{ padding: '8px 12px' }}>REGRET U(a*)-U(a)</th>
            <th style={{ padding: '8px 12px' }}>DISTINCT?</th>
          </tr>
        </thead>
        <tbody>
          {evaluations.map((ev, idx) => {
            const isOptimal = idx === 0;
            return (
              <tr
                key={ev.strategy_id}
                style={{
                  borderBottom: '1px solid rgba(255,255,255,0.05)',
                  background: isOptimal ? 'rgba(225, 6, 0, 0.1)' : 'transparent',
                }}
              >
                <td style={{ padding: '10px 12px', fontWeight: 700 }}>#{idx + 1}</td>
                <td style={{ padding: '10px 12px', fontWeight: 700, color: isOptimal ? '#FFF200' : '#FFF' }}>
                  {ev.strategy_id}
                </td>
                <td style={{ padding: '10px 12px', color: '#FFF200', fontWeight: 700 }}>
                  {ev.expected_utility} pts
                </td>
                <td style={{ padding: '10px 12px', color: '#00E5FF' }}>
                  P{ev.expected_finish_pos} [{ev.expected_finish_pos_ci95?.[0]} - {ev.expected_finish_pos_ci95?.[1]}]
                </td>
                <td style={{ padding: '10px 12px' }}>
                  P{ev.outcome_prediction_quantiles?.[0]} - P{ev.outcome_prediction_quantiles?.[1]}
                </td>
                <td style={{ padding: '10px 12px', color: '#10B981' }}>
                  {(ev.win_probability * 100).toFixed(1)}%
                </td>
                <td style={{ padding: '10px 12px', color: ev.utility_regret > 0 ? '#E10600' : 'var(--text-secondary)' }}>
                  {ev.utility_regret > 0 ? `+${ev.utility_regret}` : '0.0 (Optimal)'}
                </td>
                <td style={{ padding: '10px 12px' }}>
                  {ev.is_statistically_distinct === false ? (
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>INDISTINCT</span>
                  ) : (
                    <span style={{ color: '#10B981', fontSize: '0.75rem', fontWeight: 700 }}>DISTINCT</span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
