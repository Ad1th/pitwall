import React, { useState } from 'react';
import { runSimulation } from '../api/client';
import { GlassCard } from '../components/common/GlassCard';
import { StrategyBuilder } from '../components/simulation/StrategyBuilder';
import { RecommendedStrategyCard } from '../components/simulation/RecommendedStrategyCard';
import { StrategyComparisonTable } from '../components/simulation/StrategyComparisonTable';

export const StrategySimulatorView = ({ selectedRace = '2021-abu-dhabi', currentLap = 53, mode = 'decision_time', drivers = [] }) => {
  const [candidates, setCandidates] = useState([
    { strategy_id: 'STAY_OUT', pit_laps: [] },
    { strategy_id: 'PIT_NOW_SOFT', pit_laps: [53], target_compound: 'SOFT' },
    { strategy_id: 'PIT_NOW_HARD', pit_laps: [53], target_compound: 'HARD' },
  ]);
  const [simulationResult, setSimulationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAddStrategy = (newStrat) => {
    setCandidates((prev) => [...prev, newStrat]);
  };

  const handleSimulate = async (driverId) => {
    setLoading(true);
    setError(null);
    try {
      const res = await runSimulation(selectedRace, currentLap, driverId, mode, candidates);
      setSimulationResult(res);
    } catch (err) {
      setError('Simulation execution failed. Ensure backend API is active.');
    } finally {
      setLoading(false);
    }
  };

  const sortedEvaluations = simulationResult?.evaluations
    ? [...simulationResult.evaluations].sort((a, b) => b.expected_utility - a.expected_utility)
    : [];

  const recommendedEval = sortedEvaluations[0];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <GlassCard title="INTERACTIVE STRATEGY SIMULATOR // MONTE CARLO">
        <StrategyBuilder
          currentLap={currentLap}
          totalLaps={58}
          drivers={drivers}
          onAddStrategy={handleAddStrategy}
          onSimulate={handleSimulate}
          loading={loading}
        />
      </GlassCard>

      {error && (
        <div style={{ padding: '16px', background: 'rgba(225, 6, 0, 0.2)', border: '1px solid #E10600', borderRadius: '8px', color: '#FFF', fontFamily: 'var(--font-mono)' }}>
          ⚠️ {error}
        </div>
      )}

      {recommendedEval && <RecommendedStrategyCard evaluation={recommendedEval} />}

      {sortedEvaluations.length > 0 && (
        <GlassCard title={`MONTE CARLO CANDIDATE EVALUATIONS (${simulationResult?.evaluations?.length} FUTURES EVALUATED)`}>
          <StrategyComparisonTable evaluations={sortedEvaluations} />
        </GlassCard>
      )}
    </div>
  );
};
