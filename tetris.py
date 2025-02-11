import pygame
import random
import json
import os
from music_player import MusicPlayer

# Инициализация Pygame
pygame.init()

# Константы
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * GRID_WIDTH
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)  # Новый цвет для тени
COLORS = [
    (0, 255, 255),  # I
    (255, 255, 0),  # O 
    (128, 0, 128),  # T
    (255, 127, 0),  # L
    (0, 0, 255),    # J
    (0, 255, 0),    # S
    (255, 0, 0)     # Z
]

# Фигуры тетриса
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[0, 0, 1], [1, 1, 1]],  # L
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]]   # Z
]

class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Тетрис')
        self.clock = pygame.time.Clock()
        self.music_player = MusicPlayer()
        self.music_player.start_playing()
        self.reset_game()
        self.load_highscore()
        
    def reset_game(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        
    def load_highscore(self):
        try:
            with open('highscore.json', 'r') as f:
                self.highscore = json.load(f)
        except:
            self.highscore = 0
            
    def save_highscore(self):
        if self.score > self.highscore:
            self.highscore = self.score
            with open('highscore.json', 'w') as f:
                json.dump(self.highscore, f)
        
    def new_piece(self):
        shape = random.randint(0, len(SHAPES) - 1)
        return {
            'shape': SHAPES[shape],
            'color': COLORS[shape],
            'x': GRID_WIDTH // 2 - len(SHAPES[shape][0]) // 2,
            'y': 0
        }
        
    def rotate_piece(self, piece):
        # Поворот матрицы на 90 градусов
        shape = piece['shape']
        rotated = [[shape[j][i] for j in range(len(shape)-1, -1, -1)] for i in range(len(shape[0]))]
        return {'shape': rotated, 'color': piece['color'], 'x': piece['x'], 'y': piece['y']}
        
    def valid_move(self, piece, x, y):
        for i in range(len(piece['shape'])):
            for j in range(len(piece['shape'][0])):
                if piece['shape'][i][j]:
                    new_x = x + j
                    new_y = y + i
                    if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                        return False
                    if new_y >= 0 and self.grid[new_y][new_x]:
                        return False
        return True
        
    def get_ghost_position(self):
        ghost_y = self.current_piece['y']
        while self.valid_move(self.current_piece, self.current_piece['x'], ghost_y + 1):
            ghost_y += 1
        return ghost_y
        
    def hard_drop(self):
        while self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y'] + 1):
            self.current_piece['y'] += 1
        
    def add_to_grid(self):
        for i in range(len(self.current_piece['shape'])):
            for j in range(len(self.current_piece['shape'][0])):
                if self.current_piece['shape'][i][j]:
                    self.grid[self.current_piece['y'] + i][self.current_piece['x'] + j] = self.current_piece['color']
                    
    def remove_lines(self):
        lines = 0
        for i in range(GRID_HEIGHT):
            if all(self.grid[i]):
                del self.grid[i]
                self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
                lines += 1
        if lines > 0:
            self.score += (lines * 100) * lines  # Больше очков за несколько линий сразу
                
    def draw(self):
        self.screen.fill(BLACK)
        
        if self.game_over:
            font = pygame.font.Font(None, 48)
            score_text = font.render(f'Счёт: {self.score}', True, WHITE)
            highscore_text = font.render(f'Рекорд: {self.highscore}', True, WHITE)
            restart_text = font.render('Нажмите ПРОБЕЛ для рестарта', True, WHITE)
            
            self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 - 60))
            self.screen.blit(highscore_text, (SCREEN_WIDTH//2 - highscore_text.get_width()//2, SCREEN_HEIGHT//2))
            self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 60))
        else:
            # Отрисовка счёта
            font = pygame.font.Font(None, 36)
            score_text = font.render(f'Счёт: {self.score}', True, WHITE)
            self.screen.blit(score_text, (10, 10))
            
            # Отрисовка сетки
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    if self.grid[y][x]:
                        pygame.draw.rect(self.screen, self.grid[y][x],
                                       [x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE])
                    pygame.draw.rect(self.screen, WHITE,
                                   [x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE], 1)
            
            # Отрисовка тени (ghost piece)
            if self.current_piece:
                ghost_y = self.get_ghost_position()
                for i in range(len(self.current_piece['shape'])):
                    for j in range(len(self.current_piece['shape'][0])):
                        if self.current_piece['shape'][i][j]:
                            pygame.draw.rect(self.screen, YELLOW,
                                           [(self.current_piece['x'] + j) * BLOCK_SIZE,
                                            (ghost_y + i) * BLOCK_SIZE,
                                            BLOCK_SIZE, BLOCK_SIZE], 1)
                    
            # Отрисовка текущей фигуры
            if self.current_piece:
                for i in range(len(self.current_piece['shape'])):
                    for j in range(len(self.current_piece['shape'][0])):
                        if self.current_piece['shape'][i][j]:
                            pygame.draw.rect(self.screen, self.current_piece['color'],
                                           [(self.current_piece['x'] + j) * BLOCK_SIZE,
                                            (self.current_piece['y'] + i) * BLOCK_SIZE,
                                            BLOCK_SIZE, BLOCK_SIZE])
        
        pygame.display.flip()

game = Tetris()
fall_time = 0
fall_speed = 0.5  # Секунды

running = True
while running:
    fall_time += game.clock.get_rawtime()
    game.clock.tick()
    
    if not game.game_over:
        if fall_time/1000 >= fall_speed:
            if game.valid_move(game.current_piece, game.current_piece['x'], game.current_piece['y'] + 1):
                game.current_piece['y'] += 1
            else:
                game.add_to_grid()
                game.remove_lines()
                game.current_piece = game.new_piece()
                if not game.valid_move(game.current_piece, game.current_piece['x'], game.current_piece['y']):
                    game.game_over = True
                    game.save_highscore()
            fall_time = 0
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.USEREVENT + 1:  # Событие окончания трека
            game.music_player.play_next()
        if event.type == pygame.KEYDOWN:
            if game.game_over:
                if event.key == pygame.K_SPACE:
                    game.reset_game()
            else:
                # Управление стрелками
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    if game.valid_move(game.current_piece, game.current_piece['x'] - 1, game.current_piece['y']):
                        game.current_piece['x'] -= 1
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    if game.valid_move(game.current_piece, game.current_piece['x'] + 1, game.current_piece['y']):
                        game.current_piece['x'] += 1
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    if game.valid_move(game.current_piece, game.current_piece['x'], game.current_piece['y'] + 1):
                        game.current_piece['y'] += 1
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    rotated = game.rotate_piece(game.current_piece)
                    if game.valid_move(rotated, rotated['x'], rotated['y']):
                        game.current_piece = rotated
                if event.key == pygame.K_SPACE:
                    game.hard_drop()
                # Добавляем новые клавиши
                if event.key == pygame.K_p:  # Включение/выключение звука
                    game.music_player.toggle_mute()
                if event.key == pygame.K_o:  # Следующий трек
                    game.music_player.play_next()
                    
    game.draw()

pygame.quit()
