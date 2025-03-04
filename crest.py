import sys
import math
import types
import lark

if len(sys.argv) < 2:
	print("Please provide a file.")
	exit()

if len(sys.argv) > 2:
	options = sys.argv[2].split(",")
else:
	options = []

# Only print pygame message if file was provided
import pygame

with open(sys.argv[1]) as file:
	prog = file.read()

grammar = lark.Lark(r"""
	start: stmt*
	
	stmt: ARITY_0_STMT
		| ARITY_1_STMT expr
		| ARITY_2_STMT expr expr
		
		| "if" expr block -> if_
		| "ifelse" expr block block -> ifelse
		| "repeat" expr block -> repeat
		| "forever" block -> forever
		| "while" expr block -> while_
	
	expr: number
		| ARITY_0_EXPR
		| ARITY_1_EXPR expr
		| ARITY_2_EXPR expr expr
	
	ARITY_0_STMT: /pendown|penup|home|clean|clearscreen|showturtle|hideturtle|nextframe/
	ARITY_1_STMT: /forward|back|left|right|setpencolor|setheading|debug/
	ARITY_2_STMT: /setpos/
	
	ARITY_0_EXPR: /heading|pixel|xcor|ycor|pendownp|pencolor|shownp|true|false/
	ARITY_1_EXPR: /not/
	ARITY_2_EXPR: /and|or|equal|lessthan|morethan|plus|minus/
	
	?number: SIGNED_FLOAT -> float
		| SIGNED_INT -> int
	
	block: LEFT_SQUARE_BRACKET stmt* RIGHT_SQUARE_BRACKET
	LEFT_SQUARE_BRACKET: "["
	RIGHT_SQUARE_BRACKET: "]"
	
	%ignore WS
	
	%import common.SIGNED_INT
	%import common.SIGNED_FLOAT
	%import common.WS""")

class transformer(lark.Transformer):
	start = lambda self, ls: list(ls)
	stmt = start
	expr = start
	block = start
	if_ = lambda self, ast: ["if"] + ast
	ifelse = lambda self, ast: ["ifelse"] + ast
	repeat = lambda self, ast: ["repeat"] + ast
	forever = lambda self, ast: ["forever"] + ast
	while_ = lambda self, ast: ["while"] + ast
	int = lambda self, n: int(n[0])
	float = lambda self, n: float(n[0])

ast = transformer().transform(grammar.parse(prog))

if "ast" in options:
	print(ast)

def color_to_rgb(color):
	b, g, r = map(int, str(color).zfill(3))
	return (
		map_to_byte(r, 9),
		map_to_byte(g, 9),
		map_to_byte(b, 5)
	)

def rgb_to_color(rgb):
	return int(f"{map_from_byte(rgb[2], 5)}{map_from_byte(rgb[1], 9)}{map_from_byte(rgb[0], 9)}")

def map_to_byte(n, max):
	return round(n * 255 / max)

def map_from_byte(n, max):
	return round(n * max / 255)

window_width = 600
window_height = 600
window = (window_width, window_height)

fps_options = list(filter(
	lambda s: s.startswith("fps"), options))
if not fps_options:
	fps = 30
else:
	fps = int(fps_options[0][3:])

turtle_pos = (window_width / 2, window_height / 2)
turtle_angle = 0
is_turtle_shown = False
pen_color = color_to_rgb(0)
is_pen_down = True
next_frame = False

