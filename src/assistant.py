import logging

import requests

from src.conversation import Conversation
from src.exception import ListeningTimeoutError
from src.protocol import TextToSpeechProtocol, SpeechToTextProtocol
from src.speech_to_text import SpeechToText
from src.text_to_speech import TextToSpeech
from src.utils import load_config

logger = logging.getLogger("assistant")


class AssistantBot:
    def __init__(
            self,
            text_to_speech_model: TextToSpeechProtocol,
            activation_stt_model: SpeechToTextProtocol,
            command_stt_model: SpeechToTextProtocol,
            activation_phrase: str,
            webhook_url: str,
            assistant_name: str = "Auxilia",
    ) -> None:
        self.tts = text_to_speech_model
        self.activation_stt = activation_stt_model
        self.command_stt = command_stt_model
        self.activation_phrase = activation_phrase
        self.webhook_url = webhook_url
        self.assistant_name = assistant_name

        self.time_to_continue_conversation = 5  # seconds, time to wait for user input after activation

        self.EXIT_COMMANDS = ["beenden", "exit", "tschüss", "assistent aus", "stop", f"{self.assistant_name} aus",
                              "schließen"]

    def speak(self, text: str) -> None:
        """Speak the provided text using the text-to-speech model."""
        self.tts.speak(text)

    def listen_for_activation(self) -> str:
        """Listen for the activation phrase and return True if detected."""
        kwargs_listening = {
            "timeout": None,
            "phrase_time_limit": 4,
        }
        return self.activation_stt.listen_to_phrase(self.activation_phrase, kwargs_listening)

    def listen_for_input(self) -> str:
        """Listen for user input after activation or during follow-up."""
        kwargs_listening = {
            "timeout": self.time_to_continue_conversation,  # wait for user input for a limited time
            "phrase_time_limit": 2,
        }  # wait for timout + phrase_time_limit seconds
        return self.command_stt.listen(kwargs_listening)

    def handle_interaction(self, command: str) -> str:
        """
        Route interactions by forwarding the input to n8n

        :param command: The command from the user.
        """
        logging.info(f"Received command for n8n: {command}, command type: {type(command)}")
        answer = self.send_text_to_n8n(command)

        if not answer:
            logging.warning("Keine Antwort von n8n erhalten.")
            answer = "Entschuldigung, ich habe keine Antwort erhalten. Bitte versuche es später erneut."
        return answer

    def send_text_to_n8n(self, text):
        try:
            response = requests.get(self.webhook_url, json={"text": text}, timeout=10)
            if response.status_code == 200:
                reply = response.text
                logging.info(f"Antwort von n8n erhalten: {reply}")
            else:
                logging.warning("Fehler bei der Anfrage an n8n: ")
                reply = ""
        except requests.RequestException as e:
            logging.error(f"Fehler bei der Kommunikation mit n8n: {e}")
            reply = ""
        return reply

    def is_exit_command(self, text: str) -> bool:
        return any(cmd in text.lower() for cmd in self.EXIT_COMMANDS)

    def run(self) -> None:
        """
        Main loop for the assistant bot, listening for activation and handling interactions
        with possible follow-ups.
        """
        self.speak(
            f"Hi, ich bin {self.assistant_name}. Ich bin dein persönlicher Assistent. "
            f"Sag einfach {self.activation_phrase} und stelle mir eine Frage."
        )
        while True:
            logger.info("Listening for activation phrase...")
            if initial_input := self.listen_for_activation():
                logger.info("Activation phrase detected. Handle input...")


                # Check if the initial input is an exit command
                if self.is_exit_command(initial_input):
                    logger.info("Exit command detected. Shutting down assistant.")
                    self.speak("Tschüss, bis bald!")
                    break  # Exit the assistant

                conv = Conversation()
                conv.add_user_message(initial_input)

                # Handle the initial input after activation
                try:
                    answer = self.handle_interaction(initial_input)
                    conv.add_assistant_response(answer)
                    self.speak(answer)
                except Exception as e:
                    logger.error(f"Error processing initial input: {e}")
                    self.speak(
                        "Entschuldigung, ich habe das nicht verstanden. Kannst du das bitte wiederholen?"
                    )

                logger.info("Listening for Follow-Up input...")
                while True:

                    # Wait for follow-up input after the initial interaction
                    try:
                        follow_up_input = self.listen_for_input()
                        logger.info(f"Follow_up input received: {follow_up_input}")
                        if not follow_up_input:
                            continue

                    except ListeningTimeoutError:
                        logger.info("no follow-up input detected, waiting for activation phrase again.")
                        break
                    except Exception as e:
                        logger.error(f"Error processing input: {e}")
                        self.speak(
                            "Entschuldigung, ich habe das nicht verstanden. Kannst du das bitte wiederholen?"
                        )
                        continue


                    # Check if the follow-up input is an exit command
                    if self.is_exit_command(follow_up_input):
                        logger.info("Exit command detected during follow-up. Shutting down assistant.")
                        self.speak("Tschüss, bis bald!")
                        return  # Exit the assistant


                    # Process the follow-up input
                    try:
                        conv.add_user_message(follow_up_input)
                        input_with_history = conv.get_conversation_history()
                        answer = self.handle_interaction(input_with_history)
                        self.speak(answer)

                    except Exception as e:
                        logger.error(f"Error processing follow-up input: {e}")
                        self.speak(
                            "Entschuldigung, ich habe das nicht verstanden. Kannst du das bitte wiederholen?"
                        )
                        continue
                    conv.add_assistant_response(answer)


if __name__ == "__main__":
    config = load_config("dev", "config.yaml")

    ACTIVATION_PHRASE = config.get("activation_phrase")
    WEBHOOK_URL = config.get("webhook_url")

    assistant = AssistantBot(
        text_to_speech_model=TextToSpeech(),
        activation_stt_model=SpeechToText(recognizer_engine="recognize_whisper"),
        command_stt_model=SpeechToText(recognizer_engine="recognize_google"),
        activation_phrase=ACTIVATION_PHRASE,
        webhook_url=WEBHOOK_URL,
    )
    assistant.run()
