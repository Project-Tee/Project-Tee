import pygame
import time
import os

print("started")
pygame.init()

pygame.mouse.set_visible(False)

screen = pygame.display.set_mode((1024, 600))

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

font_size = 150

font = pygame.font.Font(None, font_size)

file_path = "todisplay.txt"

def wrap_text(text, font, max_width):
    lines = text.split('\n')
    wrapped_lines = []
    for line in lines:
        words = line.split(' ')
        current_line = ''
        for word in words:
            test_line = f"{current_line} {word}".strip()
            test_surface = font.render(test_line, True, (255, 255, 255))
            if test_surface.get_width() > max_width-10:
                if current_line:
                    wrapped_lines.append(current_line)
                current_line = word
            else:
                current_line = test_line
        if current_line:
            wrapped_lines.append(current_line)
        
    return wrapped_lines

def read_translation():
	if os.path.exists(file_path):
		with open(file_path, 'r') as file:
			return file.read()[-70:]
	return ""

text_display = "Hello World"

running = True
while running:
	new_text = read_translation()
	text_display = new_text

	screen.fill(BLACK)
	y=50
	wrapped_lines = wrap_text(text_display, font, 1024)
	for line in wrapped_lines:
		text_surface = font.render(line, True, WHITE)
		screen.blit(text_surface, (50, y))
		y+=(font_size//1.5)

	pygame.display.flip()

	for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        running = False

               # if event.type == pygame.FINGERDOWN:
                       # insidetext = "hi :3" 
	time.sleep(0.5)

pygame.quit()
