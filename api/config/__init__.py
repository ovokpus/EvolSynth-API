"""
Consolidated Configuration Module for EvolSynth API
Exports all configuration components from core and performance modules
"""

from typing import Optional

# Core configuration exports
from .core import (
    Settings,
    get_settings,
    settings,
    validate_api_keys,
    setup_environment
)

# Performance configuration exports
from .performance import (
    PerformanceConfig,
    OptimizationLevel,
    PerformanceMonitor,
    LoadBalancingConfig,
    get_optimization_config,
    apply_environment_overrides,
    get_performance_recommendations,
    get_production_config,
    integrate_with_core_settings,
    performance_monitor,
    OPTIMIZATION_PRESETS,
    PERFORMANCE_RECOMMENDATIONS
)

# Environment-specific configuration exports
from .environments import (
    Environment,
    BaseConfig,
    DevelopmentConfig,
    StagingConfig,
    ProductionConfig,
    TestingConfig,
    get_config,
    validate_config,
    create_environment_files
)

# Convenience functions for integrated configuration
def get_integrated_config(environment: Optional[str] = None):
    """Get integrated configuration with both core and performance settings"""
    # Get environment-specific config
    env_config = get_config(environment)
    
    # Get core settings (for backward compatibility)
    core_settings = settings
    
    # Get performance config integrated with core settings
    perf_config = integrate_with_core_settings(core_settings)
    
    return {
        "environment": env_config,
        "core": core_settings,
        "performance": perf_config
    }


# Export everything for backward compatibility
__all__ = [
    # Core configuration
    "Settings",
    "get_settings", 
    "settings",
    "validate_api_keys",
    "setup_environment",
    
    # Performance configuration
    "PerformanceConfig",
    "OptimizationLevel",
    "PerformanceMonitor",
    "LoadBalancingConfig",
    "get_optimization_config",
    "apply_environment_overrides",
    "get_performance_recommendations",
    "get_production_config",
    "integrate_with_core_settings",
    "performance_monitor",
    "OPTIMIZATION_PRESETS",
    "PERFORMANCE_RECOMMENDATIONS",
    
    # Environment configuration
    "Environment",
    "BaseConfig",
    "DevelopmentConfig",
    "StagingConfig", 
    "ProductionConfig",
    "TestingConfig",
    "get_config",
    "validate_config",
    "create_environment_files",
    
    # Integrated configuration
    "get_integrated_config"
] 