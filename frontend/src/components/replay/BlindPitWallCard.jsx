import React, { useState } from 'react';

export const BlindPitWallCard = ({ driverId = 'HAM', lapNumber = 53, onCommitDecision }) => {
  const [userDecision, setUserDecision] = useState('PIT_SOFT');
  const [isCommitted, setIsCommitted] = useState(false);

  const handleCommit = () => {
    setIsCommitted(true);
    onCommitDecision && onCommitDecision(userDecision);
  };

  return (
    <div
      style={{
        background: 'linear-gradient(135deg, rgba(16, 22, 34, 0.95) 0%, rgba(24, 32, 48, 0.95) 100%)',
        border: '1px solid #00E5FF',
        borderRadius: '12px',
        padding: '20px',
        fontFamily: 'var(--font-mono)',
        boxShadow: '0 0 20px rgba(0, 229, 255, 0.2)',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <span style={{ fontSize: '0.75rem', color: '#00E5FF', fontWeight: 700, letterSpacing: '1.5px' }}>
          BLIND PIT WALL CHALLENGE // DECISION POINT LAP {lapNumber}
        </span>
        <span style={{ background: '#00E5FF', color: '#0A0D14', padding: '2px 8px', borderRadius: '4px', fontSize: '0.7rem', fontWeight: 700 }}>
          LIVE INTERACTIVE
        </span>
      </div>

      <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#FFF', marginBottom: '12px' }}>
        YOU ARE THE PIT WALL ENGINEER FOR {driverId}. MAKE THE CALL.
      </h3>

      {!isCommitted ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Safety Car deployed on Lap {lapNumber}. Choose your pit strategy before historical outcome is revealed:
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
            <button
              type="button"
              onClick={() => setUserDecision('STAY_OUT')}
              style={{
                padding: '12px',
                borderRadius: '8px',
                border: userDecision === 'STAY_OUT' ? '2px solid #FFF200' : '1px solid rgba(255,255,255,0.15)',
                background: userDecision === 'STAY_OUT' ? 'rgba(255,242,0,0.15)' : 'rgba(0,0,0,0.3)',
                color: '#FFF',
                fontWeight: 700,
                cursor: 'pointer',
              }}
            >
              1. STAY OUT (Hard L39)
            </button>

            <button
              type="button"
              onClick={() => setUserDecision('PIT_SOFT')}
              style={{
                padding: '12px',
                borderRadius: '8px',
                border: userDecision === 'PIT_SOFT' ? '2px solid #FF1801' : '1px solid rgba(255,255,255,0.15)',
                background: userDecision === 'PIT_SOFT' ? 'rgba(255,24,1,0.15)' : 'rgba(0,0,0,0.3)',
                color: '#FFF',
                fontWeight: 700,
                cursor: 'pointer',
              }}
            >
              2. PIT NOW FOR FRESH SOFT
            </button>

            <button
              type="button"
              onClick={() => setUserDecision('PIT_HARD')}
              style={{
                padding: '12px',
                borderRadius: '8px',
                border: userDecision === 'PIT_HARD' ? '2px solid #FFFFFF' : '1px solid rgba(255,255,255,0.15)',
                background: userDecision === 'PIT_HARD' ? 'rgba(255,255,255,0.15)' : 'rgba(0,0,0,0.3)',
                color: '#FFF',
                fontWeight: 700,
                cursor: 'pointer',
              }}
            >
              3. PIT NOW FOR FRESH HARD
            </button>
          </div>

          <button
            type="button"
            onClick={handleCommit}
            style={{
              background: '#00E5FF',
              color: '#0A0D14',
              border: 'none',
              borderRadius: '6px',
              padding: '12px',
              fontWeight: 700,
              cursor: 'pointer',
              fontSize: '0.9rem',
              letterSpacing: '1px',
              marginTop: '8px',
            }}
          >
            🔒 LOCK IN DECISION & REVEAL COUNTERFACTUAL REPLAY
          </button>
        </div>
      ) : (
        <div style={{ background: 'rgba(16, 185, 129, 0.15)', border: '1px solid #10B981', padding: '12px', borderRadius: '8px', color: '#FFF' }}>
          ✅ Decision locked: <strong>{userDecision}</strong>. Counterfactual simulation replaying below...
        </div>
      )}
    </div>
  );
};
