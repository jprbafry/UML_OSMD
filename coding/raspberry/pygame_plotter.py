import pygame
import threading
import math
import time
from collections import deque



WIDTH, HEIGHT = 800, 400

# Setting up Data Buffer
data_buffer = deque(maxlen=800)  # sinusoidal data
lock = threading.Lock()

# --------- Sinusoidal data generator thread ---------
def generate_data():
    t = 0
    while True:
        value = math.sin(t)
        with lock:
            data_buffer.append(value)
        t += 0.05
        time.sleep(0.01)  # adjust speed

# Start data thread
threading.Thread(target=generate_data, daemon=True).start()

# PyGame Setup
pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sinusoidal Plot + Bouncing Circle")
clock = pygame.time.Clock()
FPS = 60


running = True
while running:
    clock.tick(FPS)
    window.fill((0, 0, 0))  # black background

    # Drawing Sinusoidal
    with lock:
        ydata = list(data_buffer)

    if len(ydata) > 1:
        plot_width = WIDTH 
        plot_height = HEIGHT
        scale_y = plot_height // 2 - 10  # scale sine wave
        prev_x = 0
        prev_y = plot_height // 2 - int(ydata[0] * scale_y)
        for i, val in enumerate(ydata[-plot_width:]):
            x = i
            y = plot_height // 2 - int(val * scale_y)
            pygame.draw.line(window, (0, 255, 0), (x, prev_y), (x + 1, y))
            prev_y = y

    # No event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()

pygame.quit()
