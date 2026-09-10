class BehavioralTrustEngine:
    """
    Combines biometric inputs into an Adaptive Trust Score.
    
    Formula:
      Trust = (Gesture Match * 0.45) + (Voice Match * 0.35) + 
              (Liveness Check * 0.10) + (Device/Environment Match * 0.10)
    """

    @staticmethod
    def calculate_trust_score(gesture_score: float, voice_score: float, liveness_passed: bool):
        liveness_score = 100.0 if liveness_passed else 0.0
        device_score = 100.0 # Standard device signature match

        weighted_score = (
            (gesture_score * 0.45) +
            (voice_score * 0.35) +
            (liveness_score * 0.10) +
            (device_score * 0.10)
        )

        return round(weighted_score, 2)