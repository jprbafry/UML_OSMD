
import pygame
import time
import math
import threading
from itertools import chain


color_desired = (255, 0, 0) # red
color_current = (0,255,0) # green
color_text = (255,255,255) # white
color_background = (10,10,10) # dark grey
color_line = (150,150,150) # grey
color_button_busy = (255,255,0) # yellow
color_button_idle = (255,255,255) # white

# KNOB
class Knob:
    def __init__(self, cx, cy, radius, font, min_val=0, max_val=360):
        self.cx, self.cy = cx, cy
        self.radius = radius
        self.min_val = min_val
        self.max_val = max_val
        self.angle = math.radians(min_val)
        self.old_des_val = min_val
        self.new_des_val = min_val
        self.old_cur_val = min_val
        self.new_cur_val = min_val
        self.dragging = False
        self.font = font

    def draw(self, surface):
        # Draw knob outline
        pygame.draw.circle(surface, color_line, (self.cx, self.cy), self.radius, 5)

        # Desired (red) line
        px_des = self.cx + self.radius * math.cos(math.radians(self.new_des_val) - math.pi / 2)
        py_des = self.cy + self.radius * math.sin(math.radians(self.new_des_val) - math.pi / 2)
        pygame.draw.line(surface, color_desired, (self.cx, self.cy), (px_des, py_des), 4)

        # Current (green) line
        px_cur = self.cx + self.radius * math.cos(math.radians(self.new_cur_val) - math.pi / 2)
        py_cur = self.cy + self.radius * math.sin(math.radians(self.new_cur_val) - math.pi / 2)
        pygame.draw.line(surface, color_current, (self.cx, self.cy), (px_cur, py_cur), 3)

        # Draw desired value
        cur_des_txt = f"{int(self.new_cur_val)} ---> [{int(self.new_des_val)}]"
        val_text = self.font.render(cur_des_txt, True, color_text)
        text_rect = val_text.get_rect(center=(self.cx, self.cy + self.radius * 1.2))
        surface.blit(val_text, text_rect)

    def update_current_value(self, new_value):
        self.old_cur_val = self.new_cur_val
        self.new_cur_val = new_value

    def update_desired_value(self, event):
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
            angle = math.atan2(dy, dx) + math.pi / 2            
            new_val = (math.degrees(angle) + 360) % 360
            # Prevent jump 0 <--> 360
            if abs(new_val - self.old_des_val) > 30:
                self.new_des_val = self.old_des_val
            else:
                self.old_des_val = self.new_des_val
                self.new_des_val = new_val
            self.angle = math.radians(self.new_des_val)



