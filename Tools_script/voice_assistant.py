"""Voice assistant with wake-word detection and audio playback."""

import os

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

from Tools_script.sound import play_sound_file
import Tools_script.synora_comm as synora_comm


WAKE_AUDIO_FILE = "Audio wake up log.ogg"
SYNORA_AI_MODEL = "gemma4"
WAKE_WORDS = ["synora", "hey synora", "jarvis", "hey jarvis", "wake up"]


class VoiceAssistant:
    def __init__(self, wake_audio: str = WAKE_AUDIO_FILE):
        self.wake_audio = wake_audio
        self.recognizer = sr.Recognizer() if sr else None
        self.engine = pyttsx3.init() if pyttsx3 else None
        self.running = False
        self.listening = False

    def play_wake_sound(self) -> None:
        """Play the wake-up audio file."""
        if os.path.exists(self.wake_audio):
            print(f"Playing wake sound: {self.wake_audio}")
            try:
                play_sound_file(self.wake_audio)
            except Exception as exc:
                print(f"Error playing wake sound: {exc}")
        else:
            print(f"Wake audio file not found: {self.wake_audio}")

    def speak(self, text: str) -> None:
        """Text-to-speech response."""
        if self.engine is None:
            print(f"[Synora]: {text}")
            return
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as exc:
            print(f"Speech error: {exc}")

    def _listen(self, timeout: int = 10, phrase_time_limit: int = 7) -> str:
        """Listen from the microphone and return recognized text."""
        if self.recognizer is None:
            print("speech_recognition not installed. Use text input instead.")
            return input("Enter command: ")

        try:
            with sr.Microphone() as source:
                print(f"Listening... (timeout: {timeout}s)")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

            print("Processing audio...")
            text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Could not understand audio.")
            return ""
        except sr.RequestError as exc:
            print(f"API error: {exc}")
            return ""
        except Exception as exc:
            print(f"Listening error: {exc}")
            return ""

    def listen_for_wake_word(self, timeout: int = 10) -> bool:
        """Listen for a wake word from the microphone."""
        text = self._listen(timeout=timeout, phrase_time_limit=5)
        if not text:
            return False
        lowered = text.lower()
        return any(word in lowered for word in WAKE_WORDS)

    def run_wake_mode(self) -> None:
        """Continuously wait for the wake word and then process a command."""
        if self.recognizer is None:
            print("speech_recognition not installed. Voice mode unavailable.")
            return

        print("\n--- Wake Word Mode ---")
        print("Say the wake word (for example: 'Hey Synora' or 'Hey Jarvis') to start.")
        print("Say 'quit' at any time to exit wake mode.\n")

        while True:
            try:
                if self.listen_for_wake_word(timeout=10):
                    print("Wake word detected.")
                    self.play_wake_sound()
                    command = self._listen(timeout=8, phrase_time_limit=10)
                    if command:
                        if command.lower().strip() in ("quit", "exit"):
                            print("Exiting wake mode.")
                            break
                        self.process_command(command)
                else:
                    print("Waiting for wake word...")
            except KeyboardInterrupt:
                print("\nExiting wake mode...")
                break
            except Exception as exc:
                print(f"Wake mode error: {exc}")
                break

    def run_interactive(self) -> None:
        """Run the voice assistant interactively."""
        print("\n--- Voice Assistant Active ---")
        print("Type 'quit' to exit, 'help' for commands\n")

        while True:
            try:
                choice = input("(W)ake / (V)oice / (T)ext / (Q)uit: ").strip().lower()

                if choice in ("q", "quit"):
                    print("Exiting voice assistant.")
                    break

                if choice in ("w", "wake"):
                    self.run_wake_mode()

                elif choice in ("v", "voice"):
                    self.play_wake_sound()
                    command = self._listen(timeout=8, phrase_time_limit=10)
                    if command:
                        self.process_command(command)

                elif choice in ("t", "text"):
                    command = input("Enter command: ").strip()
                    if command:
                        self.process_command(command)

                elif choice in ("h", "help"):
                    self.show_help()
                else:
                    print("Invalid choice. Type 'help' for options.")

            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as exc:
                print(f"Error: {exc}")

    def process_command(self, command: str) -> None:
        """Process a voice or text command."""
        print(f"\nProcessing: {command}")

        synora_comm.handle_synora_request(command)

        response = f"Completed: {command}"
        self.speak(response)

    def show_help(self) -> None:
        """Show help menu."""
        print("\n--- Commands ---")
        print("(W)ake   - Wait for wake word and then listen")
        print("(V)oice  - Play wake sound and listen once")
        print("(T)ext   - Enter text command")
        print("(Q)uit   - Exit assistant")
        print("(H)elp   - Show this menu")
        print("\nExample commands:")
        print("  'open google.com'")
        print("  'tell alice to say hello to bob'")
        print("  'what is the weather'")
        print()


def main() -> None:
    """Main entry point for voice assistant."""
    print("Synora Voice Assistant")
    print(f"Wake audio: {WAKE_AUDIO_FILE}")

    if not os.path.exists(WAKE_AUDIO_FILE):
        print(f"Warning: {WAKE_AUDIO_FILE} not found in current folder.")

    if sr is None:
        print("Warning: speech-recognition not installed. Voice input disabled.")
        print("Install with: pip install SpeechRecognition")

    if pyttsx3 is None:
        print("Warning: pyttsx3 not installed. Text-to-speech disabled.")
        print("Install with: pip install pyttsx3")

    assistant = VoiceAssistant(wake_audio=WAKE_AUDIO_FILE)
    assistant.run_interactive()


if __name__ == "__main__":
    main()
