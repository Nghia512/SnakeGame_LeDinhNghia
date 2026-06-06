import pygame
import random
import cv2
import numpy as np
import sys
import math

# Khởi tạo Pygame
pygame.init()

# I. CẤU HÌNH VÀ MÀU SẮC MẶC ĐỊNH
WIDTH, HEIGHT = 640, 480  
GRID_SIZE = 20
HUD_TOP_HEIGHT = 40  

# Chủ đề Màu nền
BG_THEMES = [
    {"bg": (10, 11, 18), "grid": (22, 25, 38)},       # Mặc định (Tối)
    {"bg": (15, 25, 15), "grid": (25, 40, 25)},       # Xanh rêu
    {"bg": (25, 10, 10), "grid": (45, 15, 15)},       # Đỏ sẫm
    {"bg": (20, 20, 25), "grid": (35, 35, 45)}        # Xám xanh
]

# Chủ đề Màu rắn (Đầu, Viền, Thân g_val, Thân b_val)
SNAKE_THEMES = [
    {"head": (0, 255, 204), "border": (0, 150, 120), "g": 130, "b": 190}, # Cyan (Mặc định)
    {"head": (255, 50, 50), "border": (150, 0, 0), "g": 50, "b": 50},     # Đỏ
    {"head": (50, 255, 50), "border": (0, 150, 0), "g": 200, "b": 50},    # Xanh lá
    {"head": (204, 50, 255), "border": (120, 0, 150), "g": 50, "b": 200}  # Tím
]

COLOR_FOOD = (255, 0, 127)           
COLOR_SUPER_FOOD = (255, 211, 42)    
COLOR_TEXT = (240, 244, 255)       
COLOR_SUBTEXT = (90, 105, 120)       
COLOR_MENU_BTN = (44, 62, 80)        
COLOR_HUD_BORDER = (0, 255, 204)    

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SNAKE GAME - EXTENDED")
clock = pygame.time.Clock()

font_title = pygame.font.SysFont("Segoe UI", 46, bold=True)
font_normal = pygame.font.SysFont("Segoe UI", 15, bold=False) 
font_bold = pygame.font.SysFont("Segoe UI", 15, bold=True)
font_small = pygame.font.SysFont("Segoe UI", 12, bold=False)  

# Cài đặt Game
settings = {
    "brightness": 1.0,
    "bg_idx": 0,
    "snake_idx": 0,
    "level": 0
}

# II. ĐỊA HÌNH VÀ CẤP ĐỘ (LEVELS)
def generate_obstacles(level_idx):
    obs = []
    grid_x_max = WIDTH // GRID_SIZE
    grid_y_max = HEIGHT // GRID_SIZE
    grid_y_start = HUD_TOP_HEIGHT // GRID_SIZE

    if level_idx == 0: # Màn 0: Không địa hình
        pass
    elif level_idx == 1: # Màn 1: Viền hộp
        for x in range(2, grid_x_max - 2):
            obs.append([x * GRID_SIZE, (grid_y_start + 2) * GRID_SIZE])
            obs.append([x * GRID_SIZE, (grid_y_max - 3) * GRID_SIZE])
    elif level_idx == 2: # Màn 2: Đường hầm dọc
        for y in range(grid_y_start + 4, grid_y_max - 4):
            obs.append([10 * GRID_SIZE, y * GRID_SIZE])
            obs.append([(grid_x_max - 11) * GRID_SIZE, y * GRID_SIZE]) # Đã fix lỗi dấu ngoặc
    elif level_idx == 3: # Màn 3: Dấu thập tâm
        cx, cy = grid_x_max // 2, (grid_y_start + grid_y_max) // 2
        for i in range(-5, 6):
            obs.append([(cx + i) * GRID_SIZE, cy * GRID_SIZE])
            if i != 0: obs.append([cx * GRID_SIZE, (cy + i) * GRID_SIZE])
    elif level_idx == 4: # Màn 4: Ma trận rải rác
        for x in range(4, grid_x_max - 3, 6):
            for y in range(grid_y_start + 4, grid_y_max - 3, 5):
                obs.append([x * GRID_SIZE, y * GRID_SIZE])
    elif level_idx == 5:  # Màn 5: FULL BORDER
        for x in range(0, grid_x_max):
          # cạnh trên
          obs.append([x * GRID_SIZE, grid_y_start * GRID_SIZE])
          # cạnh dưới
          obs.append([x * GRID_SIZE, (grid_y_max - 1) * GRID_SIZE])
        for y in range(grid_y_start + 1, grid_y_max - 1):
          # cạnh trái
          obs.append([0, y * GRID_SIZE])
          # cạnh phải
          obs.append([(grid_x_max - 1) * GRID_SIZE, y * GRID_SIZE])
            
    return [pos for pos in obs if pos[0] >= 0 and pos[0] < WIDTH and pos[1] >= HUD_TOP_HEIGHT and pos[1] < HEIGHT]

