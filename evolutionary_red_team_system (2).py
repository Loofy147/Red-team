"""
EVOLUTIONARY RED TEAM FRAMEWORK - CORE SYSTEM
=============================================

A comprehensive, production-grade system for autonomous adversarial testing
and co-evolutionary defense adaptation.

Principles:
-----------
1. EVOLUTIONARY ADAPTATION: System learns through failure
2. ADVERSARIAL FEEDBACK: Red team guides defense evolution
3. CO-EVOLUTION: Both system and attacker evolve simultaneously
4. AUTONOMOUS IMPROVEMENT: No manual intervention required
5. MEASURABLE FITNESS: Quantifiable defense effectiveness
6. REPRODUCIBLE: All evolution tracked and analyzable

Architecture:
--------------
- DefenseFramework: Core protection mechanisms
- AttackPattern: Evolved attack vectors
- EvolvableSeed: System that adapts
- AdaptiveRedTeam: Learning attacker
- EvolutionOrchestrator: Co-evolution manager
- MetricsCollector: Performance tracking
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Callable, Optional
from abc import ABC, abstractmethod
import json
from datetime import datetime
import copy


# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

class DefenseType(Enum):
    """Categorization of defense mechanisms"""
    INPUT_VALIDATION = "validate_input"
    TYPE_CHECKING = "check_type"
    BOUNDS_ENFORCEMENT = "enforce_bounds"
    SANITIZATION = "sanitize"
    STATE_PROTECTION = "protect_state"
    RATE_LIMITING = "rate_limit"
    CRYPTOGRAPHY = "encrypt"
    LOGIC_HARDENING = "harden_logic"
    ANOMALY_DETECTION = "detect_anomaly"


class SeverityLevel(Enum):
    """Issue severity classification"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class EvolutionPhase(Enum):
    """Stages of evolution"""
    INITIALIZATION = "init"
    TESTING = "testing"
    ANALYSIS = "analysis"
    ADAPTATION = "adaptation"
    VERIFICATION = "verification"


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class DefenseConfig:
    """Configuration for a single defense mechanism"""
    defense_type: DefenseType
    active: bool = True
    strength: int = 1  # 1-10
    threshold: float = 0.5
    times_triggered: int = 0
    successful_blocks: int = 0
    false_positives: int = 0
    
    @property
    def effectiveness(self) -> float:
        """Calculate effectiveness ratio"""
        if self.times_triggered == 0:
            return 0.0
        return self.successful_blocks / self.times_triggered
    
    def strengthen(self, amount: int = 1):
        """Increase defense strength"""
        self.strength = min(10, self.strength + amount)
    
    def trigger(self, successful: bool):
        """Record a trigger event"""
        self.times_triggered += 1
        if successful:
            self.successful_blocks += 1
        else:
            self.false_positives += 1


@dataclass
class Exploit:
    """Discovered vulnerability"""
    vector: DefenseType
    description: str
    payload: Any
    severity: SeverityLevel
    difficulty: int  # 1-10
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    blocked: bool = False
    defense_reason: str = ""


@dataclass
class AttackPattern:
    """Reusable attack that evolves"""
    defense_type: DefenseType
    payload_generator: Callable
    description: str
    difficulty: int = 1
    success_count: int = 0
    attempt_count: int = 0
    adaptations: int = 0
    
    @property
    def success_rate(self) -> float:
        if self.attempt_count == 0:
            return 0.0
        return self.success_count / self.attempt_count
    
    def record_attempt(self, succeeded: bool):
        """Record attack outcome"""
        self.attempt_count += 1
        if succeeded:
            self.success_count += 1


@dataclass
class TestIssue:
    """Issue discovered during testing"""
    issue_type: str
    description: str
    severity: SeverityLevel
    affected_defense: Optional[DefenseType] = None
    root_cause: str = ""
    fix_applied: str = ""
    fix_verified: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class GenerationReport:
    """Complete report for one generation"""
    generation: int
    phase: EvolutionPhase
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    exploits: List[Exploit] = field(default_factory=list)
    issues: List[TestIssue] = field(default_factory=list)
    defenses_snapshot: Dict[str, DefenseConfig] = field(default_factory=dict)
    fitness_score: float = 0.0
    code_iterations: int = 0
    attacks_blocked: int = 0
    attacks_total: int = 0
    
    @property
    def success_rate(self) -> float:
        """Percentage of attacks blocked"""
        if self.attacks_total == 0:
            return 0.0
        return (self.attacks_blocked / self.attacks_total) * 100


