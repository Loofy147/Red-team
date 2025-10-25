"""
CONFIGURATION MANAGEMENT
========================
Centralized configuration with validation
"""

from dataclasses import dataclass, field
from typing import Optional
import os


@dataclass
class DefenseConfig:
    """Defense system configuration"""
    max_strength: int = 10
    initial_strength: int = 1
    strengthening_rate: float = 1.0
    activation_threshold: float = 0.5


@dataclass
class AttackConfig:
    """Attack system configuration"""
    initial_population_size: int = 6
    mutation_rate: float = 0.5
    crossover_rate: float = 0.7
    max_parameter_value: int = 10000


@dataclass
class EvolutionConfig:
    """Evolution orchestration configuration"""
    max_generations: int = 10
    convergence_threshold: float = 0.95
    stagnation_detection_window: int = 3
    fitness_improvement_threshold: float = 0.05


@dataclass
class PersistenceConfig:
    """Data persistence configuration"""
    enable_persistence: bool = True
    storage_backend: str = "json"  # "json" or "sqlite"
    data_directory: str = "./data"
    auto_save_interval: int = 5  # generations
    max_history_size: int = 1000


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_output: Optional[str] = None
    console_output: bool = True


@dataclass
class SystemConfig:
    """Complete system configuration"""
    defense: DefenseConfig = field(default_factory=DefenseConfig)
    attack: AttackConfig = field(default_factory=AttackConfig)
    evolution: EvolutionConfig = field(default_factory=EvolutionConfig)
    persistence: PersistenceConfig = field(default_factory=PersistenceConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    @classmethod
    def from_file(cls, filepath: str) -> 'SystemConfig':
        """Load configuration from file"""
        import json
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls(**data)

    def to_file(self, filepath: str):
        """Save configuration to file"""
        import json
        with open(filepath, 'w') as f:
            json.dump(self.__dict__, f, indent=2, default=lambda o: o.__dict__)


# Global configuration instance
_config: Optional[SystemConfig] = None


def get_config() -> SystemConfig:
    """Get global configuration"""
    global _config
    if _config is None:
        _config = SystemConfig()
    return _config


def set_config(config: SystemConfig):
    """Set global configuration"""
    global _config
    _config = config
