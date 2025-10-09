import pygame
import threading
import math
import time
from collections import deque

# --------- Shared data ---------
data_buffer = deque(maxlen=400)  # sinusoidal data
lock = threading.Lock()

# --------- Sinusoidal data generator thread ---------
def generate_data():
    t = 0
    while True:
        value = math.sin(t)
        with lock:
            data_buffer.append(value)
        t += 0.1
        time.sleep(0.02)  # adjust speed

# Start data thread
threading.Thread(target=generate_data, daemon=True).start()

# --------- Pygame setup ---------
pygame.init()
WIDTH, HEIGHT = 800, 400
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sinusoidal Plot + Bouncing Circle")
clock = pygame.time.Clock()
FPS = 60

# Circle properties (right side)
circle_x = WIDTH * 3 // 4
circle_y = HEIGHT // 2
circle_radius = 30
dx, dy = 5, 3
circle_color = (255, 0, 0)

running = True
while running:
    clock.tick(FPS)
    window.fill((0, 0, 0))  # black background

    # --------- Draw sinusoidal plot (left side) ---------
    with lock:
        ydata = list(data_buffer)

    if len(ydata) > 1:
        plot_width = WIDTH // 2
        plot_height = HEIGHT
        scale_y = plot_height // 2 - 10  # scale sine wave
        prev_x = 0
        prev_y = plot_height // 2 - int(ydata[0] * scale_y)
        for i, val in enumerate(ydata[-plot_width:]):
            x = i
            y = plot_height // 2 - int(val * scale_y)
            pygame.draw.line(window, (0, 255, 0), (x, prev_y), (x + 1, y))
            prev_y = y

    # Vertical divider
    pygame.draw.line(window, (255, 255, 255), (WIDTH//2, 0), (WIDTH//2, HEIGHT), 2)

    # --------- Update and draw bouncing circle (right side) ---------
    circle_x += dx
    circle_y += dy
    if circle_x - circle_radius <= WIDTH//2 or circle_x + circle_radius >= WIDTH:
        dx = -dx
    if circle_y - circle_radius <= 0 or circle_y + circle_radius >= HEIGHT:
        dy = -dy
    pygame.draw.circle(window, circle_color, (circle_x, circle_y), circle_radius)

    # --------- Handle events ---------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()

pygame.quit()
