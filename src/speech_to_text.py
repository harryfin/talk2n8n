import logging
import time

import speech_recognition as sr

from src.exception import ListeningTimeoutError

logger = logging.getLogger("speech_to_text")


def _normalize_text(txt: str):
    """Entfernt alle Sonderzeichen und Leerzeichen und macht alles klein."""
    return "".join(e for e in txt if e.isalnum()).lower()


class SpeechToText:

    def __init__(self, recognizer_engine="recognize_google"):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        self.recognizer_engine = recognizer_engine

    def start_listening(self, source, timeout=None, phrase_time_limit=3):
        """Start listening and capture audio from the microphone."""
        try:
            logger.info("Listening for audio...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source, phrase_time_limit=phrase_time_limit, timeout=timeout)
            logger.info("Audio captured.")
            return audio
        except sr.WaitTimeoutError:
            raise ListeningTimeoutError("Listening timed out while waiting for phrase.")

    def recognize_speech(self, audio, language="de", recognizer_engine=None) -> str:
        """Recognize speech from the audio."""

        if recognizer_engine is None:
            recognizer_engine = self.recognizer_engine

        try:
            _recognizer = getattr(self.recognizer, recognizer_engine)
        except AttributeError:
            logger.error("Recognizer engine not found.")
            raise AttributeError("Recognizer engine not found.")

        try:
            recognized_text = _recognizer(audio, language=language)
            logger.info("Recognized: %s", recognized_text)
            return recognized_text
        except sr.UnknownValueError:
            logger.error("Could not understand the audio.")
            return ""
        except sr.RequestError as e:
            logger.error("Failed to connect to the recognition service: %s", e)
            return ""

    def listen(self, kwargs_listening: dict = None) -> str:
        """Listen to audio and return the recognized text."""

        if kwargs_listening is None:
            kwargs_listening = {}

        current_time = None
        if "timeout" in kwargs_listening:
            current_time = time.time()

        while True:
            with self.microphone as source:
                audio = self.start_listening(source, **kwargs_listening)
                recognized_text = self.recognize_speech(audio)
                logger.info("spoken for command:", recognized_text)

                if not recognized_text:  # None or empty string
                    # if background noise is too loud, the timeout will not be reached
                    if "timeout" in kwargs_listening:
                        if time.time() - current_time > kwargs_listening["timeout"]:
                            raise ListeningTimeoutError("Listening timed out while waiting for command.")

                if recognized_text and isinstance(recognized_text, str):
                    return recognized_text

    def listen_to_phrase(self, phrase: str = None, kwargs_listening: dict = None) -> str:
        """Listen to the activation phrase and return True if it is recognized."""

        if kwargs_listening is None:
            kwargs_listening = {}

        if phrase is None:
            raise ValueError("Phrases must be provided.")

        target_phrase = _normalize_text(phrase)

        while True:
            with self.microphone as source:
                audio = self.start_listening(source, **kwargs_listening)
                recognized_text = self.recognize_speech(audio)
                if recognized_text and isinstance(recognized_text, str):
                    # check if the prepared phrase is in the recognized text
                    if target_phrase in _normalize_text(recognized_text):
                        return recognized_text


if __name__ == "__main__":
    activation_phrase = "hallo Assistant"
    speech_recognition = SpeechToText(recognizer_engine="recognize_whisper")
    print("Listening to activation phrase...")
    activation_phrase = speech_recognition.listen_to_phrase(activation_phrase)
    print("Activation phrase detected:", activation_phrase)
    print("Listening for command...")
    command = speech_recognition.listen()
    print("Command received:", command)
