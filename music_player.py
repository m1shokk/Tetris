import pygame
import os
from pygame import mixer

class MusicPlayer:
    def __init__(self):
        mixer.init()
        self.music_folder = "music"  # Папка с музыкой
        self.playlist = []
        self.current_track = 0
        self.is_muted = False
        self.normal_volume = 0.2  # Сохраняем нормальную громкость
        self.load_playlist()
        mixer.music.set_volume(self.normal_volume)
        
    def load_playlist(self):
        # Загружаем все .mp3 и .wav файлы из папки music и сортируем их
        if os.path.exists(self.music_folder):
            self.playlist = [
                os.path.join(self.music_folder, f) 
                for f in os.listdir(self.music_folder) 
                if f.endswith(('.mp3', '.wav'))
            ]
            # Сортируем плейлист, чтобы треки проигрывались по порядку
            self.playlist.sort()
    
    def play_next(self):
        if not self.playlist:
            return
        
        # Переходим к следующему треку
        self.current_track = (self.current_track + 1) % len(self.playlist)
        # Если достигли конца плейлиста, начинаем сначала
        if self.current_track == 0:
            self.start_playing()  # Начинаем с первого трека
        else:
            mixer.music.load(self.playlist[self.current_track])
            mixer.music.play()
    
    def start_playing(self):
        if not self.playlist:
            return
            
        # Всегда начинаем с первого трека (track1)
        self.current_track = 0
        mixer.music.load(self.playlist[self.current_track])
        mixer.music.play()
        # Установим обработчик окончания трека
        mixer.music.set_endevent(pygame.USEREVENT + 1)
    
    def toggle_mute(self):
        if self.is_muted:
            mixer.music.set_volume(self.normal_volume)  # Восстанавливаем громкость
            self.is_muted = False
        else:
            mixer.music.set_volume(0)  # Выключаем звук
            self.is_muted = True 