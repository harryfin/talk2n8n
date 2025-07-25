from typing import Protocol

class SpeechToTextProtocol(Protocol):

    def listen(self, kwargs_listening: dict = None) -> str:
        pass

    def listen_to_phrase(self, phrases: str = None, kwargs_listening: dict = None) -> str:
        pass


class TextToSpeechProtocol(Protocol):
    def speak(self, _text: str):
        pass
