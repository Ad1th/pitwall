import React, { useState, useEffect } from 'react';
import { fetchRaces, fetchRaceState } from './api/client';
import { Header } from './components/common/Header';
import { CommandCenter } from './views/CommandCenter';
import { StrategySimulatorView } from './views/StrategySimulatorView';
import { RaceAutopsyView } from './views/RaceAutopsyView';
import { CounterfactualReplayView } from './views/CounterfactualReplayView';

export function App() {
  const [activeTab, setActiveTab] = useState('command_center');
  const [mode, setMode] = useState('decision_time');
  const [selectedRace, setSelectedRace] = useState('2021-abu-dhabi');
  const [races, setRaces] = useState([]);
  const [currentLap, setCurrentLap] = useState(53);
  const [raceState, setRaceState] = useState(null);

  useEffect(() => {
    fetchRaces()
      .then((data) => {
        if (data && data.length > 0) setRaces(data);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    fetchRaceState(selectedRace, currentLap, mode)
      .then((st) => setRaceState(st))
      .catch(() => {});
  }, [selectedRace, currentLap, mode]);

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-dark)' }}>
      <Header
        mode={mode}
        onModeChange={setMode}
        selectedRace={selectedRace}
        onRaceChange={(r) => {
          setSelectedRace(r);
          setCurrentLap(1);
        }}
        races={
          races.length > 0
            ? races
            : [
                { race_id: '2021-abu-dhabi', name: 'Abu Dhabi Grand Prix', year: 2021 },
                { race_id: '2022-monaco', name: 'Monaco Grand Prix', year: 2022 },
                { race_id: '2022-silverstone', name: 'British Grand Prix', year: 2022 },
                { race_id: '2023-zandvoort', name: 'Dutch Grand Prix', year: 2023 },
              ]
        }
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      <main style={{ padding: '24px', maxWidth: '1600px', margin: '0 auto' }}>
        {activeTab === 'command_center' && (
          <CommandCenter />
        )}

        {activeTab === 'strategy_simulator' && (
          <StrategySimulatorView
            selectedRace={selectedRace}
            currentLap={currentLap}
            mode={mode}
            drivers={raceState?.drivers || []}
          />
        )}

        {activeTab === 'race_autopsy' && (
          <RaceAutopsyView selectedRace={selectedRace} mode={mode} />
        )}

        {activeTab === 'counterfactual_replay' && (
          <CounterfactualReplayView selectedRace={selectedRace} currentLap={currentLap} mode={mode} />
        )}
      </main>
    </div>
  );
}

export default App;
