"""
Lamarr Energy Tracker - A wrapper for CodeCarbon to track energy consumption
"""

__version__ = "0.1.0"

def __getattr__(name):
    if name == "EnergyTracker":
        from .tracker import EnergyTracker
        return EnergyTracker
    if name == "GroundTruthTracker":
        from .ground_truth_tracking import GroundTruthTracker
        return GroundTruthTracker
    if name == "GroundTruthTrackingServer":
        from .ground_truth_tracking import GroundTruthTrackingServer
        return GroundTruthTrackingServer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
