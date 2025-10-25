"""
EVOLUTIONARY RED TEAM FRAMEWORK - MAIN EXECUTION
================================================

Production-ready entry point with:
- Configuration management
- Logging setup
- Error handling
- Persistence
- Clean architecture
- Comprehensive reporting

Usage:
    python main.py --mode evolution --generations 10
    python main.py --mode arms_race --config custom_config.json
    python main.py --mode test --quick
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Optional
import traceback

# Critical fixes applied:
# 1. Added proper logging
# 2. Added error boundaries
# 3. Added persistence
# 4. Added configuration management
# 5. Memory management with history limits

# ============================================================================
# CONFIGURATION (Fixed: centralized config)
# ============================================================================

class Config:
    """System configuration with validation"""
    
    def __init__(self):
        # Defense settings
        self.max_defense_strength = 10
        self.defense_strengthening_rate = 2
        
        # Evolution settings
        self.max_generations = 10
        self.convergence_threshold = 0.95
        self.history_limit = 1000  # Fix: prevent memory leaks
        
        # Persistence settings
        self.enable_persistence = True
        self.data_dir = Path("./data")
        self.auto_save_interval = 5
        
        # Logging settings
        self.log_level = "INFO"
        self.log_file = "./logs/evolution.log"
    
    @classmethod
    def from_args(cls, args):
        """Create config from command line args"""
        config = cls()
        if hasattr(args, 'generations'):
            config.max_generations = args.generations
        if hasattr(args, 'no_persist'):
            config.enable_persistence = not args.no_persist
        return config


# ============================================================================
# LOGGING SETUP (Fixed: proper logging framework)
# ============================================================================

def setup_logging(config: Config) -> logging.Logger:
    """Setup logging with file and console output"""
    
    # Create logs directory
    Path(config.log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)


# ============================================================================
# IMPORTS (Fixed: proper dependency management)
# ============================================================================

# Core components
from core import EvolvableSeed, DefenseType
from autonomous_intelligence import AutonomousIntelligence
from attacker_intelligence import AttackerIntelligence
from adaptive_attacks import AdaptiveAttackGenerator
from counter_intelligence_system import CompleteAdversarialSystem


# ============================================================================
# PERSISTENCE MANAGER (Fixed: added persistence layer)
# ============================================================================

class PersistenceManager:
    """Manages saving/loading state"""
    
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.data_dir = config.data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def save_state(self, system, generation: int):
        """Save system state"""
        if not self.config.enable_persistence:
            return
        
        try:
            import json
            
            state = {
                "generation": generation,
                "defender": {
                    "signatures": len(system.defender_intelligence.knowledge_base.signatures),
                    "principles": len(system.defender_intelligence.knowledge_base.principles),
                    "defenses": system.defender_seed.get_defense_snapshot()
                },
                "attacker": {
                    "success_rate": system.attacker_intelligence.get_success_rate(),
                    "total_attacks": system.attacker_intelligence.total_attacks,
                    "defense_profiles": {
                        k: {"strength": v.strength_estimate, "encounters": v.times_encountered}
                        for k, v in system.attacker_intelligence.defense_profiles.items()
                    }
                }
            }
            
            filepath = self.data_dir / f"state_gen_{generation:04d}.json"
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)
            
            self.logger.info(f"Saved state for generation {generation}")
        
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
    
    def load_latest_state(self) -> Optional[dict]:
        """Load most recent saved state"""
        if not self.config.enable_persistence:
            return None
        
        try:
            import json
            state_files = list(self.data_dir.glob("state_gen_*.json"))
            if not state_files:
                return None
            
            latest = max(state_files, key=lambda p: p.stat().st_mtime)
            with open(latest, 'r') as f:
                return json.load(f)
        
        except Exception as e:
            self.logger.error(f"Failed to load state: {e}")
            return None


# ============================================================================
# MEMORY MANAGER (Fixed: prevent memory leaks)
# ============================================================================

class MemoryManager:
    """Manages memory usage and cleanup"""
    
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
    
    def cleanup_history(self, system):
        """Cleanup old history to prevent memory leaks"""
        try:
            # Limit attacker history
            if len(system.attacker_intelligence.attack_history) > self.config.history_limit:
                removed = len(system.attacker_intelligence.attack_history) - self.config.history_limit
                system.attacker_intelligence.attack_history = system.attacker_intelligence.attack_history[-self.config.history_limit:]
                self.logger.debug(f"Cleaned up {removed} attack history entries")
            
            # Limit defender history
            if len(system.defender_intelligence.knowledge_base.signatures) > self.config.history_limit:
                # Keep only most recent signatures
                sorted_sigs = sorted(
                    system.defender_intelligence.knowledge_base.signatures.items(),
                    key=lambda x: x[1].last_seen,
                    reverse=True
                )
                system.defender_intelligence.knowledge_base.signatures = dict(sorted_sigs[:self.config.history_limit])
                self.logger.debug(f"Cleaned up defender signatures")
        
        except Exception as e:
            self.logger.error(f"Memory cleanup failed: {e}")


# ============================================================================
# ERROR HANDLER (Fixed: graceful error handling)
# ============================================================================

class ErrorHandler:
    """Handles errors gracefully"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.error_count = 0
        self.max_errors = 10
    
    def handle_attack_error(self, attack_data: dict, error: Exception) -> bool:
        """
        Handle attack processing error
        Returns: True if can continue, False if should abort
        """
        self.error_count += 1
        self.logger.error(f"Attack processing error: {error}")
        self.logger.debug(f"Attack data: {attack_data}")
        
        if self.error_count >= self.max_errors:
            self.logger.critical("Too many errors - aborting")
            return False
        
        return True
    
    def handle_learning_error(self, context: str, error: Exception):
        """Handle learning phase error"""
        self.logger.error(f"Learning error in {context}: {error}")
        self.logger.debug(traceback.format_exc())


