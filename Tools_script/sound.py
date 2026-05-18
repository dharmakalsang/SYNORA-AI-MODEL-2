"""Sound playback helper with queue support."""

import os
import queue
import threading

try:
    import pygame
except ImportError:
    pygame = None


def ensure_pygame():
    if pygame is None:
        raise RuntimeError("pygame is required. Install with: pip install pygame")
    if not pygame.mixer.get_init():
        pygame.mixer.init()


class SoundPlayer:
    def __init__(self):
        ensure_pygame()
        self.sound_queue = queue.Queue()
        self.thread = threading.Thread(target=self._process_queue, daemon=True)
        self.running = True
        self.thread.start()

    def _process_queue(self):
        while self.running:
            try:
                path = self.sound_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            if path is None:
                break
            try:
                self._play_now(path)
            except Exception as exc:
                print(f"Sound playback error: {exc}")
            self.sound_queue.task_done()
        self.running = False

    def _play_now(self, path: str) -> None:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Sound file not found: {path}")
        sound = pygame.mixer.Sound(path)
        sound.play()
        while pygame.mixer.get_busy():
            pygame.time.wait(100)

    def enqueue_sound(self, path: str) -> None:
        self.sound_queue.put(path)

    def stop(self) -> None:
        self.running = False
        self.sound_queue.put(None)
        self.thread.join(timeout=2)
        if pygame is not None:
            pygame.mixer.quit()


def init_sound_player() -> SoundPlayer:
    return SoundPlayer()


def play_sound_file(path: str) -> None:
    player = init_sound_player()
    player.enqueue_sound(path)
    player.sound_queue.join()
    player.stop()


if __name__ == '__main__':
    player = init_sound_player()
    filenames = [f for f in ["sound1.wav", "sound2.wav", "sound.mp3"] if os.path.exists(f)]
    if not filenames:
        print("No sound files found in the current folder. Put sound1.wav or sound2.wav here.")
    for filename in filenames:
        print(f"Queueing {filename}")
        player.enqueue_sound(filename)
    player.sound_queue.join()
    player.stop()