# SLIDER
class Slider:
    def __init__(self, x, y, width, font, min_val=0, max_val=180):
        self.x, self.y = x, y
        self.width = width
        self.min_val = min_val
        self.max_val = max_val
        self.old_des_val = min_val
        self.new_des_val = min_val
        self.old_cur_val = min_val
        self.new_cur_val = min_val
        self.dragging = False
        self.font = font

    def draw(self, surface):
        # Draw slider line
        pygame.draw.line(surface, color_line, (self.x, self.y), (self.x + self.width, self.y), 5)
        
        # Desired (red) circle
        pos_des = self.x + (self.new_des_val - self.min_val) / (self.max_val - self.min_val) * self.width
        pygame.draw.circle(surface, color_desired, (int(pos_des), self.y), 10, 5)

        # Current (green) circle
        pos_cur = self.x + (self.new_cur_val - self.min_val) / (self.max_val - self.min_val) * self.width
        pygame.draw.circle(surface, color_current, (int(pos_cur), self.y), 7, 3)

        # Draw desired value
        cur_des_txt = f"{int(self.new_cur_val)} ---> [{int(self.new_des_val)}]"
        val_text = self.font.render(cur_des_txt, True, color_text)
        text_rect = val_text.get_rect(center=(self.x + self.width / 2, self.y + self.width / 6))
        surface.blit(val_text, text_rect)

    def update_current_value(self, new_value):
        self.old_cur_val = self.new_cur_val
        self.new_cur_val = new_value

    def update_desired_value(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            pos = self.x + (self.new_des_val - self.min_val) / (self.max_val - self.min_val) * self.width
            if abs(mx - pos) < 10 and abs(my - self.y) < 15:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mx, _ = pygame.mouse.get_pos()
            mx = max(self.x, min(self.x + self.width, mx))
            self.old_des_val = self.new_des_val
            self.new_des_val = self.min_val + (mx - self.x) / self.width * (self.max_val - self.min_val)


class Label:
    def __init__(self, text, x, y, font, color=color_text, center=True):
        self.text = text
        self.x = x
        self.y = y
        self.font = font
        self.color = color
        self.center = center

    def draw(self, surface):
        text_surface = self.font.render(self.text, True, self.color)
        if self.center:
            text_rect = text_surface.get_rect(center=(self.x, self.y))
        else:
            text_rect = text_surface.get_rect(topleft=(self.x, self.y))
        surface.blit(text_surface, text_rect)

# BUTTON
class Button:
    def __init__(self, x, y, size, font, action, color_idle=color_button_idle, color_active=color_button_busy):
        self.x = x
        self.y = y
        self.size = size
        self.font = font
        self.text = "PRESS"
        self.action = action
        self.color_idle = color_idle
        self.color_active = color_active
        self.active = False
        self.rect = pygame.Rect(x - size//2, y - size//2, size, size)

    def draw(self, surface):
        color = self.color_active if self.active else self.color_idle
        pygame.draw.rect(surface, color, self.rect)
        # Draw text
        text_surf = self.font.render(self.text, True, (0,0,0))
        text_rect = text_surf.get_rect(center=(self.x, self.y))
        surface.blit(text_surf, text_rect)

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if self.rect.collidepoint(mx, my):
                self.active = True

                # Run the action in a separate thread so it doesn't block Pygame
                def run_action():
                    self.action()
                    self.active = False

                threading.Thread(target=run_action, daemon=True).start()

# PANEL
class Panel:
    """A Panel containing multiple knobs and sliders grouped logically"""
    def __init__(self, width=800, height=400, fps=60):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Control Panel")
        self.ratio_w_knob = 0.25
        self.ratio_h_knob = 0.42
        self.ratio_r_knob = 0.12
        self.ratio_h_slider = 0.80
        self.ratio_w_legends = 0.50
        self.ratio_h_titles = 0.12
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.fps = fps
        self.running = True
        self.knobs, self.sliders, self.legends, self.titles = self.create_controls()
        self.buttons = []
        # Example: button at center-bottom
        btn_x = self.width // 2
        btn_y = int(self.height * 0.15)
        btn_size = 80
        self.buttons.append(Button(btn_x, btn_y, btn_size, self.font, self.pulse_knobs_sliders))


    
    def pulse_knobs_sliders(self, N=30, delay=200):
        """
        Smoothly move each desired value from its current value up to current+N,
        then back down to the original value, step by step.
        delay in milliseconds between steps.
        """
        # Store original desired values
        original_knob_vals = [k.new_des_val for k in self.knobs]
        original_slider_vals = [s.new_des_val for s in self.sliders]

        # Step up
        for step in range(1, N + 1):
            for i, k in enumerate(self.knobs):
                k.new_des_val = original_knob_vals[i] + step
            for i, s in enumerate(self.sliders):
                s.new_des_val = original_slider_vals[i] + step
            self.draw()
            pygame.time.wait(delay)

        # Step down
        for step in range(N, -1, -1):
            for i, k in enumerate(self.knobs):
                k.new_des_val = original_knob_vals[i] + step
            for i, s in enumerate(self.sliders):
                s.new_des_val = original_slider_vals[i] + step
            self.draw()
            pygame.time.wait(delay)

    def create_controls(self):
        knobs = []
        sliders = []
        legends = []
        titles = []

        # Legends
        legends.append(Label("AZIMUTHAL", self.width * self.ratio_w_legends,
                            self.height * self.ratio_h_knob, self.font))
        legends.append(Label("POLAR", self.width * self.ratio_w_legends,
                            self.height * self.ratio_h_slider, self.font))
        
        # Left side (Light Source)
        cx_k = self.width * self.ratio_w_knob
        cy_k = self.height * self.ratio_h_knob
        r = self.height * self.ratio_r_knob
        l = 2 * r
        cx_s = cx_k - r
        cy_s = self.height * self.ratio_h_slider

        knobs.append(Knob(cx_k, cy_k, r, self.font))
        sliders.append(Slider(cx_s, cy_s, l, self.font))
        titles.append(Label("LIGHT SOURCE", cx_k, self.height*self.ratio_h_titles, self.font))

        # Right side (Detector)
        cx_k = self.width - cx_k
        cy_k = self.height * self.ratio_h_knob
        r = self.height * self.ratio_r_knob
        l = 2 * r
        cx_s = cx_k - r
        cy_s = self.height * self.ratio_h_slider

        knobs.append(Knob(cx_k, cy_k, r, self.font))
        sliders.append(Slider(cx_s, cy_s, l, self.font))
        titles.append(Label("DETECTOR", cx_k, self.height*self.ratio_h_titles, self.font))

        return knobs, sliders, legends, titles


    def draw(self):
        self.screen.fill(color_background)

        for element in chain(self.knobs, self.sliders, self.titles, self.legends, self.buttons):
            element.draw(self.screen)

        pygame.display.flip()

    def update_desired_values(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            for knob in self.knobs:
                knob.update_desired_value(event)
            for slider in self.sliders:
                slider.update_desired_value(event)
            for button in self.buttons:
                button.check_click(event)

    def run(self):
        while self.running:
            self.update_desired_values()
            self.draw()
            self.clock.tick(self.fps)
        pygame.quit()

    def print_values(self, interval=0.1):
        """Print knob and slider values only when they change"""
        prev_values = None

        while self.running:
            all_values = [k.new_des_val for k in self.knobs] + [s.new_des_val for s in self.sliders]

            if prev_values is None or all_values != prev_values:
                prev_values = all_values.copy()
                output = []
                for i, knob in enumerate(self.knobs, 1):
                    output.append(f"Knob{i}={knob.new_des_val:.1f}")
                for i, slider in enumerate(self.sliders, 1):
                    output.append(f"Slider{i}={slider.new_des_val:.1f}")
                print(" | ".join(output))

            time.sleep(interval)


