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
	start: cmd*
	
	cmd: ARITY_0_CMD
		| ARITY_1_CMD expr
		| ARITY_2_CMD expr expr
		
		| "if" expr block -> if_
		| "ifelse" expr block block -> ifelse
		| "repeat" expr block -> repeat
		| "forever" block -> forever
		| "while" expr block -> while_
	
	expr: number
		| ARITY_0_EXPR
		| ARITY_1_EXPR expr
		| ARITY_2_EXPR expr expr
	
	ARITY_0_CMD: /pendown|penup|home|clean|clearscreen|showturtle|hideturtle|nextframe/
	ARITY_1_CMD: /forward|back|left|right|setpencolor|setheading|debug/
	ARITY_2_CMD: /setpos/
	
	ARITY_0_EXPR: /heading|pixel|xcor|ycor|pendownp|pencolor|shownp|true|false/
	ARITY_1_EXPR: /not/
	ARITY_2_EXPR: /and|or|equal|lessthan|morethan|plus|minus/
	
	?number: SIGNED_FLOAT -> float
		| SIGNED_INT -> int
	
	block: LEFT_SQUARE_BRACKET cmd* RIGHT_SQUARE_BRACKET
	LEFT_SQUARE_BRACKET: "["
	RIGHT_SQUARE_BRACKET: "]"
	
	%ignore WS
	
	%import common.SIGNED_INT
	%import common.SIGNED_FLOAT
	%import common.WS""")

class transformer(lark.Transformer):
	start = lambda self, ls: list(ls)
	cmd = start
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
	return (
		map_to_byte(color % 10, 9),
		map_to_byte(color // 10 % 10, 9),
		map_to_byte(color // 100, 5))

def rgb_to_color(rgb):
	return (
		100 * map_from_byte(rgb[2], 5)
		+ 10 * map_from_byte(rgb[1], 9)
		+ map_from_byte(rgb[0], 9))

def map_to_byte(n, max):
	return round(n * 255 / max)

def map_from_byte(n, max):
	return round(n * max / 255)

white = color_to_rgb(599)

window_width = 600
window_height = 600
window = (window_width, window_height)

fps_opts = [int(s[4:]) for s in options if s.startswith("fps=")]
fps = 30 if not fps_opts else fps_opts[0]

debug = "debug" in options

turtle_pos = (window_width / 2, window_height / 2)
turtle_angle = 0
is_turtle_shown = False
pen_color = color_to_rgb(0)
is_pen_down = True
next_frame = False

time_since_started_frame = 0

def run_block(block):
	for cmd in block:
		res = run_cmd(cmd)
		
		if should_render():
			yield
		
		if isinstance(res, types.GeneratorType):
			for _ in res:
				if should_render():
					yield
	
	yield

def run_cmd(cmd):
	global turtle_pos
	global turtle_angle
	global is_turtle_shown
	global pen_color
	global is_pen_down
	global next_frame
	
	cmd_name = cmd[0]
	# Turtle Commands
	if cmd_name == "forward":
		dist = run_expr(cmd[1])
		rad = deg_to_rad(turtle_angle)
		new_turtle_pos = (
			turtle_pos[0] + math.cos(rad) * dist,
			turtle_pos[1] + math.sin(rad) * dist)
		move_to(new_turtle_pos)
	elif cmd_name == "back":
		dist = -run_expr(cmd[1])
		rad = deg_to_rad(turtle_angle)
		new_turtle_pos = (
			turtle_pos[0] + math.cos(rad) * dist,
			turtle_pos[1] + math.sin(rad) * dist)
		move_to(new_turtle_pos)
	elif cmd_name == "left":
		turtle_angle -= run_expr(cmd[1])
	elif cmd_name == "right":
		turtle_angle += run_expr(cmd[1])
	elif cmd_name == "setpos":
		move_to((run_expr(cmd[1]), run_expr(cmd[2])))
	elif cmd_name == "setheading":
		turtle_angle = run_expr(cmd[1])
	elif cmd_name == "showturtle":
		is_turtle_shown = True
	elif cmd_name == "hideturtle":
		is_turtle_shown = False
	# Pen Commands
	elif cmd_name == "setpencolor":
		pen_color = color_to_rgb(round(run_expr(cmd[1])) % 600)
	elif cmd_name == "penup":
		is_pen_down = False
	elif cmd_name == "pendown":
		is_pen_down = True
	# Reset Commands
	elif cmd_name == "home":
		turtle_pos = (window_width / 2, window_height / 2)
		turtle_angle = 0
	elif cmd_name == "clean":
		memory.fill(white)
	elif cmd_name == "clearscreen":
		turtle_pos = (window_width / 2, window_height / 2)
		turtle_angle = 0
		memory.fill(white)
	# Control Flow Commands
	elif cmd_name == "if":
		def gen():
			if run_expr(cmd[1]):
				for _ in run_block(cmd[2]):
					yield
		return gen()
	elif cmd_name == "ifelse":
		def gen():
			branch = cmd[2] if run_expr(cmd[1]) else cmd[3]
			for _ in run_block(branch):
				yield
		return gen()
	elif cmd_name == "repeat":
		def gen():
			for _ in range(run_expr(cmd[1])):
				for _ in run_block(cmd[2]):
					yield
		return gen()
	elif cmd_name == "forever":
		def gen():
			while True:
				for _ in run_block(cmd[1]):
					yield
		return gen()
	elif cmd_name == "while":
		def gen():
			while run_expr(cmd[1]):
				for _ in run_block(cmd[2]):
					yield
		return gen()
	# Time Commands
	elif cmd_name == "nextframe":
		next_frame = True
	# SeCrEt CoMmAnDs OoOoOo
	elif cmd_name == "debug":
		if debug:
			print(run_expr(cmd[1]))

def run_expr(expr):
	expr_name = expr[0]
	if (
			isinstance(expr_name, int)
			or isinstance(expr_name, float)):
		return expr_name
	# Turtle Expressions
	elif expr_name == "xcor":
		return turtle_pos[0]
	elif expr_name == "ycor":
		return turtle_pos[1]
	elif expr_name == "heading":
		return turtle_angle
	elif expr_name == "pixel":
		return rgb_to_color(memory.get_at(round_pos(turtle_pos)))
	elif expr_name == "shownp":
		return int(is_turtle_shown)
	# Pen Expressions
	elif expr_name == "pendownp":
		return int(is_pen_down)
	elif expr_name == "pencolor":
		return rgb_to_color(pen_color)
	# Math Expressions
	elif expr_name == "true":
		return 1
	elif expr_name == "false":
		return 0
	elif expr_name == "and":
		return int(run_expr(expr[1]) and run_expr(expr[2]))
	elif expr_name == "or":
		return int(run_expr(expr[1]) or run_expr(expr[2]))
	elif expr_name == "not":
		return int(not run_expr(expr[1]))
	elif expr_name == "equal":
		return int(run_expr(expr[1]) == run_expr(expr[2]))
	elif expr_name == "lessthan":
		return int(run_expr(expr[1]) < run_expr(expr[2]))
	elif expr_name == "morethan":
		return int(run_expr(expr[1]) > run_expr(expr[2]))
	elif expr_name == "plus":
		return run_expr(expr[1]) + run_expr(expr[2])
	elif expr_name == "minus":
		return run_expr(expr[1]) - run_expr(expr[2])

def should_render():
	return (
		pygame.time.get_ticks() - time_since_started_frame >= 1000/fps
		or next_frame)

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
memory.fill(white)

turtle_opts = [s[7:] for s in options if s.startswith("turtle=")]
turtle = pygame.image.load("turtle.png" if not turtle_opts else turtle_opts[0])

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
				memory.set_at((599, 599), white)
		elif event.type == pygame.QUIT:
			done = True
	
	try:
		time_since_started_frame = pygame.time.get_ticks()
		next_frame = False
		next(runner)
		
		screen.blit(memory, (0, 0))
		if is_turtle_shown:
			rotated_turtle = pygame.transform.rotate(turtle, -turtle_angle)
			screen.blit(rotated_turtle, (
				round(turtle_pos[0]) - rotated_turtle.get_width() / 2,
				round(turtle_pos[1]) - rotated_turtle.get_height() / 2))
		
		pygame.display.flip()
	except StopIteration:
		pass
	
	clock.tick(fps)