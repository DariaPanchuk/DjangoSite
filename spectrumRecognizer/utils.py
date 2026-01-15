import numpy as np
import librosa


def analyze_signal_data(file_path):
    try:
        y, sr = librosa.load(file_path, duration=60)
        fft_spectrum = np.fft.rfft(y)
        frequencies = np.fft.rfftfreq(len(y), 1 / sr)
        magnitude = np.abs(fft_spectrum)
        total_energy = np.sum(magnitude)
        top_indices = np.argsort(magnitude)[::-1][:20]
        top_indices = sorted(top_indices, key=lambda i: frequencies[i])

        results = []
        for i in top_indices:
            freq = frequencies[i]
            mag = magnitude[i]
            percent = (mag / total_energy) * 100 * 5
            results.append(f"{freq:.1f} Hz ({percent:.1f}%)")

        return ", ".join(results)

    except Exception as e:
        return f"Error: {str(e)}"