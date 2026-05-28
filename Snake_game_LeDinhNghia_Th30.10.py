import pygame
import random
import cv2
import numpy as np
import sys
import math

# Khởi tạo Pygame
pygame.init()

# I. CẤU HÌNH VÀ MÀU SẮC
WIDTH, HEIGHT = 640, 480  
GRID_SIZE = 20
HUD_TOP_HEIGHT = 40  
COLOR_BG = (10, 11, 18)             
COLOR_GRID = (22, 25, 38)           
COLOR_SNAKE_HEAD = (0, 255, 204)     
COLOR_SNAKE_BORDER = (0, 150, 120)   
COLOR_FOOD = (255, 0, 127)           
COLOR_SUPER_FOOD = (255, 211, 42)    
COLOR_TEXT = (240, 244, 255)       
COLOR_SUBTEXT = (90, 105, 120)       
COLOR_MENU_BTN = (44, 62, 80)        
COLOR_HUD_BORDER = (0, 255, 204)    

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SNAKE GAME")
clock = pygame.time.Clock()

font_title = pygame.font.SysFont("Segoe UI", 46, bold=True)
font_normal = pygame.font.SysFont("Segoe UI", 15, bold=False) 
font_bold = pygame.font.SysFont("Segoe UI", 15, bold=True)
font_small = pygame.font.SysFont("Segoe UI", 12, bold=False)  


# II. LỚP ĐỐI TƯỢNG GAME

