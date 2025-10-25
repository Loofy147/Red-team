"""
PYTEST CONFIGURATION & FIXTURES
================================
"""

import pytest
from red_team.src.core.framework import EvolvableSeed
from red_team.src.intelligence.defender import AutonomousIntelligence
from red_team.src.intelligence.attacker import AttackerIntelligence
from red_team.src.attacks.adaptive import AdaptiveAttackGenerator
from red_team.config import SystemConfig


@pytest.fixture
def system_config():
    """Provide test configuration"""
    config = SystemConfig()
    config.persistence.enable_persistence = False  # Disable for tests
    return config


@pytest.fixture
def evolvable_seed():
    """Provide evolvable seed"""
    return EvolvableSeed("TestSeed")


@pytest.fixture
def defender_intelligence(evolvable_seed):
    """Provide defender intelligence"""
    return AutonomousIntelligence(evolvable_seed)


@pytest.fixture
def attacker_intelligence():
    """Provide attacker intelligence"""
    return AttackerIntelligence()


@pytest.fixture
def attack_generator(attacker_intelligence):
    """Provide attack generator"""
    return AdaptiveAttackGenerator(attacker_intelligence)