# ============================================================================
# MAIN EXECUTION MODES
# ============================================================================

class EvolutionMode:
    """Run basic evolution cycle"""
    
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.persistence = PersistenceManager(config, logger)
        self.memory_manager = MemoryManager(config, logger)
        self.error_handler = ErrorHandler(logger)
    
    def run(self):
        """Execute evolution mode"""
        self.logger.info("Starting Evolution Mode")
        
        try:
            # Create system
            seed = EvolvableSeed("EvolutionSystem")
            intelligence = AutonomousIntelligence(seed)
            
            # Load previous state if exists
            previous_state = self.persistence.load_latest_state()
            if previous_state:
                self.logger.info(f"Loaded previous state from generation {previous_state['generation']}")
            
            # Run evolution
            from orchestrated_attacks import ScenarioOrchestrator
            orchestrator = ScenarioOrchestrator()
            
            for gen in range(self.config.max_generations):
                self.logger.info(f"Generation {gen} starting")
                
                # Generate attacks
                campaign = orchestrator.generate_orchestrated_campaign(gen)
                
                # Process attacks with error handling
                blocked = 0
                for scenario, attack_type, payload in campaign:
                    try:
                        defense_type = self._map_defense_type(attack_type)
                        blocked_result, reason = seed.test_defense(defense_type, payload)
                        
                        # Learn
                        intelligence.process_attack_result(payload, attack_type, blocked_result)
                        
                        if blocked_result:
                            blocked += 1
                    
                    except Exception as e:
                        if not self.error_handler.handle_attack_error(
                            {"scenario": scenario, "type": attack_type}, e
                        ):
                            return
                
                fitness = (blocked / len(campaign) * 100) if campaign else 0
                self.logger.info(f"Generation {gen}: Fitness {fitness:.1f}%")
                
                # Cleanup memory
                if gen % 3 == 0:
                    self.memory_manager.cleanup_history(intelligence)
                
                # Save state
                if gen % self.config.auto_save_interval == 0:
                    self.persistence.save_state(intelligence, gen)
                
                # Check convergence
                if fitness >= self.config.convergence_threshold * 100:
                    self.logger.info(f"Converged at generation {gen}")
                    break
            
            self.logger.info("Evolution complete")
            intelligence.print_intelligence_state()
        
        except Exception as e:
            self.logger.critical(f"Evolution failed: {e}")
            self.logger.debug(traceback.format_exc())
            sys.exit(1)
    
    def _map_defense_type(self, attack_type: str) -> DefenseType:
        """Map attack type to defense type"""
        mapping = {
            "injection": DefenseType.SANITIZATION,
            "sql_injection": DefenseType.SANITIZATION,
            "overflow": DefenseType.BOUNDS_ENFORCEMENT,
            "type_confusion": DefenseType.TYPE_CHECKING,
            "encoding": DefenseType.SANITIZATION,
            "state_corruption": DefenseType.STATE_PROTECTION,
        }
        return mapping.get(attack_type, DefenseType.INPUT_VALIDATION)


