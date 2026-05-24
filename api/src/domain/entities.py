from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class LocationInput:
    latitude: float
    longitude: float
    competitor_density: int
    jarak_kompetitor: float
    head_to_head: int
    jarak_pasar: float
    cluster_macro: int
    cluster_hotspot: int

    def to_array(self):
        return [
            self.latitude,
            self.longitude,
            self.competitor_density,
            self.jarak_kompetitor,
            self.head_to_head,
            self.jarak_pasar,
            self.cluster_macro,
            self.cluster_hotspot
        ]

@dataclass
class PredictionResult:
    probability: float
    is_violation: bool
    verdict: str
    confidence_percentage: float
    indicators: Dict[str, Any]
    ai_recommendation: str
