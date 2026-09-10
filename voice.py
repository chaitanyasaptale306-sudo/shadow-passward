import numpy as np

class VoiceEngine:
    """
    Analyzes energy distribution across frequency bins (simplified spectrum signature)
    and checks audio dynamic range for liveness/spoof detection.
    """

    @staticmethod
    def extract_voice_signature(audio_samples):
        samples = np.array(audio_samples, dtype=np.float32)
        if len(samples) < 100:
            return None, False

        # Liveness/Replay Check: Real speech has dynamic variance.
        # Flat amplitude variance often signals re-recorded or clipped audio.
        std_dev = np.std(samples)
        is_live = 0.005 < std_dev < 0.4  

        # Compute Fast Fourier Transform spectral distribution
        fft = np.abs(np.fft.rfft(samples))
        bands = np.array_split(fft, 16) # Split spectrum into 16 frequency bands
        band_energies = np.array([np.sum(b) for b in bands])
        
        # Normalize spectrum signature
        norm = np.linalg.norm(band_energies) + 1e-7
        signature = band_energies / norm
        
        return signature, is_live

    @classmethod
    def compare_voice(cls, stored_sig, current_audio_samples):
        curr_sig, is_live = cls.extract_voice_signature(current_audio_samples)
        if not is_live or curr_sig is None:
            return 0.0, False # Rejected due to liveness failure

        # Cosine distance match across frequency spectrum
        sim = float(np.dot(stored_sig, curr_sig)) * 100
        return min(100.0, max(0.0, sim)), True
        