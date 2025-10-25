"""
EVOLUTION ORCHESTRATOR - SYSTEM CO-EVOLUTION MANAGEMENT
=======================================================

Orchestrates the co-evolutionary process between system and red team,
manages adaptation cycles, and tracks metrics.

Architecture:
-------------
1. TEST PHASE: Execute attacks
2. ANALYSIS PHASE: Discover issues
3. ADAPTATION PHASE: Apply fixes
4. VERIFICATION PHASE: Re-test improvements
5. METRICS PHASE: Calculate fitness
"""

from typing import List, Dict, Tuple, Any
from dataclasses import dataclass, field
import json
from datetime import datetime

from core import (
    DefenseType, GenerationReport, EvolutionPhase,
    TestIssue, SeverityLevel, EvolvableSeed
)
from red_team import RedTeamExecutor, RedTeamAdaptationEngine


# ============================================================================
# METRICS COLLECTOR
# ============================================================================

@dataclass
class DefenseMetrics:
    """Metrics for individual defense"""
    name: str
    active: bool
    strength: int
    times_triggered: int
    effectiveness: float
    status: str = ""


@dataclass
class EvolutionMetrics:
    """Overall evolution metrics"""
    generation: int
    fitness_score: float
    attacks_blocked: int
    attacks_total: int
    defenses_active: int
    defenses_total: int
    issues_found: int
    issues_resolved: int
    code_iterations: int
    time_elapsed: float


class MetricsCollector:
    """Collects and analyzes metrics"""
    
    def __init__(self):
        self.metrics_history: List[EvolutionMetrics] = []
        self.baseline_fitness = 0.0
    
    def collect_generation_metrics(self, report: GenerationReport) -> EvolutionMetrics:
        """Collect metrics from generation"""
        
        defenses_active = sum(
            1 for d in report.defenses_snapshot.values() 
            if d['active']
        )
        
        metrics = EvolutionMetrics(
            generation=report.generation,
            fitness_score=report.success_rate,
            attacks_blocked=report.attacks_blocked,
            attacks_total=report.attacks_total,
            defenses_active=defenses_active,
            defenses_total=len(report.defenses_snapshot),
            issues_found=len([i for i in report.issues if i.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]]),
            issues_resolved=len([i for i in report.issues if i.fix_verified]),
            code_iterations=report.code_iterations,
            time_elapsed=0.0
        )
        
        self.metrics_history.append(metrics)
        return metrics
    
    def calculate_improvement(self) -> Dict[str, float]:
        """Calculate improvement metrics"""
        if len(self.metrics_history) < 2:
            return {}
        
        first = self.metrics_history[0]
        last = self.metrics_history[-1]
        
        return {
            "fitness_improvement": last.fitness_score - first.fitness_score,
            "defenses_activated": last.defenses_active - first.defenses_active,
            "issues_resolved": last.issues_resolved,
            "total_iterations": last.code_iterations,
        }


# ============================================================================
# EVOLUTION ORCHESTRATOR
# ============================================================================

