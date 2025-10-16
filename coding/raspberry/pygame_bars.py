import pygame
import threading
import time
import os

# ------------------------
# Bar class
# ------------------------
class Bar:
    def __init__(self, x, y, width, height, min_val, max_val, colors, label, font, surface):
        """
        x, y: top-left corner
        width, height: dimensions of the bar
        min_val, max_val: values corresponding to bottom/top
        colors: list of 2 or 3 colors [(bottom), (middle), (top)]
        label: text label
        font: pygame font object
        surface: pygame surface to draw on
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_val = min_val
        self.max_val = max_val
        self.colors = colors
        self.label = label
        self.font = font
        self.surface = surface
        self.current_val = min_val  # initial value
        self.rect_height = 5  # height of marker rectangle

    def set_value(self, val):
        # Clamp value
        self.current_val = max(self.min_val, min(self.max_val, val))

    def draw(self):
        # Draw label
        label_surf = self.font.render(self.label, True, (255, 255, 255))
        self.surface.blit(label_surf, (self.x, self.y - 25))

        # Draw gradient bar
        for i in range(self.height):
            ratio = i / self.height
            color = self.get_color(ratio)
            pygame.draw.line(self.surface, color, 
                             (self.x, self.y + self.height - i),
                             (self.x + self.width, self.y + self.height - i))

        # Draw marker rectangle
        value_ratio = (self.current_val - self.min_val) / (self.max_val - self.min_val)
        marker_y = self.y + self.height - int(value_ratio * self.height)
        pygame.draw.rect(self.surface, (255, 255, 255),
                         (self.x, marker_y - self.rect_height//2, self.width, self.rect_height))

    def get_color(self, ratio):
        """Compute the color at given ratio (0 bottom -> 1 top)"""
        if len(self.colors) == 2:
            bottom, top = self.colors
            return tuple(int(bottom[i] + (top[i] - bottom[i]) * ratio) for i in range(3))
        elif len(self.colors) == 3:
            bottom, middle, top = self.colors
            if ratio < 0.5:
                # bottom -> middle
                local_ratio = ratio / 0.5
                return tuple(int(bottom[i] + (middle[i] - bottom[i]) * local_ratio) for i in range(3))
            else:
                # middle -> top
                local_ratio = (ratio - 0.5) / 0.5
                return tuple(int(middle[i] + (top[i] - middle[i]) * local_ratio) for i in range(3))
        else:
            return (255, 255, 255)  # fallback

# ------------------------
# Thread to update values
# ------------------------
def value_updater(file_path, temp_bar, intensity_bar):
    while True:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    try:
                        temp_val = float(lines[0].strip())
                        intensity_val = float(lines[1].strip())
                        temp_bar.set_value(temp_val)
                        intensity_bar.set_value(intensity_val)
                    except ValueError:
                        pass  # ignore malformed lines
        time.sleep(0.1)  # update rate

# ------------------------
# Main pygame loop
# ------------------------
def main():
    pygame.init()
    WIDTH, HEIGHT = 400, 400
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Bars Demo")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    # Create bars
    temp_bar = Bar(x=50, y=50, width=50, height=300,
                   min_val=-10, max_val=60,
                   colors=[(0,0,255),(255,255,255),(255,0,0)],  # blue -> red
                   label="Temperature", font=font, surface=screen)

    intensity_bar = Bar(x=250, y=50, width=50, height=300,
                        min_val=0, max_val=1,
                        colors=[(255,250,220),(240,130,15)],  # white -> yellow
                        label="Intensity", font=font, surface=screen)

    # Start updater thread
    data_file = "values.txt"
    updater_thread = threading.Thread(target=value_updater, args=(data_file,temp_bar,intensity_bar), daemon=True)
    updater_thread.start()

    running = True
    while running:
        screen.fill((0,0,0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw bars
        temp_bar.draw()
        intensity_bar.draw()

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