def run_instr(instr):
	global turtle_pos
	global turtle_angle
	global is_turtle_shown
	global pen_color
	global is_pen_down
	global next_frame
	
	instr_name = instr[0]
	if (
			isinstance(instr_name, int) or
			isinstance(instr_name, float)):
		return instr_name
	elif instr_name == "forward":
		dist = run_instr(instr[1])
		rad = deg_to_rad(turtle_angle)
		new_turtle_pos = (
			turtle_pos[0] + math.cos(rad) * dist,
			turtle_pos[1] + math.sin(rad) * dist)
		move_to(new_turtle_pos)
	elif instr_name == "back":
		dist = -run_instr(instr[1])
		rad = deg_to_rad(turtle_angle)
		new_turtle_pos = (
			turtle_pos[0] + math.cos(rad) * dist,
			turtle_pos[1] + math.sin(rad) * dist)
		move_to(new_turtle_pos)
	elif instr_name == "left":
		turtle_angle -= run_instr(instr[1])
	elif instr_name == "right":
		turtle_angle += run_instr(instr[1])
	elif instr_name == "pendown":
		is_pen_down = True
	elif instr_name == "penup":
		is_pen_down = False
	elif instr_name == "setpencolor":
		pen_color = color_to_rgb(round(run_instr(instr[1])) % 600)
	
	elif instr_name == "setpos":
		move_to((run_instr(instr[1]), run_instr(instr[2])))
	elif instr_name == "xcor":
		return turtle_pos[0]
	elif instr_name == "ycor":
		return turtle_pos[1]
	elif instr_name == "setheading":
		turtle_angle = run_instr(instr[1])
	elif instr_name == "heading":
		return turtle_angle
	elif instr_name == "pixel":
		return rgb_to_color(memory.get_at(round_pos(turtle_pos)))
	elif instr_name == "pendownp":
		return int(is_pen_down)
	elif instr_name == "pencolor":
		return rgb_to_color(pen_color)
	elif instr_name == "home":
		turtle_pos = (window_width / 2, window_height / 2)
		turtle_angle = 0
	elif instr_name == "clean":
		memory.fill((255, 255, 255))
	elif instr_name == "clearscreen":
		turtle_pos = (window_width / 2, window_height / 2)
		turtle_angle = 0
		memory.fill((255, 255, 255))
	
	elif instr_name == "showturtle":
		is_turtle_shown = True
	elif instr_name == "hideturtle":
		is_turtle_shown = False
	elif instr_name == "shownp":
		return int(is_turtle_shown)
	
	elif instr_name == "true":
		return 1
	elif instr_name == "false":
		return 0
	elif instr_name == "and":
		return int(run_instr(instr[1]) and run_instr(instr[2]))
	elif instr_name == "or":
		return int(run_instr(instr[1]) or run_instr(instr[2]))
	elif instr_name == "not":
		return int(not run_instr(instr[1]))
	elif instr_name == "equal":
		return int(run_instr(instr[1]) == run_instr(instr[2]))
	elif instr_name == "lessthan":
		return int(run_instr(instr[1]) < run_instr(instr[2]))
	elif instr_name == "morethan":
		return int(run_instr(instr[1]) > run_instr(instr[2]))
	elif instr_name == "plus":
		return run_instr(instr[1]) + run_instr(instr[2])
	elif instr_name == "minus":
		return run_instr(instr[1]) - run_instr(instr[2])
	
	elif instr_name == "if":
		def gen():
			if run_instr(instr[1]):
				for _ in run_block(instr[2]):
					yield
		return gen()
	elif instr_name == "ifelse":
		def gen():
			branch = instr[2] if run_instr(instr[1]) else instr[3]
			for _ in run_block(branch):
				yield
		return gen()
	elif instr_name == "repeat":
		def gen():
			for _ in range(run_instr(instr[1])):
				for _ in run_block(instr[2]):
					yield
		return gen()
	elif instr_name == "forever":
		def gen():
			while True:
				for _ in run_block(instr[1]):
					yield
		return gen()
	elif instr_name == "while":
		def gen():
			while run_instr(instr[1]):
				for _ in run_block(instr[2]):
					yield
		return gen()
	
	elif instr_name == "nextframe":
		next_frame = True
	
	elif instr_name == "debug":
		if "debug" in options:
			print(run_instr(instr[1]))

time_since_started_frame = 0

def run_block(block):
	for instr in block:
		res = run_instr(instr)
		
		if should_render():
			yield
		
		if isinstance(res, types.GeneratorType):
			for _ in res:
				if should_render():
					yield
	
	yield

def should_render():
	return (
		pygame.time.get_ticks() - time_since_started_frame >= 1000/fps or
		next_frame)

def move_to(pos):
	global turtle_pos
	
	if is_pen_down:
		pygame.draw.line(
			memory, pen_color,
			round_pos(turtle_pos), round_pos(pos))
	
	turtle_pos = pos

def round_pos(pos):
	return (round(pos[0]), round(pos[1]))

def deg_to_rad(deg):
	return (deg - 90) / 180 * math.pi

pygame.init()
pygame.display.set_caption("Crest")

screen = pygame.display.set_mode(window)
memory = pygame.Surface(window)
memory.fill((255, 255, 255))
truttle = pygame.image.load("truttle.png")

icon = pygame.image.load("icon.png")
pygame.display.set_icon(icon)

clock = pygame.time.Clock()

runner = run_block(ast)

done = False
while not done:
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			keycode = (
					event.key
				if event.key <= 127
					else event.key - (pygame.K_CAPSLOCK - 128))
			memory.set_at((599, 599), color_to_rgb(keycode))
			
			if "keycodes" in options:
				print(keycode)
		elif event.type == pygame.KEYUP:
			if not any(pygame.key.get_pressed()):
				memory.set_at((599, 599), color_to_rgb(599))
		elif event.type == pygame.QUIT:
			done = True
	
	try:
		time_since_started_frame = pygame.time.get_ticks()
		next_frame = False
		next(runner)
		
		screen.blit(memory, (0, 0))
		if is_turtle_shown:
			rotated_truttle = pygame.transform.rotate(truttle, -turtle_angle)
			screen.blit(rotated_truttle, (
				round(turtle_pos[0]) - rotated_truttle.get_width() / 2,
				(turtle_pos[1]) - rotated_truttle.get_height() / 2))
		
		pygame.display.flip()
	except StopIteration:
		pass
	
	clock.tick(fps)