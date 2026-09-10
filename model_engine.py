import numpy as np

class GestureEngine:
    """
    Computes spatial trajectories and velocity dynamics using normalized 21 hand landmarks.
    Calculates dynamic Euclidean spatial distance and DTW-inspired velocity profile match.
    """

    @staticmethod
    def extract_features(raw_landmarks_series):
        """
        Input: list of frame landmark arrays [(21, 3)...]
        Returns: Spatial norm array and Velocity profile
        """
        series = np.array(raw_landmarks_series) # (Frames, 21, 3)
        if len(series) < 5:
            return None, None

        # Center relative to wrist (landmark 0)
        wrist = series[:, 0:1, :]
        centered = series - wrist

        # Calculate Frame-to-Frame Velocity Profile
        velocities = np.linalg.norm(np.diff(centered, axis=0), axis=(1, 2))
        
        # Flatten spatial feature
        spatial_feature = centered.mean(axis=0).flatten()
        return spatial_feature, velocities

    @classmethod
    def compare_gestures(cls, stored_spatial, stored_vel, current_raw_series):
        curr_spatial, curr_vel = cls.extract_features(current_raw_series)
        if curr_spatial is None:
            return 0.0

        # Cosine spatial similarity
        dot = np.dot(stored_spatial, curr_spatial)
        norm = (np.linalg.norm(stored_spatial) * np.linalg.norm(curr_spatial)) + 1e-7
        spatial_sim = max(0.0, float(dot / norm)) * 100

        # Velocity rhythm match
        min_len = min(len(stored_vel), len(curr_vel))
        if min_len < 2:
            vel_sim = 50.0
        else:
            v1, v2 = stored_vel[:min_len], curr_vel[:min_len]
            vel_diff = np.mean(np.abs(v1 - v2))
            vel_sim = max(0.0, 100.0 - (vel_diff * 500))

        # Combined Gesture Score (70% Shape, 30% Rhythm/Speed)
        return (spatial_sim * 0.7) + (vel_sim * 0.3)
        