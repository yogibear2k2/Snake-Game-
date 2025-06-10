import pygame
import sys
import random

pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Snake Game")
CLOCK = pygame.time.Clock()


icon = pygame.image.load('./images/image.png')  # Replace with your icon file path
pygame.display.set_icon(icon)

# Fonts
FONT = pygame.font.SysFont('Arial', 24)
BIG_FONT = pygame.font.SysFont('Arial', 36)

# --- Themes ---
themes = [
    {
        'bg': (20, 20, 20),
        'text': (255, 105, 180),  # Pink
        'button_bg': (200, 50, 150),
        'button_hover': (255, 105, 180),
        'neon': (255, 20, 147),
        'snow': (255, 255, 255)
    },
    {
        'bg': (20, 20, 20),
        'text': (50, 205, 50),    # Green
        'button_bg': (50, 205, 50),
        'button_hover': (0, 255, 0),
        'neon': (0, 255, 127),
        'snow': (255, 255, 255)
    },
    {
        'bg': (20, 20, 20),
        'text': (0, 191, 255),    # Blue
        'button_bg': (0, 191, 255),
        'button_hover': (0, 255, 255),
        'neon': (0, 255, 255),
        'snow': (255, 255, 255)
    },
    {
        'bg': (20, 20, 20),
        'text': (255, 255, 255),  # RGB
        'button_bg': (255, 0, 0),
        'button_hover': (0, 255, 0),
        'neon': (255, 0, 255),
        'snow': (255, 255, 255)
    }
]
current_theme_index = 0
current_theme = themes[current_theme_index]

# --- Snowflakes (like stars) ---
class Snow:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(-HEIGHT, 0)
        self.size = random.uniform(1, 3)
        self.speed = random.uniform(0.2, 0.7)
        self.angle = random.uniform(0, 2 * 3.14)
        self.angle_speed = random.uniform(-0.005, 0.005)

    def update(self, mouse_pos):
        mx, my = mouse_pos
        drift = (mx - self.x) / WIDTH * 0.2
        self.x += drift
        self.y += self.speed
        self.angle += self.angle_speed
        if self.y > HEIGHT or self.x < 0 or self.x > WIDTH:
            self.reset()
            self.y = -self.size

    def draw(self):
        pygame.draw.circle(SCREEN, current_theme['snow'], (int(self.x), int(self.y)), int(self.size))

SNOW_COUNT = 150
snowflakes = [Snow() for _ in range(SNOW_COUNT)]

# --- Button class ---
class Button:
    def __init__(self, rect, text, callback):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.hovered = False
        self.scale = 1.0
        self.target_scale = 1.0

    def draw(self):
        color = current_theme['button_hover'] if self.hovered else current_theme['button_bg']
        scaled_rect = self.rect.inflate(self.rect.width * (self.scale - 1), self.rect.height * (self.scale - 1))
        pygame.draw.rect(SCREEN, color, scaled_rect, border_radius=8)
        text_surf = FONT.render(self.text, True, current_theme['text'])
        text_rect = text_surf.get_rect(center=scaled_rect.center)
        SCREEN.blit(text_surf, text_rect)

    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.hovered = True
            self.target_scale = 1.1
        else:
            self.hovered = False
            self.target_scale = 1.0
        # Animate scale for hover effect
        self.scale += (self.target_scale - self.scale) * 0.1

    def check_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.callback()

# --- Game states ---
STATE_MAIN_MENU = 'main_menu'
STATE_SETTINGS = 'settings'
STATE_ABOUT = 'about'
STATE_SNAKE = 'snake_game'
state = STATE_MAIN_MENU

buttons = []

# --- Functions for menu ---
def next_theme():
    global current_theme_index, current_theme
    current_theme_index = (current_theme_index + 1) % len(themes)
    current_theme = themes[current_theme_index]

def show_about():
    global state
    state = 'about_window'

def close_about():
    global state
    state = STATE_MAIN_MENU