# 1. Lớp Rắn
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
        if self.direction == "UP":
            head[1] -= GRID_SIZE
        elif self.direction == "DOWN":
            head[1] += GRID_SIZE
        elif self.direction == "LEFT":
            head[0] -= GRID_SIZE
        elif self.direction == "RIGHT":
            head[0] += GRID_SIZE

        head[0] = head[0] % WIDTH
        
        if head[1] < HUD_TOP_HEIGHT:
            head[1] = HEIGHT - GRID_SIZE
        elif head[1] >= HEIGHT:
            head[1] = HUD_TOP_HEIGHT

        self.body.insert(0, head)
        
        if self.grow_counter > 0:
            self.grow_counter -= 1
        else:
            self.body.pop()
            
        self.chroma_tick = (self.chroma_tick + 4) % 360

    def change_direction(self, new_dir):
        if new_dir == "UP" and self.direction != "DOWN":
            self.direction = new_dir
        elif new_dir == "DOWN" and self.direction != "UP":
            self.direction = new_dir
        elif new_dir == "LEFT" and self.direction != "RIGHT":
            self.direction = new_dir
        elif new_dir == "RIGHT" and self.direction != "LEFT":
            self.direction = new_dir

    def check_collision(self):
        head = self.body[0]
        if head in self.body[1:]:
            return True
        return False

    def draw(self, surface):
        num_segments = len(self.body)
        
        # 1. Quầng sáng khuếch tán
        for i, segment in enumerate(self.body):
            size_factor = 1.0 - (i / num_segments) * 0.5
            current_glow = int(max(2, (GRID_SIZE // 2) * size_factor))
            center_x = segment[0] + GRID_SIZE // 2
            center_y = segment[1] + GRID_SIZE // 2
            pygame.draw.circle(surface, (10, 26, 36), (center_x, center_y), current_glow + 1)

        # 2. Thân rắn
        for i in range(1, num_segments):
            segment = self.body[i]
            wave_calc = math.sin(math.radians(self.chroma_tick + (i * 12)))
            g_val = int(130 + 80 * wave_calc)
            b_val = int(190 + 65 * wave_calc)
            
            ratio = 1.0 - (i / num_segments) * 0.4
            body_color = (0, int(g_val * ratio), int(b_val * ratio))
            inner_color = (0, int(min(255, g_val * 1.3) * ratio), int(min(255, b_val * 1.3) * ratio))
            
            # Sử dụng tỷ lệ giảm mượt tịnh tiến dần (từ kích thước tối đa 22px đè viền xuống đuôi nhỏ nhất)
            taper_factor = 1.0 - (i / num_segments) * 0.45
            size = int((GRID_SIZE + 2) * taper_factor)
            if size < 6: size = 6  
            
            # Giữ tâm các đốt luôn nằm chính giữa ô lưới để không lệch trục hình học
            offset = (GRID_SIZE - size) // 2
            rect_x = segment[0] + offset
            rect_y = segment[1] + offset
            
            # Bo góc nhẹ tròn trịa cho các đốt thân (border_radius tự động giảm theo kích thước đốt)
            r_val = max(2, size // 4)
            pygame.draw.rect(surface, body_color, pygame.Rect(rect_x, rect_y, size, size), border_radius=r_val)
            inner_size = max(2, size - 4)
            pygame.draw.rect(surface, inner_color, pygame.Rect(rect_x + 2, rect_y + 2, inner_size, inner_size), border_radius=max(1, r_val - 1))

        # 3. Đầu rắn
        hx, hy = self.body[0][0], self.body[0][1]

        pygame.draw.rect(surface, COLOR_SNAKE_BORDER, pygame.Rect(hx - 1, hy - 1, GRID_SIZE + 2, GRID_SIZE + 2), border_radius=8)
        pygame.draw.rect(surface, COLOR_SNAKE_HEAD, pygame.Rect(hx, hy, GRID_SIZE, GRID_SIZE), border_radius=6)
        visor_color = (15, 20, 30)
        blink_effect = math.sin(math.radians(self.chroma_tick * 2))
        if blink_effect > 0.85:  
            visor_color = (255, 255, 255)
            
        if self.direction in ["RIGHT", "LEFT"]:
            ox = 12 if self.direction == "RIGHT" else 4
            pygame.draw.rect(surface, visor_color, pygame.Rect(hx + ox, hy + 4, 4, 5), border_radius=2)
            pygame.draw.rect(surface, visor_color, pygame.Rect(hx + ox, hy + 11, 4, 5), border_radius=2)
        elif self.direction in ["UP", "DOWN"]:
            oy = 4 if self.direction == "UP" else 12
            pygame.draw.rect(surface, visor_color, pygame.Rect(hx + 4, hy + oy, 5, 4), border_radius=2)
            pygame.draw.rect(surface, visor_color, pygame.Rect(hx + 11, hy + oy, 5, 4), border_radius=2)

# 2. Lớp Thức Ăn
class Food:
    def __init__(self):
        self.position = [0, 0]
        self.is_super = False 
        self.pulse_tick = 0
        self.randomize_position()

    def randomize_position(self):
        grid_x_max = (WIDTH - GRID_SIZE) // GRID_SIZE
        grid_y_start = HUD_TOP_HEIGHT // GRID_SIZE
        grid_y_max = (HEIGHT - GRID_SIZE) // GRID_SIZE
        
        self.position = [
            random.randint(0, grid_x_max) * GRID_SIZE,
            random.randint(grid_y_start, grid_y_max) * GRID_SIZE
        ]
        self.is_super = random.random() < 0.25

    def draw(self, surface):
        self.pulse_tick = (self.pulse_tick + 6) % 360
        fx = self.position[0] + GRID_SIZE // 2
        fy = self.position[1] + GRID_SIZE // 2
        pulse_scale = math.sin(math.radians(self.pulse_tick)) * 2.0

        if self.is_super:
            pygame.draw.circle(surface, (55, 45, 15), (fx, fy), int(GRID_SIZE // 2 + 7 + pulse_scale))
            pygame.draw.circle(surface, (160, 125, 30), (fx, fy), int(GRID_SIZE // 2 + 2))
            pygame.draw.circle(surface, COLOR_SUPER_FOOD, (fx, fy), int(GRID_SIZE // 2 - 1))
            pygame.draw.circle(surface, (255, 255, 255), (fx - 3, fy - 3), 2.5)
        else:
            pygame.draw.circle(surface, (45, 5, 25), (fx, fy), int(GRID_SIZE // 2 + 5 + pulse_scale))
            pygame.draw.circle(surface, COLOR_FOOD, (fx, fy), int(GRID_SIZE // 2 - 1))
            pygame.draw.circle(surface, (255, 130, 190), (fx, fy), int(GRID_SIZE // 2 - 4))
            pygame.draw.circle(surface, (255, 255, 255), (fx - 2, fy - 2), 1.5)


class ImageProcessor:
    @staticmethod
    def process_and_detect(surface):
        view = pygame.surfarray.array3d(surface)
        view = view.transpose([1, 0, 2])
        img_bgr = cv2.cvtColor(view, cv2.COLOR_RGB2BGR)
        img_blur = cv2.GaussianBlur(img_bgr, (5, 5), 0)
        img_hsv = cv2.cvtColor(img_blur, cv2.COLOR_BGR2HSV)

        lower_green = np.array([75, 100, 100])  
        upper_green = np.array([95, 255, 255])
        mask_green = cv2.inRange(img_hsv, lower_green, upper_green)
        contours_green, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        return len(contours_green) > 0


def draw_matrix_background(surface):
    surface.fill(COLOR_BG)
    for x in range(0, WIDTH + 1, GRID_SIZE):
        pygame.draw.line(surface, COLOR_GRID, (x, HUD_TOP_HEIGHT), (x, HEIGHT), 1)
    for y in range(HUD_TOP_HEIGHT, HEIGHT + 1, GRID_SIZE):
        pygame.draw.line(surface, COLOR_GRID, (0, y), (WIDTH, y), 1)


def draw_top_hud_bar(surface, score, high_score, fps):
    pygame.draw.rect(surface, (14, 16, 26), pygame.Rect(0, 0, WIDTH, HUD_TOP_HEIGHT))
    pygame.draw.line(surface, COLOR_HUD_BORDER, (0, HUD_TOP_HEIGHT - 1), (WIDTH, HUD_TOP_HEIGHT - 1), 2)
    
    score_text = font_bold.render(f"SCORE: {score}", True, COLOR_TEXT)
    speed_text = font_normal.render(f"SPEED: {fps:.1f}", True, COLOR_SNAKE_HEAD)
    h_score_text = font_normal.render(f"HIGH SCORE: {high_score}", True, COLOR_SUBTEXT)
    
    surface.blit(score_text, (20, 3))
    surface.blit(speed_text, (WIDTH // 2 - speed_text.get_width() // 2, 3)) 
    surface.blit(h_score_text, (WIDTH - h_score_text.get_width() - 20, 3))
    
    guide_txt = font_small.render("CONTROLS: [Arrows] Move  |  [P] Pause  |  [R] Reboot", True, COLOR_SUBTEXT)
    surface.blit(guide_txt, (WIDTH // 2 - guide_txt.get_width() // 2, 22))


# ---------------------------------------------------------
# 3. VÒNG LẶP CHÍNH CHƯƠNG TRÌNH
# ---------------------------------------------------------
def main():
    snake = Snake()
    food = Food()
    score = 0
    high_score = 0  
    BASE_FPS = 8.0
    current_fps = BASE_FPS
    game_state = "MENU" 

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == "MENU":
                    start_btn_rect = pygame.Rect(WIDTH // 2 - 110, HEIGHT // 2 + 20, 220, 50)
                    if start_btn_rect.collidepoint(mouse_pos):
                        game_state = "PLAYING"
            elif event.type == pygame.KEYDOWN:
                if game_state == "MENU":
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        game_state = "PLAYING"
                elif game_state == "PLAYING":
                    if event.key == pygame.K_UP:
                        snake.change_direction("UP")
                    elif event.key == pygame.K_DOWN:
                        snake.change_direction("DOWN")
                    elif event.key == pygame.K_LEFT:
                        snake.change_direction("LEFT")
                    elif event.key == pygame.K_RIGHT:
                        snake.change_direction("RIGHT")
                    elif event.key == pygame.K_p:
                        game_state = "PAUSED"
                elif game_state == "PAUSED":
                    if event.key == pygame.K_p:
                        game_state = "PLAYING"
                elif game_state == "GAME OVER":
                    if event.key == pygame.K_r:
                        snake.reset()
                        food.randomize_position()
                        score = 0
                        current_fps = BASE_FPS  
                        game_state = "PLAYING"

        draw_matrix_background(screen)

        if game_state == "MENU":
            title_text = font_title.render("SNAKE GAME", True, COLOR_SNAKE_HEAD)
            screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 100))
            sub_title = font_normal.render("eat food to increase length and avoid biting your body and tail.", True, COLOR_SUBTEXT)
            screen.blit(sub_title, (WIDTH // 2 - sub_title.get_width() // 2, HEIGHT // 2 - 40))
            menu_guide1 = font_small.render("Press ENTER or SPACE to Quick Start", True, COLOR_TEXT)
            menu_guide2 = font_small.render("Use Arrow Keys to Navigate & Avoid biting your tail", True, COLOR_SUBTEXT)
            screen.blit(menu_guide1, (WIDTH // 2 - menu_guide1.get_width() // 2, HEIGHT // 2 - 5))
            screen.blit(menu_guide2, (WIDTH // 2 - menu_guide2.get_width() // 2, HEIGHT // 2 + 15))

            start_btn_rect = pygame.Rect(WIDTH // 2 - 110, HEIGHT // 2 + 50, 220, 50)
            if start_btn_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, (0, 255, 204), start_btn_rect, border_radius=6, width=2)
                btn_text = font_bold.render("ENTER THE GAME", True, COLOR_SNAKE_HEAD)
            else:
                pygame.draw.rect(screen, COLOR_MENU_BTN, start_btn_rect, border_radius=6)
                btn_text = font_bold.render("ENTER THE GAME", True, COLOR_TEXT)
            screen.blit(btn_text, (WIDTH // 2 - btn_text.get_width() // 2, HEIGHT // 2 + 61))

        elif game_state == "PLAYING":
            snake.move()

            if snake.body[0] == food.position:
                if food.is_super:
                    snake.grow_counter += 3  
                    score += 3
                else:
                    snake.grow_counter += 1  
                    score += 1
                food.randomize_position()

            if snake.check_collision():
                if score > high_score:
                    high_score = score
                game_state = "GAME OVER"

            snake.draw(screen)
            food.draw(screen)

            _ = ImageProcessor.process_and_detect(screen)

            current_fps = BASE_FPS + (score // 10) * 1.5
            draw_top_hud_bar(screen, score, high_score, current_fps)

        elif game_state == "PAUSED":
            snake.draw(screen)
            food.draw(screen)
            draw_top_hud_bar(screen, score, high_score, current_fps)
            
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 11, 18, 190)) 
            screen.blit(overlay, (0, 0))
            
            pause_title = font_title.render("PAUSED", True, COLOR_SUPER_FOOD)
            pause_hint = font_bold.render("Press 'P' to Resume The Game", True, COLOR_TEXT)
            screen.blit(pause_title, (WIDTH // 2 - pause_title.get_width() // 2, HEIGHT // 2 - 40))
            screen.blit(pause_hint, (WIDTH // 2 - pause_hint.get_width() // 2, HEIGHT // 2 + 20))

        elif game_state == "GAME OVER":
            over_text = font_title.render("GAME OVER", True, COLOR_FOOD)
            score_final_text = font_normal.render(f"SCORE: {score}  |  HIGH SCORE: {high_score}", True, COLOR_TEXT)
            restart_text = font_bold.render("Press 'R' To Restart The Game", True, COLOR_SNAKE_HEAD)
            screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 60))
            screen.blit(score_final_text, (WIDTH // 2 - score_final_text.get_width() // 2, HEIGHT // 2 + 10))
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 60))

        pygame.display.flip()
        clock.tick(int(current_fps))  

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()