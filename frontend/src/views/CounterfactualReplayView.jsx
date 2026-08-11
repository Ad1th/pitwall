import React, { useState, useEffect } from 'react';
import { runSimulation } from '../api/client';
import { GlassCard } from '../components/common/GlassCard';
import { BlindPitWallCard } from '../components/replay/BlindPitWallCard';
import { ReplayComparisonView } from '../components/replay/ReplayComparisonView';

export const CounterfactualReplayView = ({ selectedRace = '2021-abu-dhabi', currentLap = 53, mode = 'decision_time' }) => {
  const [committedDecision, setCommittedDecision] = useState(null);
  const [simulationResult, setSimulationResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Run baseline counterfactual simulation
    setLoading(true);
    const candidateStrats = [
      { strategy_id: 'STAY_OUT', pit_laps: [] },
      { strategy_id: 'PIT_NOW_SOFT', pit_laps: [currentLap], target_compound: 'SOFT' },
      { strategy_id: 'PIT_NOW_HARD', pit_laps: [currentLap], target_compound: 'HARD' },
    ];

    runSimulation(selectedRace, currentLap, 'HAM', mode, candidateStrats)
      .then((res) => {
        setSimulationResult(res);
        setLoading(false);
      })
      .catch((err) => {
        setLoading(false);
      });
  }, [selectedRace, currentLap, mode]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <GlassCard title={`COUNTERFACTUAL REPLAY EXPERIENCE — ${selectedRace.toUpperCase()}`}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <BlindPitWallCard
            driverId="HAM"
            lapNumber={currentLap}
            onCommitDecision={(decision) => setCommittedDecision(decision)}
          />

          {loading ? (
            <div style={{ padding: '30px', textAlign: 'center', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>
              SIMULATING REPLAY TRAJECTORIES...
            </div>
          ) : (
            <ReplayComparisonView
              actualStrategy="STAY_OUT"
              counterfactualStrategy="PIT_NOW_SOFT"
              simulationResult={simulationResult}
            />
          )}
        </div>
      </GlassCard>
    </div>
  );
};
