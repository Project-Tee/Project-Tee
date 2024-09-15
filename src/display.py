import pygame
import time
import os
import psutil
import signal

print("started")
pygame.init()

pygame.mouse.set_visible(False)

screen = pygame.display.set_mode((1024, 600))

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

font_size = 150

font = pygame.font.Font(None, font_size)

DISPLAY_FILE = os.path.dirname(os.path.realpath(__file__)) + "/../tmp/todisplay.txt"
LANGUAGE_CODE_FILE = os.path.dirname(os.path.realpath(__file__)) + "/../tmp/langcode.txt"

def wrap_text(text, font, max_width):
	lines = text.split('\n')
	wrapped_lines = []
	for line in lines:
		words = line.split(' ')
		current_line = ''
		for word in words:
			test_line = f"{current_line} {word}".strip()
			test_surface = font.render(test_line, True, (255, 255, 255))
			if test_surface.get_width() > (max_width-40):
				if current_line:
					wrapped_lines.append(current_line)
				current_line = word
			else:
				current_line = test_line
		if current_line:
			wrapped_lines.append(current_line)
		
	return wrapped_lines

def read_translation():
	if os.path.exists(DISPLAY_FILE):
		with open(DISPLAY_FILE, 'r') as file:
			return file.read()[-70:]
	return ""

def main():
	# clear input file
	if os.path.exists(DISPLAY_FILE):
		with open(DISPLAY_FILE, 'w') as file:
			file.write("")

	text_display = "Hello World"
	color = (0, 0, 0)
	index = 0
	running = True
	while running:
		new_text = read_translation()
		text_display = new_text

		screen.fill(color)
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

					if event.type == pygame.FINGERDOWN:
						index += 1
						color = [(0, 0, 0), (0, 0, 255), (199, 127, 0), (255, 0, 0), (125, 125, 125)][index % 5]
						for proc in psutil.process_iter():
							cmdline = proc.cmdline()
							if len(cmdline) >= 2 and "python" in cmdline[0] and "main.py" in cmdline[1]:
								print(f"Killed {proc.cmdline()}")
								os.kill(proc.pid, signal.SIGUSR1)
		time.sleep(0.5)

	pygame.quit()

if __name__ == '__main__':
	main()