def create_main_menu():
    global buttons
    buttons.clear()
    # Create main menu buttons
    buttons.extend([
        Button((WIDTH//2 - 100, 200, 200, 50), 'Play', start_game),
        Button((WIDTH//2 - 100, 270, 200, 50), 'Settings', go_settings),
        Button((WIDTH//2 - 100, 340, 200, 50), 'Themes', next_theme),
        Button((10, HEIGHT - 60, 120, 40), 'About Dev', show_about)
    ])

def go_settings():
    global state
    state = STATE_SETTINGS

def start_game():
    global state
    init_game()
    state = STATE_SNAKE

# --- Settings menu ---
def draw_settings():
    rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 50, 300, 100)
    pygame.draw.rect(SCREEN, current_theme['button_bg'], rect, border_radius=10)
    text = FONT.render("Press T to change theme", True, current_theme['text'])
    SCREEN.blit(text, (rect.centerx - text.get_width()//2, rect.centery - text.get_height()//2))
    return rect

# --- Snake game ---
class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.body = [(WIDTH//2, HEIGHT//2)]
        self.dir = (0, -10)
        self.length = 1
        self.move_delay = 100  # ms
        self.last_move_time = pygame.time.get_ticks()
        self.speed = 10

    def change_dir(self, new_dir):
        # Prevent reversing
        if (new_dir[0] == -self.dir[0] and new_dir[1] == -self.dir[1]):
            return
        self.dir = new_dir

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_move_time > self.move_delay:
            head_x, head_y = self.body[0]
            new_head = (head_x + self.dir[0], head_y + self.dir[1])
            self.body.insert(0, new_head)
            if len(self.body) > self.length:
                self.body.pop()
            self.last_move_time = now

    def grow(self):
        self.length += 1

    def draw(self):
        for segment in self.body:
            pygame.draw.rect(SCREEN, current_theme['neon'], (*segment, 10, 10), border_radius=3)

    def check_collision(self):
        head = self.body[0]
        # Wall collision
        if not (0 <= head[0] <= WIDTH - 10 and 0 <= head[1] <= HEIGHT - 10):
            return True
        # Self collision
        if head in self.body[1:]:
            return True
        return False

class Food:
    def __init__(self):
        self.pos = self.random_pos()

    def random_pos(self):
        return (random.randint(0, (WIDTH - 10)//10)*10, random.randint(0, (HEIGHT - 10)//10)*10)

    def draw(self):
        pygame.draw.rect(SCREEN, current_theme['neon'], (*self.pos, 10, 10), border_radius=3)

def init_game():
    global snake, food
    snake = Snake()
    food = Food()

# --- Main loop ---
create_main_menu()

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            for btn in buttons:
                btn.check_click(mouse_pos)

        # Keyboard input
        if event.type == pygame.KEYDOWN:
            if state == STATE_SNAKE:
                if event.key == pygame.K_UP:
                    snake.change_dir((0, -10))
                elif event.key == pygame.K_DOWN:
                    snake.change_dir((0, 10))
                elif event.key == pygame.K_LEFT:
                    snake.change_dir((-10, 0))
                elif event.key == pygame.K_RIGHT:
                    snake.change_dir((10, 0))
            elif state == 'about_window':
                close_about()
            elif state == STATE_SETTINGS:
                if event.key == pygame.K_t:
                    next_theme()

    # Snow update
    for snow in snowflakes:
        snow.update(mouse_pos)

    # Draw background and snow
    SCREEN.fill(current_theme['bg'])
    for snow in snowflakes:
        snow.draw()

    # State-specific rendering
    if state == STATE_MAIN_MENU:
        title = BIG_FONT.render("Neon Snake", True, current_theme['text'])
        SCREEN.blit(title, (WIDTH//2 - title.get_width()//2, 120))
        for btn in buttons:
            btn.update(mouse_pos)
            btn.draw()

    elif state == STATE_SETTINGS:
        draw_settings()

    elif state == 'about_window':
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        SCREEN.blit(overlay, (0, 0))
        box_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 100, 400, 200)
        pygame.draw.rect(SCREEN, current_theme['button_bg'], box_rect, border_radius=10)
        lines = [
            "github.com/JunoDoes",
            "Made with <3 By JunoDoes",
            "Press any key to close"
        ]
        for i, line in enumerate(lines):
            text_surf = FONT.render(line, True, current_theme['text'])
            text_rect = text_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 50 + i*30))
            SCREEN.blit(text_surf, text_rect)

    elif state == STATE_SNAKE:
        snake.update()
        if snake.check_collision():
            init_game()
        if snake.body[0] == food.pos:
            snake.grow()
            food.pos = food.random_pos()
        snake.draw()
        food.draw()

    # About Dev button (bottom left)
    about_button = pygame.Rect(10, HEIGHT - 60, 120, 40)
    pygame.draw.rect(SCREEN, current_theme['button_bg'], about_button, border_radius=8)
    about_text = FONT.render("About Dev", True, current_theme['text'])
    SCREEN.blit(about_text, about_text.get_rect(center=about_button.center))
    if pygame.mouse.get_pressed()[0]:
        if about_button.collidepoint(mouse_pos):
            show_about()

    pygame.display.flip()
    CLOCK.tick(60)


        # Update the GUI game
    pygame.display.update()

pygame.quit()
sys.exit()
