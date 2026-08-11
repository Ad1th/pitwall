import React from 'react';
import { TyreBadge } from '../common/TyreBadge';

export const LiveStandings = ({ drivers = [], selectedDriver, onSelectDriver }) => {
  if (!drivers || drivers.length === 0) {
    return (
      <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-secondary)' }}>
        No driver telemetry available for this lap.
      </div>
    );
  }

  const formatLapTime = (sec) => {
    if (!sec) return '—';
    const mins = Math.floor(sec / 60);
    const remainder = (sec % 60).toFixed(3);
    return mins > 0 ? `${mins}:${remainder.padStart(6, '0')}` : `${remainder}s`;
  };

  return (
    <div style={{ width: '100%', overflowX: 'auto' }}>
      <table
        style={{
          width: '100%',
          borderCollapse: 'collapse',
          fontSize: '0.85rem',
          fontFamily: 'var(--font-mono)',
        }}
      >
        <thead>
          <tr
            style={{
              borderBottom: '1px solid rgba(255,255,255,0.15)',
              color: 'var(--text-secondary)',
              textAlign: 'left',
            }}
          >
            <th style={{ padding: '8px 12px' }}>POS</th>
            <th style={{ padding: '8px 12px' }}>DRIVER</th>
            <th style={{ padding: '8px 12px' }}>TEAM</th>
            <th style={{ padding: '8px 12px' }}>TYRE</th>
            <th style={{ padding: '8px 12px' }}>GAP LEADER</th>
            <th style={{ padding: '8px 12px' }}>INTERVAL</th>
            <th style={{ padding: '8px 12px' }}>LAST LAP</th>
          </tr>
        </thead>
        <tbody>
          {drivers.map((d) => {
            const isSelected = selectedDriver === d.driver_id;
            return (
              <tr
                key={d.driver_id}
                onClick={() => onSelectDriver && onSelectDriver(d.driver_id)}
                style={{
                  borderBottom: '1px solid rgba(255,255,255,0.05)',
                  cursor: 'pointer',
                  background: isSelected ? 'rgba(225, 6, 0, 0.15)' : 'transparent',
                  transition: 'background 0.15s ease',
                }}
              >
                <td style={{ padding: '10px 12px', fontWeight: 700, color: d.position === 1 ? '#FFF200' : 'inherit' }}>
                  P{d.position}
                </td>
                <td style={{ padding: '10px 12px', fontWeight: 700 }}>
                  {d.driver_id}
                  {d.is_pit_lap && (
                    <span
                      style={{
                        marginLeft: '8px',
                        fontSize: '0.65rem',
                        background: '#E10600',
                        color: '#FFF',
                        padding: '1px 5px',
                        borderRadius: '3px',
                      }}
                    >
                      PIT
                    </span>
                  )}
                </td>
                <td style={{ padding: '10px 12px', color: 'var(--text-secondary)', textTransform: 'capitalize' }}>
                  {d.constructor_id.replace('_', ' ')}
                </td>
                <td style={{ padding: '10px 12px' }}>
                  <TyreBadge compound={d.compound} age={d.tyre_age} />
                </td>
                <td style={{ padding: '10px 12px' }}>
                  {d.position === 1 ? 'LEADER' : `+${d.gap_to_leader_sec.toFixed(3)}s`}
                </td>
                <td style={{ padding: '10px 12px' }}>
                  {d.position === 1 ? '—' : `+${d.interval_ahead_sec.toFixed(3)}s`}
                </td>
                <td style={{ padding: '10px 12px', color: '#00E5FF' }}>
                  {formatLapTime(d.last_lap_time_sec)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
