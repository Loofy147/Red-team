"""
RED TEAM ENGINE - ADAPTIVE ATTACK GENERATION
=============================================

Implements evolutionary attack patterns that adapt based on defense strength.

Key Concepts:
-------------
1. ATTACK PATTERN GENOME: Reusable attack templates with evolution
2. ADAPTIVE DIFFICULTY: Attacks become harder as defenses strengthen
3. SUCCESS TRACKING: Patterns that work more are emphasized
4. PAYLOAD MUTATION: Attack payloads evolve based on outcomes
5. VECTOR COVERAGE: Ensures all defense types are tested
"""

from typing import List, Tuple, Dict, Any, Callable
from dataclasses import dataclass, field
import random
from enum import Enum

from .framework import (
    DefenseType, Exploit, AttackPattern, SeverityLevel,
    TestIssue, GenerationReport, EvolutionPhase
)


# ============================================================================
# ATTACK PATTERN LIBRARY
# ============================================================================

class AttackPatternLibrary:
    """Repository of attack patterns"""
    
    @staticmethod
    def null_injection():
        """Null pointer injection"""
        return None
    
    @staticmethod
    def empty_string():
        """Empty string attack"""
        return ""
    
    @staticmethod
    def type_confusion_list():
        """Array/list type confusion"""
        return ["malicious", "payload", "data"]
    
    @staticmethod
    def type_confusion_dict():
        """Dictionary/object type confusion"""
        return {"payload": "malicious", "exec": "true"}
    
    @staticmethod
    def buffer_overflow_small(gen: int = 0):
        """String overflow - scales with generation"""
        size = 500 + (gen * 100)
        return "A" * size
    
    @staticmethod
    def sql_injection():
        """SQL injection pattern"""
        return "'; DROP TABLE users--"
    
    @staticmethod
    def sql_injection_obfuscated(gen: int = 0):
        """Obfuscated SQL injection"""
        if gen < 3:
            return "1'/**/OR/**/1=1"
        else:
            return "1'/*!50000OR*/'1'='1"
    
    @staticmethod
    def comment_injection():
        """Comment-based injection"""
        return "/* malicious */ UNION SELECT * FROM admin"
    
    @staticmethod
    def state_corruption():
        """State object injection"""
        return {"_protected": "corrupted", "_internal": "compromised"}
    
    @staticmethod
    def code_injection():
        """Code execution injection"""
        return {"eval": "exec('malicious_code')", "__builtins__": "override"}
    
    @staticmethod
    def unicode_overflow():
        """Unicode character overflow"""
        return "🔴" * 200 + "\x00" * 50


# ============================================================================
# RED TEAM EXECUTOR
# ============================================================================

from red_team.config import get_config

class RedTeamExecutor:
    """Executes attack patterns against target system"""
    
    def __init__(self, target_seed, config=None):
        if config is None:
            config = get_config().attack
        self.config = config
        self.target = target_seed
        self.attack_patterns: List[AttackPattern] = []
        self.generation_number = 0
        self._initialize_patterns()
    
    def _initialize_patterns(self):
        """Initialize attack pattern suite"""
        # In a real system, this would be data-driven
        patterns = [
            ("Null injection attack", DefenseType.INPUT_VALIDATION, AttackPatternLibrary.null_injection, 1),
            ("Empty string bypass", DefenseType.INPUT_VALIDATION, AttackPatternLibrary.empty_string, 1),
            ("List type confusion", DefenseType.TYPE_CHECKING, AttackPatternLibrary.type_confusion_list, 2),
            ("Dict type confusion", DefenseType.TYPE_CHECKING, AttackPatternLibrary.type_confusion_dict, 2),
            ("String buffer overflow", DefenseType.BOUNDS_ENFORCEMENT, lambda: AttackPatternLibrary.buffer_overflow_small(self.generation_number), 3),
            ("SQL injection", DefenseType.SANITIZATION, AttackPatternLibrary.sql_injection, 4),
            ("Obfuscated SQL injection", DefenseType.SANITIZATION, lambda: AttackPatternLibrary.sql_injection_obfuscated(self.generation_number), 5),
            ("State object corruption", DefenseType.STATE_PROTECTION, AttackPatternLibrary.state_corruption, 3),
            ("Code execution injection", DefenseType.STATE_PROTECTION, AttackPatternLibrary.code_injection, 5),
        ]

        for i in range(min(len(patterns), self.config.initial_population_size)):
            name, defense, generator, difficulty = patterns[i]
            self.attack_patterns.append(
                AttackPattern(
                    defense_type=defense,
                    payload_generator=generator,
                    description=name,
                    difficulty=difficulty
                )
            )
    
    def execute_attack(self, pattern: AttackPattern) -> Exploit:
        """Execute single attack pattern"""
        try:
            payload = pattern.payload_generator()
        except Exception as e:
            payload = None
        
        blocked, reason = self.target.test_defense(pattern.defense_type, payload)
        pattern.record_attempt(not blocked)
        
        severity = self._calculate_severity(pattern)
        
        exploit = Exploit(
            vector=pattern.defense_type,
            description=pattern.description,
            payload=payload,
            severity=severity,
            difficulty=pattern.difficulty,
            blocked=blocked,
            defense_reason=reason
        )
        
        return exploit
    
    def execute_suite(self) -> Tuple[List[Exploit], int, int]:
        """Execute all attack patterns"""
        exploits = []
        blocked_count = 0
        
        for pattern in self.attack_patterns:
            exploit = self.execute_attack(pattern)
            exploits.append(exploit)
            
            if exploit.blocked:
                blocked_count += 1
        
        return exploits, blocked_count, len(exploits)
    
    def _calculate_severity(self, pattern: AttackPattern) -> SeverityLevel:
        """Calculate exploit severity"""
        if pattern.difficulty >= 5:
            return SeverityLevel.CRITICAL
        elif pattern.difficulty >= 4:
            return SeverityLevel.HIGH
        elif pattern.difficulty >= 2:
            return SeverityLevel.MEDIUM
        else:
            return SeverityLevel.LOW
    
    def get_pattern_status(self) -> Dict[str, Any]:
        """Get attack pattern effectiveness"""
        return {
            pattern.description: {
                "success_rate": pattern.success_rate,
                "difficulty": pattern.difficulty,
                "attempts": pattern.attempt_count,
                "successes": pattern.success_count,
            }
            for pattern in self.attack_patterns
        }


