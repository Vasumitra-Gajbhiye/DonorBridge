"""Pool generation calibrated to Indian (and US) statistics.

Owner: Lead (re-exports only; the modules belong to Generator)
Implemented in: P1
"""

from donorbridge.generator.calibration import INDIA, US, Calibration
from donorbridge.generator.regions import split_by_region
from donorbridge.generator.report import calibration_report
from donorbridge.generator.saidman import (
    GenerationReport,
    PoolGenerator,
    SaidmanGenerator,
    make_generator,
)
from donorbridge.generator.survival_models import SensitisationSurvival

__all__ = [
    "INDIA",
    "US",
    "Calibration",
    "GenerationReport",
    "PoolGenerator",
    "SaidmanGenerator",
    "SensitisationSurvival",
    "calibration_report",
    "make_generator",
    "split_by_region",
]