# ============================================================================
# DEFENSE FRAMEWORK
# ============================================================================

class DefenseMechanism(ABC):
    """Base class for all defense mechanisms"""
    
    def __init__(self, config: DefenseConfig):
        self.config = config
    
    @abstractmethod
    def evaluate(self, value: Any) -> Tuple[bool, str]:
        """
        Evaluate if value should be blocked.
        Returns (should_block, reason)
        """
        pass
    
    def execute(self, value: Any) -> Tuple[bool, str]:
        """Execute defense with tracking"""
        should_block, reason = self.evaluate(value)
        self.config.trigger(should_block)
        return should_block, reason


class InputValidationDefense(DefenseMechanism):
    """Validates basic input properties"""
    
    def evaluate(self, value: Any) -> Tuple[bool, str]:
        if value is None:
            return True, "Rejected: null value"
        if isinstance(value, str) and value == "":
            return True, "Rejected: empty string"
        if self.config.strength >= 4:
            if not isinstance(value, (str, int, float)):
                return True, "Rejected: invalid base type"
        return False, "Passed validation"


class TypeCheckingDefense(DefenseMechanism):
    """Validates type safety"""
    
    def evaluate(self, value: Any) -> Tuple[bool, str]:
        # Reject complex types
        if isinstance(value, (list, dict, tuple, set)):
            return True, f"Rejected: {type(value).__name__} type"
        if hasattr(value, '__dict__') and not isinstance(value, (str, int, float)):
            return True, "Rejected: complex object"
        return False, "Passed type check"


class BoundsEnforcementDefense(DefenseMechanism):
    """Enforces size and length limits"""
    
    def evaluate(self, value: Any) -> Tuple[bool, str]:
        # Dynamic threshold based on strength
        max_len = 50 - (10 - self.config.strength) * 3
        
        if isinstance(value, str) and len(value) > max_len:
            return True, f"Rejected: string too long ({len(value)} > {max_len})"
        
        if isinstance(value, (list, dict)) and len(value) > max_len / 2:
            return True, f"Rejected: collection too large"
        
        return False, "Passed bounds check"


class SanitizationDefense(DefenseMechanism):
    """Blocks dangerous character patterns"""
    
    def evaluate(self, value: Any) -> Tuple[bool, str]:
        dangerous = ["'", '"', ";", "--", "/*", "*/", "DROP", "DELETE", "UNION"]
        
        if self.config.strength >= 8:
            dangerous.extend(["<", ">", "{", "}", "[", "]"])
        
        value_str = str(value).upper()
        for pattern in dangerous:
            if pattern in value_str:
                return True, f"Rejected: dangerous pattern '{pattern}'"
        
        return False, "Passed sanitization"


class StateProtectionDefense(DefenseMechanism):
    """Prevents state corruption attacks"""
    
    def evaluate(self, value: Any) -> Tuple[bool, str]:
        if isinstance(value, (dict, list)):
            value_str = str(value)
            if "_protected" in value_str or "_private" in value_str:
                return True, "Rejected: state injection attempt"
            if "exec" in value_str or "eval" in value_str:
                return True, "Rejected: code injection attempt"
        
        return False, "Passed state protection"


class RateLimitingDefense(DefenseMechanism):
    """Rate limiting mechanism"""
    
    def __init__(self, config: DefenseConfig):
        super().__init__(config)
        self.request_count = 0
    
    def evaluate(self, value: Any) -> Tuple[bool, str]:
        self.request_count += 1
        
        if self.config.strength >= 5 and self.request_count > self.config.strength * 2:
            self.request_count = 0
            return True, "Rejected: rate limit exceeded"
        
        return False, "Passed rate limit"


class CryptographyDefense(DefenseMechanism):
    """Cryptographic validation"""
    
    def evaluate(self, value: Any) -> Tuple[bool, str]:
        if self.config.strength >= 7:
            # Simulate cryptographic check
            if isinstance(value, str):
                # Check for payload tampering patterns
                if len(value) % 2 != 0 and value.count("'") > 0:
                    return True, "Rejected: crypto validation failed"
        
        return False, "Passed crypto check"