class EvolutionOrchestrator:
    """Orchestrates complete co-evolution cycle"""
    
    def __init__(self, seed: EvolvableSeed, max_generations: int = 10):
        self.seed = seed
        self.red_team = RedTeamExecutor(seed)
        self.adaptation_engine = RedTeamAdaptationEngine(self.red_team)
        self.metrics_collector = MetricsCollector()
        self.max_generations = max_generations
        self.evolution_log: List[GenerationReport] = []
        self.code_iteration_count = 0
    
    def run_generation(self, gen_num: int) -> GenerationReport:
        """Run complete generation cycle"""
        
        print(f"\n{'='*90}")
        print(f"🧪 GENERATION {gen_num} - LIVE TESTING")
        print(f"{'='*90}")
        
        report = GenerationReport(
            generation=gen_num,
            phase=EvolutionPhase.TESTING
        )
        
        self.red_team.generation_number = gen_num
        
        # PHASE 1: TESTING
        print(f"\n📊 PHASE 1: EXECUTING TESTS")
        exploits, blocked, total = self.red_team.execute_suite()
        report.exploits = exploits
        report.attacks_blocked = blocked
        report.attacks_total = total
        report.fitness_score = (blocked / total * 100) if total > 0 else 0
        
        print(f"  Attacks Blocked: {blocked}/{total}")
        print(f"  Fitness Score: {report.fitness_score:.1f}%")
        
        # PHASE 2: ANALYSIS
        print(f"\n🔍 PHASE 2: ANALYZING RESULTS")
        issues = self.adaptation_engine.analyze_results(exploits)
        report.issues = issues
        
        for issue in issues:
            print(f"  ⚠️  [{issue.severity.value}] {issue.description}")
        
        # PHASE 3: ADAPTATION
        print(f"\n🔧 PHASE 3: APPLYING FIXES")
        fixes = self._apply_defensive_adaptations(issues, exploits)
        report.code_iterations = len(fixes)
        self.code_iteration_count += len(fixes)
        
        for fix in fixes:
            print(f"  ✓ {fix}")
        
        # PHASE 4: RED TEAM EVOLUTION
        print(f"\n🧠 PHASE 4: RED TEAM ADAPTATION")
        attack_adaptations = self.adaptation_engine.adapt_patterns(exploits)
        for adaptation in attack_adaptations:
            print(f"  {adaptation}")
        
        # PHASE 5: SNAPSHOT
        report.defenses_snapshot = self.seed.get_defense_snapshot()
        report.phase = EvolutionPhase.VERIFICATION
        
        # Display state
        self._display_generation_state(report)
        
        self.evolution_log.append(report)
        self.seed.record_evolution(report)
        
        return report
    
    def _apply_defensive_adaptations(self, issues: List[TestIssue], exploits) -> List[str]:
        """Apply defensive fixes based on discovered issues"""
        fixes = []
        
        # Strategy 1: Strengthen failed defenses
        failed_defenses = set()
        for exploit in exploits:
            if not exploit.blocked:
                failed_defenses.add(exploit.vector)
        
        for defense_type in failed_defenses:
            self.seed.strengthen_defense(defense_type, amount=2)
            fixes.append(f"💪 Strengthened {defense_type.value} defense (strength +2)")
        
        # Strategy 2: Activate complementary defenses
        defense_relationships = {
            DefenseType.INPUT_VALIDATION: [DefenseType.SANITIZATION, DefenseType.BOUNDS_ENFORCEMENT],
            DefenseType.TYPE_CHECKING: [DefenseType.BOUNDS_ENFORCEMENT],
            DefenseType.SANITIZATION: [DefenseType.CRYPTOGRAPHY, DefenseType.STATE_PROTECTION],
            DefenseType.BOUNDS_ENFORCEMENT: [DefenseType.RATE_LIMITING],
        }
        
        for failed_defense in failed_defenses:
            if failed_defense in defense_relationships:
                for complementary in defense_relationships[failed_defense]:
                    current_state = self.seed.get_defense_snapshot()
                    if not current_state[complementary.value]['active']:
                        self.seed.activate_defense(complementary)
                        fixes.append(f"🧬 Activated {complementary.value} (complementary defense)")
        
        # Strategy 3: Low fitness emergency activation
        fitness = (sum(1 for e in exploits if e.blocked) / len(exploits) * 100) if exploits else 0
        if fitness < 50:
            for defense_type in DefenseType:
                self.seed.activate_defense(defense_type)
            fixes.append(f"🚨 Emergency: Activated ALL defenses (fitness: {fitness:.1f}%)")
        
        return fixes
    
    def _display_generation_state(self, report: GenerationReport):
        """Display current generation state"""
        print(f"\n🛡️  DEFENSE STATE:")
        
        snapshot = report.defenses_snapshot
        for name, state in snapshot.items():
            status = "✓" if state['active'] else "✗"
            bar = "█" * state['strength'] + "░" * (10 - state['strength'])
            effectiveness = state.get('effectiveness', 0) * 100
            print(f"  {status} {name:25} {bar} ({state['strength']:2d}/10) Eff: {effectiveness:5.1f}%")
        
        print(f"\n🎯 TOP ATTACK PATTERNS:")
        pattern_status = self.red_team.get_pattern_status()
        sorted_patterns = sorted(
            pattern_status.items(),
            key=lambda x: x[1]['success_rate'],
            reverse=True
        )[:5]
        
        for name, stats in sorted_patterns:
            sr = stats['success_rate'] * 100
            bar = "█" * int(sr / 10) + "░" * (10 - int(sr / 10))
            print(f"  {name:35} {bar} {sr:5.1f}% (Diff: {stats['difficulty']})")
    
    def run_evolution_cycle(self):
        """Run complete multi-generation evolution"""
        
        print("="*90)
        print("EVOLUTIONARY RED TEAM FRAMEWORK - FULL SYSTEM EXECUTION")
        print("="*90)
        print(f"Target: {self.seed.name}")
        print(f"Max Generations: {self.max_generations}")
        print()
        
        for gen in range(self.max_generations):
            report = self.run_generation(gen)
            
            # Collect metrics
            metrics = self.metrics_collector.collect_generation_metrics(report)
            
            # Check for perfect defense
            if report.fitness_score >= 100.0:
                print(f"\n✅ PERFECT DEFENSE ACHIEVED AT GENERATION {gen}!")
                break
            
            # Check for stagnation
            if gen > 3 and self._check_stagnation():
                print(f"\n⚠️  Evolution stagnating - applying breakthrough mutations...")
                self._apply_breakthrough_mutations()
        
        # Final summary
        self.print_evolution_summary()
    
    def _check_stagnation(self) -> bool:
        """Check if evolution is stagnating"""
        if len(self.evolution_log) < 4:
            return False
        
        recent = self.evolution_log[-3:]
        fitness_values = [r.fitness_score for r in recent]
        
        # Check if fitness hasn't improved
        if max(fitness_values) - min(fitness_values) < 5:
            return True
        
        return False
    
    def _apply_breakthrough_mutations(self):
        """Apply aggressive mutations to break stagnation"""
        for defense_type in DefenseType:
            self.seed.strengthen_defense(defense_type, amount=3)
            self.seed.activate_defense(defense_type)
    
    def print_evolution_summary(self):
        """Print comprehensive evolution summary"""
        
        print("\n" + "="*90)
        print("EVOLUTION SUMMARY: COMPLETE SYSTEM ANALYSIS")
        print("="*90)
        
        if not self.evolution_log:
            print("No evolution data recorded.")
            return
        
        first_gen = self.evolution_log[0]
        last_gen = self.evolution_log[-1]
        
        # Fitness progression
        print(f"\n📈 FITNESS PROGRESSION:")
        print(f"  Generation 0: {first_gen.fitness_score:.1f}%")
        print(f"  Generation {last_gen.generation}: {last_gen.fitness_score:.1f}%")
        print(f"  Improvement: +{last_gen.fitness_score - first_gen.fitness_score:.1f}%")
        
        # Defense evolution
        print(f"\n🛡️  DEFENSE EVOLUTION:")
        first_active = sum(1 for d in first_gen.defenses_snapshot.values() if d['active'])
        last_active = sum(1 for d in last_gen.defenses_snapshot.values() if d['active'])
        print(f"  Active Defenses: {first_active} → {last_active}")
        
        first_avg_strength = sum(d['strength'] for d in first_gen.defenses_snapshot.values()) / len(first_gen.defenses_snapshot)
        last_avg_strength = sum(d['strength'] for d in last_gen.defenses_snapshot.values()) / len(last_gen.defenses_snapshot)
        print(f"  Average Strength: {first_avg_strength:.1f} → {last_avg_strength:.1f}")
        
        # Issues & fixes
        print(f"\n⚠️  ISSUES & FIXES:")
        total_issues = sum(len(r.issues) for r in self.evolution_log)
        critical_issues = sum(
            len([i for i in r.issues if i.severity == SeverityLevel.CRITICAL])
            for r in self.evolution_log
        )
        print(f"  Total Issues Discovered: {total_issues}")
        print(f"  Critical Issues: {critical_issues}")
        print(f"  Code Iterations Applied: {self.code_iteration_count}")
        
        # Attack pattern evolution
        print(f"\n🎲 ATTACK PATTERN EVOLUTION:")
        pattern_stats = self.red_team.get_pattern_status()
        avg_difficulty = sum(p['difficulty'] for p in pattern_stats.values()) / len(pattern_stats)
        print(f"  Average Attack Difficulty: {avg_difficulty:.1f}/10")
        
        successful_patterns = [p for p in pattern_stats.values() if p['success_rate'] > 0]
        print(f"  Patterns Still Succeeding: {len(successful_patterns)}/{len(pattern_stats)}")
        
        # Generation-by-generation breakdown
        print(f"\n📊 GENERATION-BY-GENERATION BREAKDOWN:")
        print(f"  {'Gen':>3} | {'Fitness':>7} | {'Blocked':>7} | {'Issues':>6} | {'Fixes':>5}")
        print(f"  {'-'*3}-+-{'-'*7}-+-{'-'*7}-+-{'-'*6}-+-{'-'*5}")
        
        for report in self.evolution_log:
            print(f"  {report.generation:3d} | {report.fitness_score:6.1f}% | "
                  f"{report.attacks_blocked:2d}/{report.attacks_total:2d} | "
                  f"{len(report.issues):6d} | {report.code_iterations:5d}")
        
        # Final state
        print(f"\n🏆 FINAL STATE:")
        print(f"  System Name: {self.seed.name}")
        print(f"  Generations Completed: {last_gen.generation + 1}")
        print(f"  Final Fitness: {last_gen.fitness_score:.1f}%")
        print(f"  Total Adaptations: {self.code_iteration_count}")
        
        # Improvement metrics
        improvements = self.metrics_collector.calculate_improvement()
        if improvements:
            print(f"\n💪 KEY IMPROVEMENTS:")
            for key, value in improvements.items():
                print(f"  {key.replace('_', ' ').title()}: {value:.1f}")
        
        print(f"\n{'='*90}")
        print("EVOLUTION COMPLETE")
        print(f"{'='*90}\n")