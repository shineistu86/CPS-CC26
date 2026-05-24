from src.domain.entities import LocationInput, PredictionResult
from src.adapters.ml_repository import MLRepository
from src.infrastructure.gemini_client import GeminiClient

class EvaluateZonasi:
    def __init__(self, ml_repo: MLRepository, gemini_client: GeminiClient):
        self.ml_repo = ml_repo
        self.gemini_client = gemini_client

    def execute(self, location: LocationInput) -> PredictionResult:
        # 1. Get ML Prediction
        prob = self.ml_repo.predict(location.to_array())
        
        is_violation = prob >= 0.5
        verdict = "⚠️ PELANGGARAN" if is_violation else "✅ PATUH"
        
        # 2. Calculate Indicators (FR-02)
        indicators = {
            "jarak_ke_pasar_tradisional": {
                "nilai": location.jarak_pasar,
                "status": "Aman" if location.jarak_pasar >= 500 else "Terlalu Dekat (< 500m)",
                "is_safe": location.jarak_pasar >= 500
            },
            "kepadatan_kompetitor_500m": {
                "nilai": location.competitor_density,
                "status": "Tinggi" if location.competitor_density > 4 else "Normal",
                "is_safe": location.competitor_density <= 4
            }
        }

        # 3. Get AI Advisor recommendation (FR-03)
        ai_advice = self.gemini_client.generate_recommendation(
            verdict=verdict,
            jarak_pasar=location.jarak_pasar,
            competitor_density=location.competitor_density
        )

        confidence = prob * 100 if is_violation else (1 - prob) * 100

        return PredictionResult(
            probability=round(prob, 4),
            is_violation=is_violation,
            verdict=verdict,
            confidence_percentage=round(confidence, 2),
            indicators=indicators,
            ai_recommendation=ai_advice
        )
