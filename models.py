from dataclasses import dataclass
from typing import List, Tuple

# ============================================================================
# SUBMARINE CABLES MODELS
# ============================================================================

@dataclass
class LandingStation:
    """A submarine cable landing station."""
    country: str
    lat: float
    lon: float
    station_name: str

@dataclass
class LandingStationResponse:
    """Response for landing station queries."""
    stations: List[LandingStation]
    count: int

@dataclass
class CableRoute:
    """A submarine cable route between countries."""
    country_a: str
    country_b: str
    waypoints: List[Tuple[float, float]]
    distance_km: float
    cable_name: str

@dataclass
class CableLatencyResponse:
    """Latency estimate for a cable route."""
    country_a: str
    country_b: str
    estimated_latency_ms: float
    distance_km: float

@dataclass
class CableOutageRiskResponse:
    """Outage risk assessment for a location."""
    lat: float
    lon: float
    risk_score: float
    risk_level: str
    nearby_cables: List[str]

# ============================================================================
# BASE STATION MODELS
# ============================================================================

@dataclass
class BaseStation:
    """A cellular base station."""
    station_id: str
    lat: float
    lon: float
    coverage_radius_km: float
    capacity: int
    signal_strength_dbm: float

@dataclass
class BaseStationResponse:
    """Response for base station queries."""
    stations: List[BaseStation]
    count: int

@dataclass
class CoverageStrengthResponse:
    """Signal strength at a specific location."""
    lat: float
    lon: float
    signal_strength_dbm: float
    nearest_station: str
    distance_to_station_km: float

@dataclass
class ProposedStation:
    """A proposed new base station location."""
    lat: float
    lon: float
    estimated_coverage_radius_km: float
    reason: str
    expected_improvement: str

@dataclass
class HandoverEvent:
    """A handover event during mobile movement."""
    timestamp: int
    lat: float
    lon: float
    from_station: str
    to_station: str
    signal_quality: str

@dataclass
class HandoverPathResponse:
    """Response for handover simulation."""
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    handover_events: List[HandoverEvent]
    total_handovers: int