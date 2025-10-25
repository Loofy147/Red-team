"""
INTEGRATION TESTS FOR EVOLUTION CYCLE
======================================
"""

from red_team.src.core.framework import DefenseType, EvolvableSeed
from red_team.src.core.seed import RedTeamExecutor
from red_team.src.evolution.orchestrator import EvolutionOrchestrator


def test_seed_defense_integration(evolvable_seed):
    """Test seed and defense framework integration"""
    blocked, reason = evolvable_seed.test_defense(DefenseType.INPUT_VALIDATION, None)
    assert blocked is True


def test_red_team_executor(evolvable_seed):
    """Test red team executor"""
    red_team = RedTeamExecutor(evolvable_seed)
    assert len(red_team.attack_patterns) > 0


def test_red_team_single_attack(evolvable_seed):
    """Test single attack execution"""
    red_team = RedTeamExecutor(evolvable_seed)
    pattern = red_team.attack_patterns[0]
    exploit = red_team.execute_attack(pattern)
    assert exploit is not None
    assert hasattr(exploit, "blocked")
    assert hasattr(exploit, "description")


def test_red_team_full_suite(evolvable_seed):
    """Test full attack suite"""
    red_team = RedTeamExecutor(evolvable_seed)
    exploits, blocked, total = red_team.execute_suite()
    assert len(exploits) == total
    assert blocked <= total
    assert blocked >= 0


def test_defense_strengthening_effect(evolvable_seed):
    """Test that strengthening actually improves defense"""
    red_team = RedTeamExecutor(evolvable_seed)

    # First attack
    exploits1, blocked1, total1 = red_team.execute_suite()

    # Strengthen all defenses
    for defense_type in DefenseType:
        evolvable_seed.strengthen_defense(defense_type, 5)

    # Second attack
    exploits2, blocked2, total2 = red_team.execute_suite()

    # Should block more or equal attacks
    assert blocked2 >= blocked1


def test_snapshot_accuracy(evolvable_seed):
    """Test defense snapshot accuracy"""
    snapshot1 = evolvable_seed.get_defense_snapshot()

    evolvable_seed.strengthen_defense(DefenseType.INPUT_VALIDATION, 3)
    snapshot2 = evolvable_seed.get_defense_snapshot()

    assert snapshot2["validate_input"]["strength"] == snapshot1["validate_input"]["strength"] + 3


def test_single_generation(evolvable_seed):
    """Test single generation execution"""
    orchestrator = EvolutionOrchestrator(evolvable_seed)
    report = orchestrator.run_generation(0)

    assert report.generation == 0
    assert report.attacks_total > 0
    assert 0 <= report.fitness_score <= 100


def test_fitness_improvement(evolvable_seed):
    """Test that fitness improves over generations"""
    orchestrator = EvolutionOrchestrator(evolvable_seed)

    fitness_scores = []
    for gen in range(3):
        report = orchestrator.run_generation(gen)
        fitness_scores.append(report.fitness_score)

    # Fitness should generally improve
    assert fitness_scores[-1] >= fitness_scores[0]
