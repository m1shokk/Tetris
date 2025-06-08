import pygame
import random
import json
import os
from music_player import MusicPlayer

# Initialize Pygame
pygame.init()

# Constants
BLOCK_SIZE = 32
GRID_WIDTH = 10
GRID_HEIGHT = 20
PANEL_WIDTH = 220
SCREEN_WIDTH = BLOCK_SIZE * GRID_WIDTH + PANEL_WIDTH
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)  # New color for ghost piece
COLORS = [
    (0, 255, 255),  # I
    (255, 255, 0),  # O 
    (128, 0, 128),  # T
    (255, 127, 0),  # L
    (0, 0, 255),    # J
    (0, 255, 0),    # S
    (255, 0, 0)     # Z
]

# Tetris shapes
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
        pygame.display.set_caption('Tetris')
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
        # Rotate matrix 90 degrees
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
            self.score += (lines * 100) * lines  # More points for multiple lines at once
                
    def draw(self):
        # Gradient background
        for y in range(SCREEN_HEIGHT):
            color = (
                int(30 + 40 * y / SCREEN_HEIGHT),
                int(30 + 60 * y / SCREEN_HEIGHT),
                int(60 + 100 * y / SCREEN_HEIGHT)
            )
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))

        # Draw playfield background
        pygame.draw.rect(self.screen, (24, 24, 32), (0, 0, BLOCK_SIZE * GRID_WIDTH, SCREEN_HEIGHT))
        # Draw side panel background
        pygame.draw.rect(self.screen, (36, 36, 48), (BLOCK_SIZE * GRID_WIDTH, 0, PANEL_WIDTH, SCREEN_HEIGHT))

        # Draw grid (subtle)
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = [x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE]
                if self.grid[y][x]:
                    # Draw block with shadow
                    pygame.draw.rect(self.screen, (0,0,0), [rect[0]+2, rect[1]+2, BLOCK_SIZE-4, BLOCK_SIZE-4], border_radius=6)
                    pygame.draw.rect(self.screen, self.grid[y][x], [rect[0]+1, rect[1]+1, BLOCK_SIZE-2, BLOCK_SIZE-2], border_radius=6)
                # Subtle grid
                pygame.draw.rect(self.screen, (60, 60, 80, 60), rect, 1)

        # Draw ghost piece
        if self.current_piece:
            ghost_y = self.get_ghost_position()
            for i in range(len(self.current_piece['shape'])):
                for j in range(len(self.current_piece['shape'][0])):
                    if self.current_piece['shape'][i][j]:
                        pygame.draw.rect(
                            self.screen, (200, 200, 80),
                            [
                                (self.current_piece['x'] + j) * BLOCK_SIZE + 3,
                                (ghost_y + i) * BLOCK_SIZE + 3,
                                BLOCK_SIZE-6, BLOCK_SIZE-6
                            ], 2, border_radius=6)

        # Draw current piece
        if self.current_piece:
            for i in range(len(self.current_piece['shape'])):
                for j in range(len(self.current_piece['shape'][0])):
                    if self.current_piece['shape'][i][j]:
                        x = (self.current_piece['x'] + j) * BLOCK_SIZE
                        y = (self.current_piece['y'] + i) * BLOCK_SIZE
                        # Shadow
                        pygame.draw.rect(self.screen, (0,0,0), [x+2, y+2, BLOCK_SIZE-4, BLOCK_SIZE-4], border_radius=6)
                        # Block
                        pygame.draw.rect(self.screen, self.current_piece['color'], [x+1, y+1, BLOCK_SIZE-2, BLOCK_SIZE-2], border_radius=6)

        # Draw side panel (score, highscore, controls)
        panel_x = BLOCK_SIZE * GRID_WIDTH + 20
        font_title = pygame.font.SysFont('Arial', 36, bold=True)
        font = pygame.font.SysFont('Arial', 28)
        font_small = pygame.font.SysFont('Arial', 20)
        # Title
        title = font_title.render('TETRIS', True, (255,255,255))
        self.screen.blit(title, (panel_x, 30))
        # Author (smaller, light color)
        author = font_small.render('by Ch0kz Games', True, (180, 200, 255))
        self.screen.blit(author, (panel_x, 70))
        # Subtitle
        subtitle = font_small.render('Minimalist Edition', True, (200, 200, 220))
        self.screen.blit(subtitle, (panel_x, 100))
        # Score
        score_text = font.render(f'Score: {self.score}', True, (255,255,255))
        self.screen.blit(score_text, (panel_x, 140))
        # Highscore
        highscore_text = font.render(f'Highscore: {self.highscore}', True, (220,220,220))
        self.screen.blit(highscore_text, (panel_x, 180))
        # Controls
        controls_title = font_small.render('Controls:', True, (180,180,180))
        self.screen.blit(controls_title, (panel_x, 220))
        controls = [
            '←/A: Move Left',
            '→/D: Move Right',
            '↓/S: Move Down',
            '↑/W: Rotate',
            'Space: Hard Drop',
            'P: Mute/Unmute',
            'O: Next Track'
        ]
        for idx, ctrl in enumerate(controls):
            ctrl_text = font_small.render(ctrl, True, (200,200,200))
            self.screen.blit(ctrl_text, (panel_x, 250 + idx*28))

        # Game over overlay
        if self.game_over:
            overlay = pygame.Surface((BLOCK_SIZE*GRID_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,180))
            self.screen.blit(overlay, (0,0))
            font_over = pygame.font.SysFont('Arial', 48, bold=True)
            over_text = font_over.render('GAME OVER', True, (255, 80, 80))
            self.screen.blit(over_text, (BLOCK_SIZE*GRID_WIDTH//2 - over_text.get_width()//2, SCREEN_HEIGHT//2 - 80))
            font_restart = pygame.font.SysFont('Arial', 32)
            restart_text = font_restart.render('Press SPACE to restart', True, (255,255,255))
            self.screen.blit(restart_text, (BLOCK_SIZE*GRID_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 - 20))
            score_text = font.render(f'Score: {self.score}', True, (255,255,255))
            self.screen.blit(score_text, (BLOCK_SIZE*GRID_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 + 40))
            highscore_text = font.render(f'Highscore: {self.highscore}', True, (220,220,220))
            self.screen.blit(highscore_text, (BLOCK_SIZE*GRID_WIDTH//2 - highscore_text.get_width()//2, SCREEN_HEIGHT//2 + 80))

        pygame.display.flip()

game = Tetris()
fall_time = 0
fall_speed = 0.5  # Seconds

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
        elif event.type == pygame.USEREVENT + 1:  # Track ended event
            game.music_player.play_next()
        if event.type == pygame.KEYDOWN:
            if game.game_over:
                if event.key == pygame.K_SPACE:
                    game.reset_game()
            else:
                # Arrow key controls
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
                # Additional keys
                if event.key == pygame.K_p:  # Mute/unmute
                    game.music_player.toggle_mute()
                if event.key == pygame.K_o:  # Next track
                    game.music_player.play_next()
                    
    game.draw()

pygame.quit()