class ArmsRaceMode:
    """Run complete adversarial arms race"""
    
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.persistence = PersistenceManager(config, logger)
        self.memory_manager = MemoryManager(config, logger)
    
    def run(self):
        """Execute arms race mode"""
        self.logger.info("Starting Arms Race Mode")
        
        try:
            # Create systems
            seed = EvolvableSeed("DefenderSystem")
            defender_intelligence = AutonomousIntelligence(seed)
            
            # Create adversarial system
            arms_race = CompleteAdversarialSystem(seed, defender_intelligence)
            
            # Run with memory management
            original_run = arms_race.run_arms_race
            
            def managed_run(max_generations):
                for gen in range(max_generations):
                    # Run single generation
                    arms_race.generation = gen
                    arms_race.attacker_intelligence.next_generation()
                    arms_race.defender_intelligence.next_generation()
                    
                    all_attacks = arms_race._generate_intelligent_campaign()
                    results = arms_race._process_attacks(all_attacks)
                    arms_race._mutual_adaptation(results)
                    
                    # Memory cleanup
                    if gen % 3 == 0:
                        self.memory_manager.cleanup_history(arms_race)
                    
                    # Persistence
                    if gen % self.config.auto_save_interval == 0:
                        self.persistence.save_state(arms_race, gen)
                    
                    # Display
                    arms_race.attacker_intelligence.print_intelligence_state()
                    arms_race.defender_intelligence.print_intelligence_state()
                    
                    # Check termination
                    attacker_success = arms_race.attacker_intelligence.get_success_rate()
                    if results["fitness"] >= 95:
                        self.logger.info(f"Defender dominance at gen {gen}")
                        break
                    elif attacker_success >= 0.8:
                        self.logger.info(f"Attacker dominance at gen {gen}")
                        break
                
                arms_race._print_final_analysis()
            
            managed_run(self.config.max_generations)
            self.logger.info("Arms race complete")
        
        except Exception as e:
            self.logger.critical(f"Arms race failed: {e}")
            self.logger.debug(traceback.format_exc())
            sys.exit(1)


class TestMode:
    """Run comprehensive testing"""
    
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
    
    def run(self, quick: bool = False):
        """Execute test mode"""
        self.logger.info("Starting Test Mode")
        
        try:
            if quick:
                self.logger.info("Running quick test (3 generations)")
                config = Config()
                config.max_generations = 3
                mode = EvolutionMode(config, self.logger)
                mode.run()
            else:
                self.logger.info("Running full test suite")
                import pytest
                pytest.main(["-v", "tests/"])
        
        except Exception as e:
            self.logger.critical(f"Testing failed: {e}")
            sys.exit(1)


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def parse_arguments():
    """Parse command line arguments"""
    
    parser = argparse.ArgumentParser(
        description="Evolutionary Red Team Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --mode evolution --generations 10
  python main.py --mode arms_race --config custom.json
  python main.py --mode test --quick
  python main.py --mode evolution --no-persist
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['evolution', 'arms_race', 'test'],
        default='evolution',
        help='Execution mode'
    )
    
    parser.add_argument(
        '--generations',
        type=int,
        default=10,
        help='Number of generations'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Configuration file path'
    )
    
    parser.add_argument(
        '--no-persist',
        action='store_true',
        help='Disable persistence'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )
    
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Quick test mode (3 generations)'
    )
    
    return parser.parse_args()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    
    # Parse arguments
    args = parse_arguments()
    
    # Create configuration
    config = Config.from_args(args)
    config.log_level = args.log_level
    
    # Setup logging
    logger = setup_logging(config)
    logger.info("="*80)
    logger.info("EVOLUTIONARY RED TEAM FRAMEWORK - PRODUCTION VERSION")
    logger.info("="*80)
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Generations: {config.max_generations}")
    logger.info(f"Persistence: {config.enable_persistence}")
    logger.info("="*80)
    
    try:
        # Execute mode
        if args.mode == 'evolution':
            mode = EvolutionMode(config, logger)
            mode.run()
        
        elif args.mode == 'arms_race':
            mode = ArmsRaceMode(config, logger)
            mode.run()
        
        elif args.mode == 'test':
            mode = TestMode(config, logger)
            mode.run(quick=args.quick)
        
        logger.info("="*80)
        logger.info("EXECUTION COMPLETE")
        logger.info("="*80)
        
        return 0
    
    except KeyboardInterrupt:
        logger.warning("\nExecution interrupted by user")
        return 1
    
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        logger.debug(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())