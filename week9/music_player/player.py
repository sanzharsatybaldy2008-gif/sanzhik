import os
import pygame


class MusicPlayer:
    def __init__(self, music_folder):
        self.music_folder = music_folder
        self.tracks = self.load_tracks()
        self.current_index = 0
        self.paused = False

    def load_tracks(self):
        tracks = []

        for file_name in os.listdir(self.music_folder):
            if file_name.endswith(".wav") or file_name.endswith(".mp3") or file_name.endswith(".ogg"):
                full_path = os.path.join(self.music_folder, file_name)
                tracks.append(full_path)

        tracks.sort()
        return tracks

    def play(self):
        if len(self.tracks) == 0:
            return

        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
        else:
            pygame.mixer.music.load(self.tracks[self.current_index])
            pygame.mixer.music.play()

    def pause(self):
        pygame.mixer.music.pause()
        self.paused = True

    def next_track(self):
        if len(self.tracks) == 0:
            return

        self.current_index = (self.current_index + 1) % len(self.tracks)
        pygame.mixer.music.load(self.tracks[self.current_index])
        pygame.mixer.music.play()
        self.paused = False

    def previous_track(self):
        if len(self.tracks) == 0:
            return

        self.current_index = (self.current_index - 1) % len(self.tracks)
        pygame.mixer.music.load(self.tracks[self.current_index])
        pygame.mixer.music.play()
        self.paused = False

    def current_track_name(self):
        if len(self.tracks) == 0:
            return "No tracks"

        return os.path.basename(self.tracks[self.current_index])

    def current_position(self):
        pos_ms = pygame.mixer.music.get_pos()

        if pos_ms < 0:
            pos_ms = 0

        total_seconds = pos_ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60

        return f"{minutes:02}:{seconds:02}"