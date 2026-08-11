import React, { useState, useEffect } from 'react';

export const LapScrubber = ({ currentLap = 1, totalLaps = 58, onLapChange, trackStatus = '1' }) => {
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    let interval = null;
    if (isPlaying) {
      interval = setInterval(() => {
        onLapChange && onLapChange((prev) => (prev >= totalLaps ? 1 : prev + 1));
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isPlaying, totalLaps, onLapChange]);

  const getTrackStatusBadge = (status) => {
    if (status === '4') {
      return (
        <span style={{ background: '#FFF200', color: '#0A0D14', padding: '2px 8px', borderRadius: '4px', fontWeight: 700, fontSize: '0.75rem' }}>
          SAFETY CAR (SC)
        </span>
      );
    }
    if (status === '6') {
      return (
        <span style={{ background: '#FFF200', color: '#0A0D14', padding: '2px 8px', borderRadius: '4px', fontWeight: 700, fontSize: '0.75rem' }}>
          VIRTUAL SAFETY CAR (VSC)
        </span>
      );
    }
    return (
      <span style={{ background: '#10B981', color: '#FFFFFF', padding: '2px 8px', borderRadius: '4px', fontWeight: 700, fontSize: '0.75rem' }}>
        TRACK GREEN
      </span>
    );
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
        background: 'rgba(0, 0, 0, 0.4)',
        padding: '16px',
        borderRadius: '8px',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        fontFamily: 'var(--font-mono)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button
            type="button"
            onClick={() => setIsPlaying(!isPlaying)}
            style={{
              background: '#E10600',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '6px',
              padding: '6px 14px',
              fontWeight: 700,
              cursor: 'pointer',
              fontSize: '0.85rem',
            }}
          >
            {isPlaying ? 'PAUSE' : 'PLAY'}
          </button>

          <button
            type="button"
            onClick={() => onLapChange && onLapChange(Math.max(1, currentLap - 1))}
            style={{
              background: 'rgba(255, 255, 255, 0.1)',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '6px',
              padding: '6px 10px',
              cursor: 'pointer',
            }}
          >
            ◀ STEP -1
          </button>

          <button
            type="button"
            onClick={() => onLapChange && onLapChange(Math.min(totalLaps, currentLap + 1))}
            style={{
              background: 'rgba(255, 255, 255, 0.1)',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '6px',
              padding: '6px 10px',
              cursor: 'pointer',
            }}
          >
            STEP +1 ▶
          </button>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          {getTrackStatusBadge(trackStatus)}
          <span style={{ fontSize: '1rem', fontWeight: 700 }}>
            LAP <span style={{ color: '#E10600' }}>{currentLap}</span> / {totalLaps}
          </span>
        </div>
      </div>

      <input
        type="range"
        min={1}
        max={totalLaps}
        value={currentLap}
        onChange={(e) => onLapChange && onLapChange(Number(e.target.value))}
        style={{
          width: '100%',
          accentColor: '#E10600',
          cursor: 'pointer',
        }}
      />
    </div>
  );
};
