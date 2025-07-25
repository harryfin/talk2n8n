import fire

from src.assistant import AssistantBot
from src.speech_to_text import SpeechToText
from src.text_to_speech import TextToSpeech
from src.utils import load_config, setup_logging


def main(app_env: str = "dev") -> None:
    config = load_config(app_env, "config.yaml")
    setup_logging(config.get("log_level", "INFO"), logfile=config.get("logfile", "log.txt"))

    webhook_url = config.get("webhook_url", None)
    activation_phrase = config.get("activation_phrase", "Hallo Assistant")
    assistant_name = config.get("assistant_name", "Auxilia")

    if not webhook_url:
        raise ValueError("Webhook URL must be provided in the config file.")

    assistant = AssistantBot(
        text_to_speech_model=TextToSpeech(),
        activation_stt_model=SpeechToText(recognizer_engine="recognize_whisper"),
        command_stt_model=SpeechToText(recognizer_engine="recognize_google"),
        activation_phrase=activation_phrase,
        webhook_url=webhook_url,
        assistant_name=assistant_name,
    )
    assistant.run()


if __name__ == '__main__':
    fire.Fire(main)
