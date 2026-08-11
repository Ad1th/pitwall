import React, { useState, useEffect } from 'react';
import { fetchAutopsy } from '../api/client';
import { GlassCard } from '../components/common/GlassCard';
import { RegretTimeline } from '../components/autopsy/RegretTimeline';
import { DecisionComparisonDetailCard } from '../components/autopsy/DecisionComparisonDetailCard';

export const RaceAutopsyView = ({ selectedRace = '2021-abu-dhabi', mode = 'decision_time' }) => {
  const [autopsyData, setAutopsyData] = useState(null);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchAutopsy(selectedRace, mode)
      .then((data) => {
        setAutopsyData(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(`Failed to fetch race autopsy for ${selectedRace}. Make sure backend API is active.`);
        setLoading(false);
      });
  }, [selectedRace, mode]);

  const decisions = autopsyData?.key_decisions || [];
  const selectedDecision = decisions[selectedIndex];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <GlassCard title={`RACE AUTOPSY & STRATEGIC REGRET ANALYSIS — ${selectedRace.toUpperCase()}`}>
        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>
            ANALYZING HISTORICAL STRATEGIC DECISIONS...
          </div>
        ) : error ? (
          <div style={{ padding: '24px', color: '#E10600', fontFamily: 'var(--font-mono)' }}>
            ⚠️ {error}
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <RegretTimeline
              decisions={decisions}
              selectedDecisionIndex={selectedIndex}
              onSelectDecision={setSelectedIndex}
            />

            {selectedDecision && <DecisionComparisonDetailCard decision={selectedDecision} />}
          </div>
        )}
      </GlassCard>
    </div>
  );
};
