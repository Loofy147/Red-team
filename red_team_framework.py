import React, { useState, useEffect } from 'react';
import { Play, Pause, RotateCcw, Zap, AlertCircle, CheckCircle } from 'lucide-react';

export default function EvolutionaryTestFramework() {
  const [generation, setGeneration] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [testResults, setTestResults] = useState([]);
  const [issues, setIssues] = useState([]);
  const [defenses, setDefenses] = useState({});
  const [fitness, setFitness] = useState(0);
  const [codeIterations, setCodeIterations] = useState(0);
  const [history, setHistory] = useState([]);

  // Initialize defenses
  useEffect(() => {
    const initialDefenses = {
      input_validation: { active: true, strength: 2, triggered: 0 },
      type_checking: { active: true, strength: 1, triggered: 0 },
      bounds_enforcement: { active: true, strength: 1, triggered: 0 },
      sanitization: { active: true, strength: 2, triggered: 0 },
      state_protection: { active: true, strength: 1, triggered: 0 },
      rate_limiting: { active: false, strength: 1, triggered: 0 },
      cryptography: { active: false, strength: 1, triggered: 0 },
    };
    setDefenses(initialDefenses);
  }, []);

  // Apply defense logic
  const applyDefense = (defenseType, value, defenseState) => {
    const defense = defenseState[defenseType];
    if (!defense?.active) return { blocked: false, reason: 'Defense inactive' };

    try {
      if (defenseType === 'input_validation') {
        if (value === null || value === '') {
          return { blocked: true, reason: 'Blocked null/empty input' };
        }
        if (defense.strength >= 4 && typeof value !== 'string') {
          return { blocked: true, reason: 'Blocked non-string type' };
        }
      }

      if (defenseType === 'type_checking') {
        if (typeof value !== 'string' && typeof value !== 'number') {
          return { blocked: true, reason: `Blocked type ${typeof value}` };
        }
      }

      if (defenseType === 'bounds_enforcement') {
        const maxLen = 100 - (10 - defense.strength) * 5;
        if (typeof value === 'string' && value.length > maxLen) {
          return { blocked: true, reason: `Blocked oversized (${value.length} > ${maxLen})` };
        }
        if (Array.isArray(value) && value.length > 50 - (10 - defense.strength) * 3) {
          return { blocked: true, reason: 'Blocked large collection' };
        }
      }

      if (defenseType === 'sanitization') {
        const dangerous = ["'", '"', ';', '--', '/*', '*/', 'DROP', 'DELETE', 'UNION'];
        if (defense.strength >= 8) {
          dangerous.push('<', '>', '{', '}', '[', ']');
        }
        if (dangerous.some(p => String(value).toUpperCase().includes(p))) {
          return { blocked: true, reason: 'Blocked dangerous characters' };
        }
      }

      if (defenseType === 'state_protection') {
        if (typeof value === 'object' && String(value).includes('_protected')) {
          return { blocked: true, reason: 'Blocked state injection' };
        }
      }

      if (defenseType === 'rate_limiting' && defense.strength >= 5) {
        return { blocked: true, reason: 'Rate limited' };
      }

      if (defenseType === 'cryptography' && defense.strength >= 7) {
        return { blocked: true, reason: 'Crypto validation failed' };
      }

      return { blocked: false, reason: 'Attack passed' };
    } catch (e) {
      return { blocked: false, reason: `Defense error: ${e.message}` };
    }
  };

  // Run test generation
  const runTestGeneration = async (currentGen, currentDefenses) => {
    const attackPatterns = [
      { type: 'input_validation', payload: null, name: 'Null injection', difficulty: 1 },
      { type: 'input_validation', payload: '', name: 'Empty string', difficulty: 1 },
      { type: 'type_checking', payload: ['list'], name: 'List confusion', difficulty: 2 },
      { type: 'type_checking', payload: { dict: 'x' }, name: 'Dict confusion', difficulty: 2 },
      { type: 'bounds_enforcement', payload: 'A'.repeat(500), name: 'String overflow', difficulty: 3 },
      { type: 'sanitization', payload: "'; DROP--", name: 'SQL injection', difficulty: 4 },
      { type: 'sanitization', payload: '/**/UNION', name: 'Comment inject', difficulty: 5 },
      { type: 'state_protection', payload: { _protected: 'x' }, name: 'State corrupt', difficulty: 3 },
    ];

    const results = [];
    let blockedCount = 0;
    const newIssues = [];

    for (const pattern of attackPatterns) {
      const { blocked, reason } = applyDefense(pattern.type, pattern.payload, currentDefenses);

      results.push({
        name: pattern.name,
        type: pattern.type,
        blocked: blocked,
        reason: reason,
        difficulty: pattern.difficulty,
      });

      if (blocked) {
        blockedCount++;
        const updatedDefense = { ...currentDefenses[pattern.type] };
        updatedDefense.strength = Math.min(10, updatedDefense.strength + 1);
        updatedDefense.triggered += 1;
        currentDefenses[pattern.type] = updatedDefense;
      } else {
        newIssues.push({
          type: 'EXPLOIT_SUCCESS',
          description: `${pattern.name} bypassed ${pattern.type}`,
          severity: pattern.difficulty > 4 ? 'CRITICAL' : 'HIGH',
        });
      }
    }

    const fitScore = (blockedCount / attackPatterns.length) * 100;
    return { results, blockedCount, total: attackPatterns.length, fitness: fitScore, issues: newIssues, defenses: currentDefenses };
  };

  // Apply code fixes
  const applyCodeFixes = (currentDefenses, genNum) => {
    let fixes = [];
    let updatedDefenses = { ...currentDefenses };

    // Fix 1: Low fitness - activate more defenses
    const activeCount = Object.values(updatedDefenses).filter(d => d.active).length;
    if (activeCount < 5) {
      Object.entries(updatedDefenses).forEach(([key, def]) => {
        if (!def.active) {
          updatedDefenses[key] = { ...def, active: true };
          fixes.push(`🧬 Activated ${key}`);
        }
      });
    }

    // Fix 2: Strengthen weak defenses
    Object.entries(updatedDefenses).forEach(([key, def]) => {
      if (def.active && def.strength < 3) {
        updatedDefenses[key] = { ...def, strength: Math.min(10, def.strength + 1) };
        fixes.push(`💪 Strengthened ${key}`);
      }
    });

    // Fix 3: Difficulty scaling
    if (genNum % 2 === 0) {
      fixes.push('🔧 Applied difficulty scaling fix');
    }

    return { fixes, defenses: updatedDefenses };
  };

  // Main evolution cycle
  const runEvolutionCycle = async () => {
    setIsRunning(true);
    let currentGen = 0;
    let currentDefenses = { ...defenses };
    let allIssues = [];
    let allHistory = [];
    let iterations = 0;

    while (currentGen < 10 && isRunning) {
      // Run tests
      const genResult = await runTestGeneration(currentGen, currentDefenses);
      currentDefenses = genResult.defenses;
      
      setTestResults(genResult.results);
      setFitness(genResult.fitness);
      allIssues = [...allIssues, ...genResult.issues];
      setIssues(allIssues);
      
      // Apply code fixes
      const { fixes, defenses: fixedDefenses } = applyCodeFixes(currentDefenses, currentGen);
      currentDefenses = fixedDefenses;
      iterations += fixes.length;
      setCodeIterations(iterations);

      // Update history
      allHistory.push({
        gen: currentGen,
        fitness: genResult.fitness,
        blocked: genResult.blockedCount,
        issues: genResult.issues.length,
        fixes: fixes,
      });
      setHistory(allHistory);

      setDefenses(currentDefenses);
      setGeneration(currentGen);

      // Wait before next generation
      await new Promise(r => setTimeout(r, 1200));
      currentGen++;

      if (genResult.fitness === 100) break;
    }

    setIsRunning(false);
  };

  const reset = () => {
    setGeneration(0);
    setTestResults([]);
    setIssues([]);
    setFitness(0);
    setCodeIterations(0);
    setHistory([]);
    const initialDefenses = {
      input_validation: { active: true, strength: 2, triggered: 0 },
      type_checking: { active: true, strength: 1, triggered: 0 },
      bounds_enforcement: { active: true, strength: 1, triggered: 0 },
      sanitization: { active: true, strength: 2, triggered: 0 },
      state_protection: { active: true, strength: 1, triggered: 0 },
      rate_limiting: { active: false, strength: 1, triggered: 0 },
      cryptography: { active: false, strength: 1, triggered: 0 },
    };
    setDefenses(initialDefenses);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-black p-6 text-white">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
            🧪 Evolutionary Test Framework
          </h1>
          <p className="text-gray-400">JavaScript-based live testing with real-time analysis & code improvement</p>
        </div>

        {/* Controls */}
        <div className="flex gap-4 mb-8">
          <button
            onClick={runEvolutionCycle}
            disabled={isRunning}
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 disabled:opacity-50 rounded-lg font-bold transition"
          >
            <Play size={20} /> Start Testing
          </button>
          <button
            onClick={reset}
            disabled={isRunning}
            className="flex items-center gap-2 px-6 py-3 bg-gray-700 hover:bg-gray-600 disabled:opacity-50 rounded-lg font-bold transition"
          >
            <RotateCcw size={20} /> Reset
          </button>
        </div>

        {/* Main Stats */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          <div className="bg-gray-800 border border-cyan-500 rounded-lg p-4">
            <div className="text-gray-400 text-sm">Generation</div>
            <div className="text-3xl font-bold text-cyan-400">{generation}</div>
          </div>
          <div className="bg-gray-800 border border-green-500 rounded-lg p-4">
            <div className="text-gray-400 text-sm">Fitness Score</div>
            <div className="text-3xl font-bold text-green-400">{fitness.toFixed(1)}%</div>
          </div>
          <div className="bg-gray-800 border border-blue-500 rounded-lg p-4">
            <div className="text-gray-400 text-sm">Code Iterations</div>
            <div className="text-3xl font-bold text-blue-400">{codeIterations}</div>
          </div>
          <div className="bg-gray-800 border border-red-500 rounded-lg p-4">
            <div className="text-gray-400 text-sm">Issues Found</div>
            <div className="text-3xl font-bold text-red-400">{issues.length}</div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-6">
          {/* Test Results */}
          <div className="col-span-2">
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
              <h2 className="text-xl font-bold mb-4 text-cyan-400">🎯 Test Results</h2>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {testResults.map((result, idx) => (
                  <div key={idx} className="bg-gray-900 p-3 rounded border border-gray-700 flex items-center justify-between">
                    <div className="flex-1">
                      <div className="font-semibold text-sm">{result.name}</div>
                      <div className="text-xs text-gray-400">{result.reason}</div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-xs bg-gray-700 px-2 py-1 rounded">Diff: {result.difficulty}</span>
                      {result.blocked ? (
                        <CheckCircle size={20} className="text-green-400" />
                      ) : (
                        <AlertCircle size={20} className="text-red-400" />
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Defenses */}
          <div>
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
              <h2 className="text-xl font-bold mb-4 text-blue-400">🛡️ Defenses</h2>
              <div className="space-y-3">
                {Object.entries(defenses).map(([key, def]) => (
                  <div key={key} className="bg-gray-900 p-3 rounded">
                    <div className="flex justify-between items-center mb-1">
                      <div className="text-sm font-semibold">{key}</div>
                      <div className="text-xs">{def.active ? '✓' : '✗'} {def.strength}/10</div>
                    </div>
                    <div className="w-full bg-gray-700 rounded h-2">
                      <div
                        className="bg-gradient-to-r from-green-500 to-blue-500 h-2 rounded transition-all"
                        style={{ width: `${(def.strength / 10) * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Issues & Fixes */}
        <div className="grid grid-cols-2 gap-6 mt-6">
          {/* Issues */}
          <div className="bg-gray-800 border border-red-700 rounded-lg p-6">
            <h2 className="text-xl font-bold mb-4 text-red-400">⚠️ Issues Discovered</h2>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {issues.slice(-5).map((issue, idx) => (
                <div key={idx} className="bg-gray-900 p-3 rounded border-l-4 border-red-500">
                  <div className="text-xs font-bold text-red-400">{issue.severity}</div>
                  <div className="text-sm">{issue.description}</div>
                </div>
              ))}
            </div>
          </div>

          {/* History */}
          <div className="bg-gray-800 border border-green-700 rounded-lg p-6">
            <h2 className="text-xl font-bold mb-4 text-green-400">📈 Evolution History</h2>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {history.slice(-5).map((h, idx) => (
                <div key={idx} className="bg-gray-900 p-3 rounded text-sm">
                  <div className="font-bold text-cyan-400">Gen {h.gen}</div>
                  <div className="text-xs text-gray-400">Fitness: {h.fitness.toFixed(1)}% | Blocked: {h.blocked} | Fixes: {h.fixes.length}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-8 bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-semibold">Overall Progress</span>
            <span className="text-sm text-gray-400">{fitness.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-cyan-500 via-blue-500 to-green-500 h-3 rounded-full transition-all duration-500"
              style={{ width: `${fitness}%` }}
            />
          </div>
        </div>

        {/* Status */}
        <div className="mt-8 text-center text-gray-400">
          {isRunning ? (
            <div className="flex items-center justify-center gap-2">
              <Zap className="animate-pulse text-yellow-400" size={20} />
              <span>Testing in progress...</span>
            </div>
          ) : (
            <span>{generation === 0 ? 'Ready to start testing' : 'Testing complete'}</span>
          )}
        </div>
      </div>
    </div>
  );
}