# ============================================================================
# DEFENSE FRAMEWORK MANAGER
# ============================================================================

class DefenseFramework:
    """Manages all defense mechanisms"""
    
    def __init__(self):
        self.defenses: Dict[DefenseType, DefenseMechanism] = {}
        self._initialize_defenses()
    
    def _initialize_defenses(self):
        """Initialize all defense mechanisms"""
        configs = {
            DefenseType.INPUT_VALIDATION: DefenseConfig(DefenseType.INPUT_VALIDATION, strength=2),
            DefenseType.TYPE_CHECKING: DefenseConfig(DefenseType.TYPE_CHECKING, strength=1),
            DefenseType.BOUNDS_ENFORCEMENT: DefenseConfig(DefenseType.BOUNDS_ENFORCEMENT, strength=1),
            DefenseType.SANITIZATION: DefenseConfig(DefenseType.SANITIZATION, strength=2),
            DefenseType.STATE_PROTECTION: DefenseConfig(DefenseType.STATE_PROTECTION, strength=1),
            DefenseType.RATE_LIMITING: DefenseConfig(DefenseType.RATE_LIMITING, active=False),
            DefenseType.CRYPTOGRAPHY: DefenseConfig(DefenseType.CRYPTOGRAPHY, active=False),
        }
        
        defense_classes = {
            DefenseType.INPUT_VALIDATION: InputValidationDefense,
            DefenseType.TYPE_CHECKING: TypeCheckingDefense,
            DefenseType.BOUNDS_ENFORCEMENT: BoundsEnforcementDefense,
            DefenseType.SANITIZATION: SanitizationDefense,
            DefenseType.STATE_PROTECTION: StateProtectionDefense,
            DefenseType.RATE_LIMITING: RateLimitingDefense,
            DefenseType.CRYPTOGRAPHY: CryptographyDefense,
        }
        
        for defense_type, config in configs.items():
            self.defenses[defense_type] = defense_classes[defense_type](config)
    
    def apply_defense(self, defense_type: DefenseType, value: Any) -> Tuple[bool, str]:
        """Apply a specific defense"""
        if defense_type not in self.defenses:
            return False, "Defense not found"
        
        defense = self.defenses[defense_type]
        if not defense.config.active:
            return False, "Defense inactive"
        
        try:
            return defense.execute(value)
        except Exception as e:
            return False, f"Defense execution error: {str(e)}"
    
    def activate(self, defense_type: DefenseType):
        """Activate a defense"""
        if defense_type in self.defenses:
            self.defenses[defense_type].config.active = True
    
    def strengthen(self, defense_type: DefenseType, amount: int = 1):
        """Increase defense strength"""
        if defense_type in self.defenses:
            self.defenses[defense_type].config.strengthen(amount)
    
    def get_snapshot(self) -> Dict[str, Dict]:
        """Get current state snapshot"""
        return {
            name.value: {
                "active": defense.config.active,
                "strength": defense.config.strength,
                "triggered": defense.config.times_triggered,
                "effectiveness": defense.config.effectiveness,
            }
            for name, defense in self.defenses.items()
        }


# ============================================================================
# EVOLVABLE SEED SYSTEM
# ============================================================================

class EvolvableSeed:
    """System that evolves defensive capabilities"""
    
    def __init__(self, name: str):
        self.name = name
        self.generation = 0
        self.defense_framework = DefenseFramework()
        self.evolution_history: List[GenerationReport] = []
    
    def test_defense(self, defense_type: DefenseType, payload: Any) -> Tuple[bool, str]:
        """Test a payload against a defense"""
        return self.defense_framework.apply_defense(defense_type, payload)
    
    def strengthen_defense(self, defense_type: DefenseType, amount: int = 1):
        """Strengthen a defense"""
        self.defense_framework.strengthen(defense_type, amount)
    
    def activate_defense(self, defense_type: DefenseType):
        """Activate a defense"""
        self.defense_framework.activate(defense_type)
    
    def get_defense_snapshot(self) -> Dict:
        """Get current defenses state"""
        return self.defense_framework.get_snapshot()
    
    def record_evolution(self, report: GenerationReport):
        """Record evolution step"""
        self.evolution_history.append(report)
        self.generation = report.generation