# ============================================================================
# RED TEAM ADAPTATION ENGINE
# ============================================================================

class RedTeamAdaptationEngine:
    """Evolves attack patterns based on results"""
    
    def __init__(self, executor: RedTeamExecutor):
        self.executor = executor
        self.adaptation_history: List[str] = []
    
    def analyze_results(self, exploits: List[Exploit]) -> List[TestIssue]:
        """Analyze attack results and identify patterns"""
        issues = []
        
        # Group by defense type
        failures_by_defense = {}
        for exploit in exploits:
            if not exploit.blocked:
                defense_name = exploit.vector.value
                if defense_name not in failures_by_defense:
                    failures_by_defense[defense_name] = []
                failures_by_defense[defense_name].append(exploit)
        
        # Create issues for failed defenses
        for defense_name, failed_exploits in failures_by_defense.items():
            issue = TestIssue(
                issue_type="DEFENSE_FAILURE",
                description=f"{defense_name} failed against {len(failed_exploits)} attacks",
                severity=SeverityLevel.CRITICAL if len(failed_exploits) > 2 else SeverityLevel.HIGH,
                affected_defense=failed_exploits[0].vector
            )
            issues.append(issue)
        
        return issues
    
    def adapt_patterns(self, exploits: List[Exploit]) -> List[str]:
        """Adapt attack patterns based on results"""
        adaptations = []
        
        for pattern in self.executor.attack_patterns:
            if pattern.success_rate > 0.6:
                # Pattern works well - increase difficulty
                old_diff = pattern.difficulty
                pattern.difficulty = min(10, pattern.difficulty + 1)
                pattern.adaptations += 1
                adaptations.append(f"📈 Increased difficulty '{pattern.description}': {old_diff} → {pattern.difficulty}")
            
            elif pattern.success_rate < 0.2 and pattern.attempt_count > 2:
                # Pattern failing - evolve payload
                pattern = self._mutate_payload(pattern, exploits)
                adaptations.append(f"🧬 Mutated payload for '{pattern.description}'")
        
        self.adaptation_history.extend(adaptations)
        return adaptations
    
    def _mutate_payload(self, pattern: AttackPattern, exploits: List[Exploit]) -> AttackPattern:
        """Mutate attack payload for better effectiveness"""
        
        # Mutation strategies based on defense type
        if pattern.defense_type == DefenseType.BOUNDS_ENFORCEMENT:
            # Increase payload size
            pattern.difficulty += 1
        
        elif pattern.defense_type == DefenseType.SANITIZATION:
            # Try obfuscation
            pattern.difficulty += 1
        
        elif pattern.defense_type == DefenseType.TYPE_CHECKING:
            # Try nested types
            pattern.difficulty += 1
        
        return pattern