LEVEL_NAMES = ["0: EMPTY FIELD", "1: HORIZONTAL BARS", "2: TUNNELS", "3: THE CROSS", "4: SCATTERED DOTS", "5: THE CAGE"]


# III. LỚP ĐỐI TƯỢNG GAME

class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.body = [[160, 240], [140, 240], [120, 240]]
        self.direction = "RIGHT"
        self.grow_counter = 0  
        self.chroma_tick = 0   

    def move(self):
        head = list(self.body[0])
        if self.direction == "UP": head[1] -= GRID_SIZE
        elif self.direction == "DOWN": head[1] += GRID_SIZE
        elif self.direction == "LEFT": head[0] -= GRID_SIZE
        elif self.direction == "RIGHT": head[0] += GRID_SIZE

        head[0] = head[0] % WIDTH
        if head[1] < HUD_TOP_HEIGHT: head[1] = HEIGHT - GRID_SIZE
        elif head[1] >= HEIGHT: head[1] = HUD_TOP_HEIGHT

        self.body.insert(0, head)
        if self.grow_counter > 0: self.grow_counter -= 1
        else: self.body.pop()
            
        self.chroma_tick = (self.chroma_tick + 4) % 360

    def change_direction(self, new_dir):
        opposites = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
        if new_dir != opposites.get(self.direction):
            self.direction = new_dir

    def check_collision(self, obstacles):
        head = self.body[0]
        if head in self.body[1:]: return True
        if head in obstacles: return True
        return False

    def draw(self, surface):
        num_segments = len(self.body)
        theme = SNAKE_THEMES[settings["snake_idx"]]

        # Quầng sáng
        for i, segment in enumerate(self.body):
            size_factor = 1.0 - (i / num_segments) * 0.5
            glow = int(max(2, (GRID_SIZE // 2) * size_factor))
            pygame.draw.circle(surface, (10, 26, 36), (segment[0] + GRID_SIZE // 2, segment[1] + GRID_SIZE // 2), glow + 1)

        # Thân rắn
        for i in range(1, num_segments):
            segment = self.body[i]
            wave_calc = math.sin(math.radians(self.chroma_tick + (i * 12)))
            
            # Đổi màu thân theo Theme
            if settings["snake_idx"] == 0:
                g_val = int(130 + 80 * wave_calc); b_val = int(190 + 65 * wave_calc); r_val = 0
            else:
                r_val = int(theme["head"][0] * 0.6 + 50 * wave_calc) if theme["head"][0] > 0 else 0
                g_val = int(theme["head"][1] * 0.6 + 50 * wave_calc) if theme["head"][1] > 0 else 0
                b_val = int(theme["head"][2] * 0.6 + 50 * wave_calc) if theme["head"][2] > 0 else 0

            ratio = 1.0 - (i / num_segments) * 0.4
            body_color = (
               max(0, min(255, int(r_val * ratio))),
               max(0, min(255, int(g_val * ratio))),
               max(0, min(255, int(b_val * ratio)))
            )
            
            taper_factor = 1.0 - (i / num_segments) * 0.45
            size = int((GRID_SIZE + 2) * taper_factor)
            size = max(6, size)
            
            offset = (GRID_SIZE - size) // 2
            rx, ry = segment[0] + offset, segment[1] + offset
            br = max(2, size // 4)
            pygame.draw.rect(surface, body_color, pygame.Rect(rx, ry, size, size), border_radius=br)

        # Đầu rắn
        hx, hy = self.body[0][0], self.body[0][1]
        pygame.draw.rect(surface, theme["border"], pygame.Rect(hx - 1, hy - 1, GRID_SIZE + 2, GRID_SIZE + 2), border_radius=8)
        pygame.draw.rect(surface, theme["head"], pygame.Rect(hx, hy, GRID_SIZE, GRID_SIZE), border_radius=6)
        
        visor_color = (255, 255, 255) if math.sin(math.radians(self.chroma_tick * 2)) > 0.85 else (15, 20, 30)
        if self.direction in ["RIGHT", "LEFT"]:
            ox = 12 if self.direction == "RIGHT" else 4
            pygame.draw.rect(surface, visor_color, pygame.Rect(hx + ox, hy + 4, 4, 5), border_radius=2)
            pygame.draw.rect(surface, visor_color, pygame.Rect(hx + ox, hy + 11, 4, 5), border_radius=2)
        elif self.direction in ["UP", "DOWN"]:
            oy = 4 if self.direction == "UP" else 12
            pygame.draw.rect(surface, visor_color, pygame.Rect(hx + 4, hy + oy, 5, 4), border_radius=2)
            pygame.draw.rect(surface, visor_color, pygame.Rect(hx + 11, hy + oy, 5, 4), border_radius=2)

class Food:
    def __init__(self):
        self.position = [0, 0]
        self.is_super = False 
        self.pulse_tick = 0

    def randomize_position(self, obstacles, snake_body):
        grid_x_max = (WIDTH - GRID_SIZE) // GRID_SIZE
        grid_y_start = HUD_TOP_HEIGHT // GRID_SIZE
        grid_y_max = (HEIGHT - GRID_SIZE) // GRID_SIZE
        
        for _ in range(1000):
            pos = [
                random.randint(0, grid_x_max) * GRID_SIZE,
                random.randint(grid_y_start, grid_y_max) * GRID_SIZE
            ]
            if pos not in obstacles and pos not in snake_body:
                self.position = pos
                self.is_super = random.random() < 0.15
                return True
        return False
        self.is_super = random.random() < 0.15

    def draw(self, surface):
        self.pulse_tick = (self.pulse_tick + 6) % 360
        fx, fy = self.position[0] + GRID_SIZE // 2, self.position[1] + GRID_SIZE // 2
        pulse = math.sin(math.radians(self.pulse_tick)) * 2.0

        if self.is_super:
            pygame.draw.circle(
                surface,
                (160, 125, 30),
                (fx, fy),
                int(GRID_SIZE // 2 + 2 + pulse)
            ) 
            pygame.draw.circle(
                surface,
                COLOR_SUPER_FOOD,
                (fx, fy),
                int(GRID_SIZE // 2 - 1 + pulse)
            )
        else:
            pygame.draw.circle(
                surface,
                COLOR_FOOD,
                (fx, fy),
                int(GRID_SIZE // 2 - 1 + pulse)
            )
            pygame.draw.circle(surface, (255, 255, 255), (fx - 2, fy - 2), 1.5)

class ImageProcessor:
    @staticmethod
    def process_and_detect(surface):
        view = pygame.surfarray.array3d(surface)
        view = view.transpose([1, 0, 2])
        img_bgr = cv2.cvtColor(view, cv2.COLOR_RGB2BGR)
        img_blur = cv2.GaussianBlur(img_bgr, (5, 5), 0)
        img_hsv = cv2.cvtColor(img_blur, cv2.COLOR_BGR2HSV)
        mask_green = cv2.inRange(img_hsv, np.array([75, 100, 100]), np.array([95, 255, 255]))
        contours, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return len(contours) > 0
    @staticmethod
    def detect_wall(surface):
        frame = pygame.surfarray.array3d(surface)
        frame = np.transpose(frame, (1, 0, 2))
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        return np.sum(edges) > 1000

# IV. HÀM VẼ GIAO DIỆN VÀ HỆ THỐNG
def draw_matrix_background(surface):
    bg_color = BG_THEMES[settings["bg_idx"]]["bg"]
    grid_color = BG_THEMES[settings["bg_idx"]]["grid"]
    surface.fill(bg_color)
    for x in range(0, WIDTH + 1, GRID_SIZE):
        pygame.draw.line(surface, grid_color, (x, HUD_TOP_HEIGHT), (x, HEIGHT), 1)
    for y in range(HUD_TOP_HEIGHT, HEIGHT + 1, GRID_SIZE):
        pygame.draw.line(surface, grid_color, (0, y), (WIDTH, y), 1)

def draw_obstacles(surface, obstacles):
    for obs in obstacles:
        pygame.draw.rect(surface, (80, 90, 100), pygame.Rect(obs[0], obs[1], GRID_SIZE, GRID_SIZE), border_radius=3)
        pygame.draw.rect(surface, (50, 60, 70), pygame.Rect(obs[0]+4, obs[1]+4, GRID_SIZE-8, GRID_SIZE-8))

def draw_top_hud_bar(surface, score, high_score, fps, ai_detected):
    pygame.draw.rect(surface, (14, 16, 26), pygame.Rect(0, 0, WIDTH, HUD_TOP_HEIGHT))
    pygame.draw.line(surface, COLOR_HUD_BORDER, (0, HUD_TOP_HEIGHT - 1), (WIDTH, HUD_TOP_HEIGHT - 1), 2)

    surface.blit(font_bold.render(f"SCORE: {score}", True, COLOR_TEXT), (20, 3))
    surface.blit(font_normal.render(f"SPEED: {fps:.1f}", True, COLOR_HUD_BORDER), (WIDTH // 2 - 40, 3))
    surface.blit(font_normal.render(f"HIGH SCORE: {high_score}", True, COLOR_SUBTEXT), (WIDTH - 180, 3))
    status = "DETECTED" if ai_detected else "NONE"
    surface.blit(
        font_small.render(
            f"AI: {status}",
            True,
            COLOR_SUPER_FOOD if ai_detected else COLOR_SUBTEXT
        ),
        (20, 22)
    )
    surface.blit(
        font_small.render(
            "CONTROLS: [Arrows] Move | [P] Pause | [R] Retry | [ESC] Menu",
            True,
            COLOR_SUBTEXT
        ),
        (WIDTH // 2 - 130, 22)
    )
def draw_button(surface, text, x, y, w, h, mouse_pos):
    rect = pygame.Rect(x, y, w, h)
    is_hover = rect.collidepoint(mouse_pos)
    color = COLOR_HUD_BORDER if is_hover else COLOR_MENU_BTN
    txt_color = (10, 10, 10) if is_hover else COLOR_TEXT
    pygame.draw.rect(surface, color, rect, border_radius=6)
    
    txt_surf = font_bold.render(text, True, txt_color)
    surface.blit(txt_surf, (x + w//2 - txt_surf.get_width()//2, y + h//2 - txt_surf.get_height()//2))
    return rect, is_hover

def apply_brightness(surface):
    b = settings["brightness"]
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    if b < 1.0:
        overlay.fill((0, 0, 0, int((1.0 - b) * 255)))
    elif b > 1.0:
        overlay.fill((255, 255, 255, int((b - 1.0) * 100)))
    surface.blit(overlay, (0, 0))

# V. VÒNG LẶP CHÍNH
def main():
    snake = Snake()
    food = Food()
    score, high_score = 0, 0
    BASE_FPS = 8.0
    current_fps = BASE_FPS
    game_state = "MENU" 
    
    obstacles = generate_obstacles(settings["level"])
    food.randomize_position(obstacles, snake.body)

    running = True
    frame_count = 0
    ai_detected = False
    while running:
        frame_count += 1
        mouse_pos = pygame.mouse.get_pos()
        clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: game_state = "MENU"
                elif game_state == "PLAYING":
                    if event.key == pygame.K_UP: snake.change_direction("UP")
                    elif event.key == pygame.K_DOWN: snake.change_direction("DOWN")
                    elif event.key == pygame.K_LEFT: snake.change_direction("LEFT")
                    elif event.key == pygame.K_RIGHT: snake.change_direction("RIGHT")
                    elif event.key == pygame.K_p: game_state = "PAUSED"
                elif game_state == "PAUSED" and event.key == pygame.K_p:
                    game_state = "PLAYING"
                elif game_state == "GAME OVER" and event.key == pygame.K_r:
                    snake.reset()
                    obstacles = generate_obstacles(settings["level"])
                    food.randomize_position(obstacles, snake.body)
                    score = 0
                    game_state = "PLAYING"

        draw_matrix_background(screen)

        # MÀN HÌNH CHÍNH (MENU)
        if game_state == "MENU":
            title = font_title.render("SNAKE GAME", True, SNAKE_THEMES[settings["snake_idx"]]["head"])
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))

            btn_play, _ = draw_button(screen, "PLAY GAME", WIDTH//2 - 100, 180, 200, 45, mouse_pos)
            btn_lvl, _ = draw_button(screen, "LEVELS", WIDTH//2 - 100, 240, 200, 45, mouse_pos)
            btn_opt, _ = draw_button(screen, "OPTIONS", WIDTH//2 - 100, 300, 200, 45, mouse_pos)
            btn_quit, _ = draw_button(screen, "QUIT GAME", WIDTH//2 - 100, 360, 200, 45, mouse_pos)
            
            if clicked:
                if btn_play.collidepoint(mouse_pos):
                    snake.reset()
                    obstacles = generate_obstacles(settings["level"])
                    food.randomize_position(obstacles, snake.body)
                    score = 0
                    current_fps = BASE_FPS
                    game_state = "PLAYING"
                elif btn_lvl.collidepoint(mouse_pos): game_state = "LEVELS"
                elif btn_opt.collidepoint(mouse_pos): game_state = "OPTIONS"
                elif btn_quit.collidepoint(mouse_pos): running = False

        # MÀN HÌNH CHỌN MÀN CHƠI (LEVELS)
        elif game_state == "LEVELS":
            title = font_title.render("SELECT DIFFICULTY", True, COLOR_SUPER_FOOD)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 40))
            
            btn_prev, _ = draw_button(screen, "<", WIDTH//2 - 150, 120, 40, 40, mouse_pos)
            lvl_text = font_bold.render(LEVEL_NAMES[settings["level"]], True, COLOR_TEXT)
            screen.blit(lvl_text, (WIDTH//2 - lvl_text.get_width()//2, 130))
            btn_next, _ = draw_button(screen, ">", WIDTH//2 + 110, 120, 40, 40, mouse_pos)
            
            # Vẽ Mini-map xem trước địa hình
            map_rect = pygame.Rect(WIDTH//2 - 120, 180, 240, 180)
            pygame.draw.rect(screen, BG_THEMES[settings["bg_idx"]]["bg"], map_rect)
            pygame.draw.rect(screen, COLOR_HUD_BORDER, map_rect, 2)
            
            preview_obs = generate_obstacles(settings["level"])
            for obs in preview_obs:
                px = map_rect.x + (obs[0] * 240 // WIDTH)
                py = map_rect.y + ((obs[1] - HUD_TOP_HEIGHT) * 180 // (HEIGHT - HUD_TOP_HEIGHT))
                pw, ph = max(2, 240 // (WIDTH//GRID_SIZE)), max(2, 180 // ((HEIGHT-HUD_TOP_HEIGHT)//GRID_SIZE))
                pygame.draw.rect(screen, (150, 150, 160), (px, py, pw, ph))

            btn_back, _ = draw_button(screen, "BACK", WIDTH//2 - 100, 390, 200, 45, mouse_pos)

            if clicked:
                if btn_prev.collidepoint(mouse_pos): settings["level"] = (settings["level"] - 1) % 6
                elif btn_next.collidepoint(mouse_pos): settings["level"] = (settings["level"] + 1) % 6
                elif btn_back.collidepoint(mouse_pos): game_state = "MENU"

        # MÀN HÌNH TÙY CHỌN (OPTIONS)
        elif game_state == "OPTIONS":
            title = font_title.render("OPTIONS", True, COLOR_HUD_BORDER)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 60))

            btn_b_down, _ = draw_button(screen, "-", 150, 160, 40, 40, mouse_pos)
            screen.blit(font_bold.render(f"BRIGHTNESS: {int(settings['brightness']*100)}%", True, COLOR_TEXT), (210, 170))
            btn_b_up, _ = draw_button(screen, "+", 450, 160, 40, 40, mouse_pos)

            btn_s_color, _ = draw_button(screen, f"SNAKE COLOR: {settings['snake_idx']+1}", WIDTH//2 - 120, 220, 240, 40, mouse_pos)
            btn_bg_color, _ = draw_button(screen, f"BACKGROUND: {settings['bg_idx']+1}", WIDTH//2 - 120, 280, 240, 40, mouse_pos)
            btn_back, _ = draw_button(screen, "BACK", WIDTH//2 - 100, 360, 200, 45, mouse_pos)

            if clicked:
                if btn_b_down.collidepoint(mouse_pos): settings["brightness"] = max(0.5, settings["brightness"] - 0.1)
                elif btn_b_up.collidepoint(mouse_pos): settings["brightness"] = min(1.5, settings["brightness"] + 0.1)
                elif btn_s_color.collidepoint(mouse_pos): settings["snake_idx"] = (settings["snake_idx"] + 1) % len(SNAKE_THEMES)
                elif btn_bg_color.collidepoint(mouse_pos): settings["bg_idx"] = (settings["bg_idx"] + 1) % len(BG_THEMES)
                elif btn_back.collidepoint(mouse_pos): game_state = "MENU"

        # CHƠI GAME
        elif game_state == "PLAYING":
            snake.move()
            if snake.body[0] == food.position:
                if food.is_super:
                    snake.grow_counter += 3; score += 3
                else:
                    snake.grow_counter += 1; score += 1
                food.randomize_position(obstacles, snake.body)

            if snake.check_collision(obstacles):
                if score > high_score: high_score = score
                game_state = "GAME OVER"

            draw_obstacles(screen, obstacles)
            food.draw(screen)
            snake.draw(screen)
            if frame_count % 20 == 0:
                ai_detected = ImageProcessor.process_and_detect(screen)
            current_fps = min(
               BASE_FPS + score * 0.15,
               18
            )
            draw_top_hud_bar(screen, score, high_score, current_fps, ai_detected)

        # TẠM DỪNG (PAUSED)
        elif game_state == "PAUSED":
            draw_obstacles(screen, obstacles)
            food.draw(screen)
            snake.draw(screen)
            draw_top_hud_bar(screen, score, high_score, current_fps, ai_detected)
            
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 11, 18, 190)) 
            screen.blit(overlay, (0, 0))
            
            screen.blit(font_title.render("PAUSED", True, COLOR_SUPER_FOOD), (WIDTH // 2 - 70, HEIGHT // 2 - 100))
            btn_resume, _ = draw_button(screen, "RESUME", WIDTH//2 - 100, HEIGHT//2 - 20, 200, 45, mouse_pos)
            btn_menu, _ = draw_button(screen, "BACK TO MENU", WIDTH//2 - 100, HEIGHT//2 + 40, 200, 45, mouse_pos)
            btn_quit, _ = draw_button(screen, "QUIT GAME", WIDTH//2 - 100, HEIGHT//2 + 100, 200, 45, mouse_pos)
            
            if clicked:
                if btn_resume.collidepoint(mouse_pos): game_state = "PLAYING"
                elif btn_menu.collidepoint(mouse_pos): game_state = "MENU"
                elif btn_quit.collidepoint(mouse_pos): running = False

        # GAME OVER
        elif game_state == "GAME OVER":
            draw_obstacles(screen, obstacles)
            snake.draw(screen)
            draw_top_hud_bar(screen, score, high_score, current_fps, ai_detected)

            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((50, 10, 10, 190)) 
            screen.blit(overlay, (0, 0))

            screen.blit(font_title.render("GAME OVER", True, COLOR_FOOD), (WIDTH // 2 - 110, HEIGHT // 2 - 110))
            screen.blit(font_normal.render(f"SCORE: {score}  |  HIGH SCORE: {high_score}", True, COLOR_TEXT), (WIDTH // 2 - 100, HEIGHT // 2 - 40))
            
            btn_retry, _ = draw_button(screen, "RETRY", WIDTH//2 - 100, HEIGHT//2 + 10, 200, 45, mouse_pos)
            btn_menu, _ = draw_button(screen, "BACK TO MENU", WIDTH//2 - 100, HEIGHT//2 + 70, 200, 45, mouse_pos)
            btn_quit, _ = draw_button(screen, "QUIT GAME", WIDTH//2 - 100, HEIGHT//2 + 130, 200, 45, mouse_pos)

            if clicked:
                if btn_retry.collidepoint(mouse_pos):
                    snake.reset()
                    obstacles = generate_obstacles(settings["level"])
                    food.randomize_position(obstacles, snake.body)
                    score = 0
                    current_fps = BASE_FPS
                    game_state = "PLAYING"
                elif btn_menu.collidepoint(mouse_pos): game_state = "MENU"
                elif btn_quit.collidepoint(mouse_pos): running = False

        # Phủ lớp hiển thị độ sáng
        apply_brightness(screen)

        pygame.display.flip()
        clock.tick(int(current_fps))  

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
