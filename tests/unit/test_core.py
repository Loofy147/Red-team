"""
UNIT TESTS FOR CORE COMPONENTS
==============================
"""

from red_team.src.core.framework import DefenseConfig, DefenseType
from red_team.src.core.defenses import (
    InputValidationDefense,
    TypeCheckingDefense,
    BoundsEnforcementDefense,
    SanitizationDefense,
)
from red_team.src.core.seed import AttackPatternLibrary


def test_defense_config_creation():
    """Test defense configuration creation"""
    config = DefenseConfig(DefenseType.INPUT_VALIDATION, active=True, strength=5)
    assert config.active is True
    assert config.strength == 5
    assert config.times_triggered == 0


def test_defense_config_strengthen():
    """Test defense strengthening"""
    config = DefenseConfig(DefenseType.INPUT_VALIDATION, strength=5)
    config.strengthen(2)
    assert config.strength == 7
    config.strengthen(5)
    assert config.strength == 10  # Max cap


def test_defense_config_effectiveness():
    """Test effectiveness calculation"""
    config = DefenseConfig(DefenseType.INPUT_VALIDATION)
    assert config.effectiveness == 0.0

    config.trigger(True)
    config.trigger(True)
    config.trigger(False)
    assert config.effectiveness == 2 / 3


def test_input_validation_null():
    """Test input validation blocks null"""
    config = DefenseConfig(DefenseType.INPUT_VALIDATION)
    defense = InputValidationDefense(config)
    blocked, reason = defense.execute(None)
    assert blocked is True
    assert "null" in reason.lower()


def test_input_validation_empty():
    """Test input validation blocks empty string"""
    config = DefenseConfig(DefenseType.INPUT_VALIDATION)
    defense = InputValidationDefense(config)
    blocked, reason = defense.execute("")
    assert blocked is True
    assert "empty" in reason.lower()


def test_type_checking_list():
    """Test type checking blocks list"""
    config = DefenseConfig(DefenseType.TYPE_CHECKING)
    defense = TypeCheckingDefense(config)
    blocked, reason = defense.execute(["test"])
    assert blocked is True
    assert "list" in reason.lower()


def test_type_checking_dict():
    """Test type checking blocks dict"""
    config = DefenseConfig(DefenseType.TYPE_CHECKING)
    defense = TypeCheckingDefense(config)
    blocked, reason = defense.execute({"key": "value"})
    assert blocked is True


def test_bounds_enforcement_string():
    """Test bounds enforcement blocks large strings"""
    config = DefenseConfig(DefenseType.BOUNDS_ENFORCEMENT, strength=1)
    defense = BoundsEnforcementDefense(config)
    large_string = "A" * 200
    blocked, reason = defense.execute(large_string)
    assert blocked is True
    assert "oversized" in reason.lower() or "too long" in reason.lower()


def test_sanitization_sql():
    """Test sanitization blocks SQL injection"""
    config = DefenseConfig(DefenseType.SANITIZATION)
    defense = SanitizationDefense(config)
    blocked, reason = defense.execute("'; DROP TABLE--")
    assert blocked is True
    assert "dangerous" in reason.lower()


def test_evolvable_seed_creation(evolvable_seed):
    """Test evolvable seed creation"""
    assert evolvable_seed.name == "TestSeed"
    assert evolvable_seed.generation == 0
    assert len(evolvable_seed.defense_framework.defenses) > 0


def test_evolvable_seed_strengthen(evolvable_seed):
    """Test seed defense strengthening"""
    initial_strength = evolvable_seed.defense_framework.defenses[DefenseType.INPUT_VALIDATION].config.strength
    evolvable_seed.strengthen_defense(DefenseType.INPUT_VALIDATION, 3)
    new_strength = evolvable_seed.defense_framework.defenses[DefenseType.INPUT_VALIDATION].config.strength
    assert new_strength == initial_strength + 3


def test_attack_pattern_library():
    """Test attack pattern generation"""
    assert AttackPatternLibrary.null_injection() is None
    assert AttackPatternLibrary.empty_string() == ""
    assert isinstance(AttackPatternLibrary.type_confusion_list(), list)
    assert isinstance(AttackPatternLibrary.type_confusion_dict(), dict)
    assert len(AttackPatternLibrary.buffer_overflow_small()) > 100
