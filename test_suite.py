"""
TEST RUNNER - COMPREHENSIVE VALIDATION SUITE
=============================================

Validates all system components through automated testing.

Test Categories:
----------------
1. Unit Tests: Individual component validation
2. Integration Tests: Component interaction validation
3. Evolution Tests: Full cycle validation
4. Regression Tests: Ensure improvements persist
5. Performance Tests: Benchmark execution
"""

import sys
import time
from typing import List, Tuple
from dataclasses import dataclass

from core import (
    EvolvableSeed, DefenseType, DefenseConfig,
    InputValidationDefense, TypeCheckingDefense,
    BoundsEnforcementDefense, SanitizationDefense
)
from red_team import RedTeamExecutor, AttackPatternLibrary
from orchestrator import EvolutionOrchestrator


# ============================================================================
# TEST RESULT TRACKING
# ============================================================================

@dataclass
class TestResult:
    """Result of a single test"""
    name: str
    passed: bool
    message: str
    duration: float


class TestRunner:
    """Manages test execution and reporting"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
    
    def run_test(self, test_name: str, test_func) -> TestResult:
        """Execute a single test"""
        print(f"  Running: {test_name}...", end=" ")
        
        start_time = time.time()
        try:
            test_func()
            duration = time.time() - start_time
            result = TestResult(test_name, True, "PASSED", duration)
            print(f"✓ ({duration:.3f}s)")
            self.tests_passed += 1
        except AssertionError as e:
            duration = time.time() - start_time
            result = TestResult(test_name, False, str(e), duration)
            print(f"✗ FAILED: {e}")
            self.tests_failed += 1
        except Exception as e:
            duration = time.time() - start_time
            result = TestResult(test_name, False, f"ERROR: {e}", duration)
            print(f"✗ ERROR: {e}")
            self.tests_failed += 1
        
        self.tests_run += 1
        self.results.append(result)
        return result
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Tests Run: {self.tests_run}")
        print(f"Passed: {self.tests_passed} ✓")
        print(f"Failed: {self.tests_failed} ✗")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        total_time = sum(r.duration for r in self.results)
        print(f"Total Time: {total_time:.3f}s")
        
        if self.tests_failed > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.results:
                if not result.passed:
                    print(f"  - {result.name}: {result.message}")
        
        print("="*80)


# ============================================================================
# UNIT TESTS
# ============================================================================

class UnitTests:
    """Unit tests for individual components"""
    
    @staticmethod
    def test_defense_config_creation():
        """Test defense configuration creation"""
        config = DefenseConfig(DefenseType.INPUT_VALIDATION, active=True, strength=5)
        assert config.active == True
        assert config.strength == 5
        assert config.times_triggered == 0
    
    @staticmethod
    def test_defense_config_strengthen():
        """Test defense strengthening"""
        config = DefenseConfig(DefenseType.INPUT_VALIDATION, strength=5)
        config.strengthen(2)
        assert config.strength == 7
        config.strengthen(5)
        assert config.strength == 10  # Max cap
    
    @staticmethod
    def test_defense_config_effectiveness():
        """Test effectiveness calculation"""
        config = DefenseConfig(DefenseType.INPUT_VALIDATION)
        assert config.effectiveness == 0.0
        
        config.trigger(True)
        config.trigger(True)
        config.trigger(False)
        assert config.effectiveness == 2/3
    
    @staticmethod
    def test_input_validation_null():
        """Test input validation blocks null"""
        config = DefenseConfig(DefenseType.INPUT_VALIDATION)
        defense = InputValidationDefense(config)
        blocked, reason = defense.execute(None)
        assert blocked == True
        assert "null" in reason.lower()
    
    @staticmethod
    def test_input_validation_empty():
        """Test input validation blocks empty string"""
        config = DefenseConfig(DefenseType.INPUT_VALIDATION)
        defense = InputValidationDefense(config)
        blocked, reason = defense.execute("")
        assert blocked == True
        assert "empty" in reason.lower()
    
    @staticmethod
    def test_type_checking_list():
        """Test type checking blocks list"""
        config = DefenseConfig(DefenseType.TYPE_CHECKING)
        defense = TypeCheckingDefense(config)
        blocked, reason = defense.execute(["test"])
        assert blocked == True
        assert "list" in reason.lower()
    
    @staticmethod
    def test_type_checking_dict():
        """Test type checking blocks dict"""
        config = DefenseConfig(DefenseType.TYPE_CHECKING)
        defense = TypeCheckingDefense(config)
        blocked, reason = defense.execute({"key": "value"})
        assert blocked == True
    
    @staticmethod
    def test_bounds_enforcement_string():
        """Test bounds enforcement blocks large strings"""
        config = DefenseConfig(DefenseType.BOUNDS_ENFORCEMENT, strength=1)
        defense = BoundsEnforcementDefense(config)
        large_string = "A" * 200
        blocked, reason = defense.execute(large_string)
        assert blocked == True
        assert "oversized" in reason.lower() or "too long" in reason.lower()
    
    @staticmethod
    def test_sanitization_sql():
        """Test sanitization blocks SQL injection"""
        config = DefenseConfig(DefenseType.SANITIZATION)
        defense = SanitizationDefense(config)
        blocked, reason = defense.execute("'; DROP TABLE--")
        assert blocked == True
        assert "dangerous" in reason.lower()
    
    @staticmethod
    def test_evolvable_seed_creation():
        """Test evolvable seed creation"""
        seed = EvolvableSeed("TestSystem")
        assert seed.name == "TestSystem"
        assert seed.generation == 0
        assert len(seed.defense_framework.defenses) > 0
    
    @staticmethod
    def test_evolvable_seed_strengthen():
        """Test seed defense strengthening"""
        seed = EvolvableSeed("TestSystem")
        initial_strength = seed.defense_framework.defenses[DefenseType.INPUT_VALIDATION].config.strength
        seed.strengthen_defense(DefenseType.INPUT_VALIDATION, 3)
        new_strength = seed.defense_framework.defenses[DefenseType.INPUT_VALIDATION].config.strength
        assert new_strength == initial_strength + 3
    
    @staticmethod
    def test_attack_pattern_library():
        """Test attack pattern generation"""
        assert AttackPatternLibrary.null_injection() is None
        assert AttackPatternLibrary.empty_string() == ""
        assert isinstance(AttackPatternLibrary.type_confusion_list(), list)
        assert isinstance(AttackPatternLibrary.type_confusion_dict(), dict)
        assert len(AttackPatternLibrary.buffer_overflow_small()) > 100


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class IntegrationTests:
    """Integration tests for component interactions"""
    
    @staticmethod
    def test_seed_defense_integration():
        """Test seed and defense framework integration"""
        seed = EvolvableSeed("TestSystem")
        blocked, reason = seed.test_defense(DefenseType.INPUT_VALIDATION, None)
        assert blocked == True
    
    @staticmethod
    def test_red_team_executor():
        """Test red team executor"""
        seed = EvolvableSeed("TestSystem")
        red_team = RedTeamExecutor(seed)
        assert len(red_team.attack_patterns) > 0
    
    @staticmethod
    def test_red_team_single_attack():
        """Test single attack execution"""
        seed = EvolvableSeed("TestSystem")
        red_team = RedTeamExecutor(seed)
        pattern = red_team.attack_patterns[0]
        exploit = red_team.execute_attack(pattern)
        assert exploit is not None
        assert hasattr(exploit, 'blocked')
        assert hasattr(exploit, 'description')
    
    @staticmethod
    def test_red_team_full_suite():
        """Test full attack suite"""
        seed = EvolvableSeed("TestSystem")
        red_team = RedTeamExecutor(seed)
        exploits, blocked, total = red_team.execute_suite()
        assert len(exploits) == total
        assert blocked <= total
        assert blocked >= 0
    
    @staticmethod
    def test_defense_strengthening_effect():
        """Test that strengthening actually improves defense"""
        seed = EvolvableSeed("TestSystem")
        red_team = RedTeamExecutor(seed)
        
        # First attack
        exploits1, blocked1, total1 = red_team.execute_suite()
        
        # Strengthen all defenses
        for defense_type in DefenseType:
            seed.strengthen_defense(defense_type, 5)
        
        # Second attack
        exploits2, blocked2, total2 = red_team.execute_suite()
        
        # Should block more or equal attacks
        assert blocked2 >= blocked1
    
    @staticmethod
    def test_snapshot_accuracy():
        """Test defense snapshot accuracy"""
        seed = EvolvableSeed("TestSystem")
        snapshot1 = seed.get_defense_snapshot()
        
        seed.strengthen_defense(DefenseType.INPUT_VALIDATION, 3)
        snapshot2 = seed.get_defense_snapshot()
        
        assert snapshot2['validate_input']['strength'] == snapshot1['validate_input']['strength'] + 3


# ============================================================================
# EVOLUTION TESTS
# ============================================================================

class EvolutionTests:
    """Tests for evolution cycles"""
    
    @staticmethod
    def test_single_generation():
        """Test single generation execution"""
        seed = EvolvableSeed("TestSystem")
        orchestrator = EvolutionOrchestrator(seed, max_generations=1)
        report = orchestrator.run_generation(0)
        
        assert report.generation == 0
        assert report.attacks_total > 0
        assert 0 <= report.fitness_score <= 100
    
    @staticmethod
    def test_fitness_improvement():
        """Test that fitness improves over generations"""
        seed = EvolvableSeed("TestSystem")
        orchestrator = EvolutionOrchestrator(seed, max_generations=3)
        
        fitness_scores = []
        for gen in range(3):
            report = orchestrator.run_generation(gen)
            fitness_scores.append(report.fitness_score)
        
        # Fitness should generally improve
        assert fitness_scores[-1] >= fitness_scores[0]
    
    @staticmethod
    def test_defense_activation():
        """Test that inactive defenses get activated"""
        seed = EvolvableSeed("TestSystem")
        
        initial_snapshot = seed.get_defense_snapshot()
        initial_active = sum(1 for d in initial_snapshot.values() if d['active'])
        
        orchestrator = EvolutionOrchestrator(seed, max_generations=2)
        for gen in range(2):
            orchestrator.run_generation(gen)
        
        final_snapshot = seed.get_defense_snapshot()
        final_active = sum(1 for d in final_snapshot.values() if d['active'])
        
        # Should activate more defenses
        assert final_active >= initial_active
    
    @staticmethod
    def test_metrics_collection():
        """Test metrics are collected properly"""
        seed = EvolvableSeed("TestSystem")
        orchestrator = EvolutionOrchestrator(seed, max_generations=2)
        
        for gen in range(2):
            report = orchestrator.run_generation(gen)
            orchestrator.metrics_collector.collect_generation_metrics(report)
        
        assert len(orchestrator.metrics_collector.metrics_history) == 2
        
        improvements = orchestrator.metrics_collector.calculate_improvement()
        assert 'fitness_improvement' in improvements


# ============================================================================
# REGRESSION TESTS
# ============================================================================

class RegressionTests:
    """Ensure bugs don't reappear"""
    
    @staticmethod
    def test_no_division_by_zero():
        """Test no division by zero in fitness calculation"""
        seed = EvolvableSeed("TestSystem")
        orchestrator = EvolutionOrchestrator(seed, max_generations=1)
        
        # Should not raise exception
        report = orchestrator.run_generation(0)
        assert report.fitness_score >= 0
    
    @staticmethod
    def test_defense_strength_cap():
        """Test defense strength caps at 10"""
        config = DefenseConfig(DefenseType.INPUT_VALIDATION, strength=9)
        config.strengthen(5)
        assert config.strength == 10
    
    @staticmethod
    def test_empty_exploit_list():
        """Test handling of empty exploit list"""
        from red_team import RedTeamAdaptationEngine
        
        seed = EvolvableSeed("TestSystem")
        red_team = RedTeamExecutor(seed)
        engine = RedTeamAdaptationEngine(red_team)
        
        # Should not crash
        issues = engine.analyze_results([])
        assert isinstance(issues, list)


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class PerformanceTests:
    """Performance benchmarks"""
    
    @staticmethod
    def test_single_generation_speed():
        """Test single generation completes quickly"""
        seed = EvolvableSeed("TestSystem")
        orchestrator = EvolutionOrchestrator(seed, max_generations=1)
        
        start = time.time()
        orchestrator.run_generation(0)
        duration = time.time() - start
        
        # Should complete in under 1 second
        assert duration < 1.0
    
    @staticmethod
    def test_ten_generations_speed():
        """Test 10 generations complete reasonably"""
        seed = EvolvableSeed("TestSystem")
        orchestrator = EvolutionOrchestrator(seed, max_generations=10)
        
        start = time.time()
        for gen in range(10):
            orchestrator.run_generation(gen)
        duration = time.time() - start
        
        # Should complete in under 10 seconds
        assert duration < 10.0


# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def main():
    """Run all tests"""
    
    print("\n" + "="*80)
    print("EVOLUTIONARY RED TEAM FRAMEWORK - TEST SUITE")
    print("="*80 + "\n")
    
    runner = TestRunner()
    
    # Unit Tests
    print("📦 UNIT TESTS")
    print("-" * 80)
    runner.run_test("Defense config creation", UnitTests.test_defense_config_creation)
    runner.run_test("Defense strengthening", UnitTests.test_defense_config_strengthen)
    runner.run_test("Defense effectiveness", UnitTests.test_defense_config_effectiveness)
    runner.run_test("Input validation - null", UnitTests.test_input_validation_null)
    runner.run_test("Input validation - empty", UnitTests.test_input_validation_empty)
    runner.run_test("Type checking - list", UnitTests.test_type_checking_list)
    runner.run_test("Type checking - dict", UnitTests.test_type_checking_dict)
    runner.run_test("Bounds enforcement", UnitTests.test_bounds_enforcement_string)
    runner.run_test("Sanitization - SQL", UnitTests.test_sanitization_sql)
    runner.run_test("Evolvable seed creation", UnitTests.test_evolvable_seed_creation)
    runner.run_test("Evolvable seed strengthen", UnitTests.test_evolvable_seed_strengthen)
    runner.run_test("Attack pattern library", UnitTests.test_attack_pattern_library)
    
    # Integration Tests
    print("\n🔗 INTEGRATION TESTS")
    print("-" * 80)
    runner.run_test("Seed-defense integration", IntegrationTests.test_seed_defense_integration)
    runner.run_test("Red team executor init", IntegrationTests.test_red_team_executor)
    runner.run_test("Single attack execution", IntegrationTests.test_red_team_single_attack)
    runner.run_test("Full attack suite", IntegrationTests.test_red_team_full_suite)
    runner.run_test("Strengthening effect", IntegrationTests.test_defense_strengthening_effect)
    runner.run_test("Snapshot accuracy", IntegrationTests.test_snapshot_accuracy)
    
    # Evolution Tests
    print("\n🧬 EVOLUTION TESTS")
    print("-" * 80)
    runner.run_test("Single generation", EvolutionTests.test_single_generation)
    runner.run_test("Fitness improvement", EvolutionTests.test_fitness_improvement)
    runner.run_test("Defense activation", EvolutionTests.test_defense_activation)
    runner.run_test("Metrics collection", EvolutionTests.test_metrics_collection)
    
    # Regression Tests
    print("\n🔄 REGRESSION TESTS")
    print("-" * 80)
    runner.run_test("No division by zero", RegressionTests.test_no_division_by_zero)
    runner.run_test("Defense strength cap", RegressionTests.test_defense_strength_cap)
    runner.run_test("Empty exploit list", RegressionTests.test_empty_exploit_list)
    
    # Performance Tests
    print("\n⚡ PERFORMANCE TESTS")
    print("-" * 80)
    runner.run_test("Single generation speed", PerformanceTests.test_single_generation_speed)
    runner.run_test("Ten generations speed", PerformanceTests.test_ten_generations_speed)
    
    # Summary
    runner.print_summary()
    
    return 0 if runner.tests_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())