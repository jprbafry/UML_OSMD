import pygame, math, threading, time

# Knob: for azimuthal rotation
class Knob:
    def __init__(self, name, cx, cy, radius, min_val=0, max_val=360):
        self.name = name
        self.cx, self.cy = cx, cy
        self.radius = radius
        self.min_val = min_val
        self.max_val = max_val
        self.angle = math.radians(min_val)
        self.value = min_val
        self.dragging = False

    def draw(self, surface):
        pygame.draw.circle(surface, (100, 100, 100), (self.cx, self.cy), self.radius, 5)
        px = self.cx + self.radius * math.cos(self.angle - math.pi/2)
        py = self.cy + self.radius * math.sin(self.angle - math.pi/2)
        pygame.draw.line(surface, (255, 0, 0), (self.cx, self.cy), (px, py), 4)

    def update_value(self):
        deg = (math.degrees(self.angle) + 360) % 360
        self.value = max(self.min_val, min(self.max_val, deg))
        self.angle = math.radians(self.value)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            dx, dy = mx - self.cx, my - self.cy
            dist = math.hypot(dx, dy)
            if abs(dist - self.radius) < 15:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mx, my = pygame.mouse.get_pos()
            dx, dy = mx - self.cx, my - self.cy
            angle = math.atan2(dy, dx) + math.pi/2
            self.angle = angle
            self.update_value()


class Slider:
    def __init__(self, x, y, width, min_val=0, max_val=180):
        self.x, self.y = x, y
        self.width = width
        self.min_val = min_val
        self.max_val = max_val
        self.value = min_val
        self.dragging = False

    def draw(self, surface):
        pygame.draw.line(surface, (150,150,150), (self.x, self.y), (self.x+self.width, self.y), 5)
        pos = self.x + (self.value - self.min_val)/(self.max_val - self.min_val)*self.width
        pygame.draw.circle(surface, (0,255,0), (int(pos), self.y), 10)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            pos = self.x + (self.value - self.min_val)/(self.max_val - self.min_val)*self.width
            if abs(mx - pos) < 10 and abs(my - self.y) < 15:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mx, _ = pygame.mouse.get_pos()
            mx = max(self.x, min(self.x + self.width, mx))
            self.value = self.min_val + (mx - self.x)/self.width*(self.max_val - self.min_val)


# Initializing Elements of the Control Interface
def init():
    pygame.init()
    screen = pygame.display.set_mode((800, 400))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    knob1 = Knob('Source', 200, 150, 50)
    slider1 = Slider(150, 250, 100)
    knob2 = Knob('Detector', 600, 150, 50)
    slider2 = Slider(550, 250, 100)

    knobs = [knob1, knob2]
    sliders = [slider1, slider2]

    return screen, clock, font, knobs, sliders



def print_values(knobs, sliders):
    while True:
        print(f"Light Knob: {knobs[0].value:.1f}, Light Slider: {sliders[0].value:.1f}, "
              f"Detector Knob: {knobs[1].value:.1f}, Detector Slider: {sliders[1].value:.1f}")
        time.sleep(1)


def main(screen, clock, font, knobs, sliders):
    running = True
    while running:
        screen.fill((30,30,30))

        title_ls = font.render("Light Source", True, (255,255,255))
        screen.blit(title_ls, (200 - title_ls.get_width()//2, 50))
        title_det = font.render("Detector", True, (255,255,255))
        screen.blit(title_det, (600 - title_det.get_width()//2, 50))

        azimuthal = font.render("Azimuthal", True, (255,255,255))
        polar = font.render("Polar", True, (255,255,255))
        screen.blit(azimuthal, (400 - azimuthal.get_width()//2, 150))
        screen.blit(polar, (400 - polar.get_width()//2, 250))

        for knob in knobs:
            knob.draw(screen)
            val_text = font.render(f"{int(knob.value)}", True, (255,255,255))
            screen.blit(val_text, (knob.cx, knob.cy + 50))
        for slider in sliders:
            slider.draw(screen)
            val_text = font.render(f"{int(slider.value)}", True, (255,255,255))
            screen.blit(val_text, (slider.x+48, slider.y + 20))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for knob in knobs:
                knob.handle_event(event)
            for slider in sliders:
                slider.handle_event(event)

        clock.tick(60)

    pygame.quit()


# ---- Run the application ----
if __name__ == "__main__":

    screen, clock, font, knobs, sliders = init()

    # Start the printing thread
    threading.Thread(target=print_values, args=(knobs, sliders), daemon=True).start()

    main(screen, clock, font, knobs, sliders)
