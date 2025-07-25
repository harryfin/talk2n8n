# Importieren der notwendigen Bibliotheken
import logging

from TTS.api import TTS
import sounddevice as sd
import numpy as np

logger = logging.getLogger("text_to_speech")


class TextToSpeech:
    def __init__(self, model_name: str = "tts_models/de/thorsten/vits"):
        """Initialisiert das Text-To-Speech-Modell."""
        # Modell wird einmalig geladen und bleibt im Speicher, solange das Programm läuft.
        self.tts = TTS(model_name=model_name)
        self.sample_rate = self.tts.synthesizer.output_sample_rate

    def speak(self, _text: str):
        """Generiert Sprache aus dem gegebenen Text und spielt das Ergebnis ab."""
        logger.info(f"TTS: Synthetisiere Text: {_text}")
        audio_samples = self._synthesize(_text)
        self._play(audio_samples)

    def _synthesize(self, _text: str) -> np.ndarray:
        """Generiert ein Audiosignal aus dem gegebenen Text."""
        audio_samples = self.tts.tts(_text)
        audio_samples = audio_samples / np.max(np.abs(audio_samples))
        return audio_samples

    def _play(self, _audio_samples: np.ndarray):
        """Spielt das gegebene Audiosignal ab."""
        sd.play(_audio_samples, self.sample_rate)
        sd.wait()


if __name__ == "__main__":
    tts = TextToSpeech()
    text = "Guten Tag! Dies ist ein Beispiel für die direkte Wiedergabe von Sprache."
    tts.speak(text)
