# Crest

## History

In 1792 the german mathematician Frederick Weiß studied what he called "movement goemetries", or the goemetry resulting from the relative movements of a point on a Cartesian plane. Centuries later, a programming language you may have heard of was made based on his works. That language, called Logo, is what gave the name to Weiß's point: the "turtle". The programming language detailed here, on the other hand, is much more faithful to Weiß's original vision of how to use a turtle. Thus it has been named Crest, a kind of really, really old fashioned logo. (Although really crests were from before Weiß's time.) Unfortunately this is all made up, but it makes for a fun story.

## The Language

Crest is a Logo-based esolang with a turtle starting in the middle of the screen, facing up (an angle of 0°). It has a 600x600 screen that serves both as the only way to output, but also as the entire program memory, as there are no variables. Because the screen is 600 pixels wide, it was chosen that the pixels could only hold a number from 0-599, each corresponding to a color.

You can tell what color a number corresponds to by decomposing its digits:
- The last digit is the red channel
- The middle digit is the green channel
- The first digit is theh blue channel

The first digit, being the blue channel, has fewer possible values. The number for each color then gets mapped to the range 0-255. For example:
- 0 is #000000
- 599 is #ffffff
- 9 is #ff0000
- 122 is #393933

The screen starts out all white, filled by 599s.

### To Run Crest

The interpreter is `crest.py`, which is used like so: `python ./crest.py <crest_file> <options>`. The options are:
- `fps=<n>` to make Crest run at that fps. The default is 30.
- `debug` to enable the `debug <number>` command that prints that number. By default the command is a noop.
- `keycodes` to print the keycode of each key you press (this is relating to [input](#input)).
- `ast` to print out the parsed ast.

The interpreter depends on two packages: pygame and lark. Both are available from pip under those same names.

### Syntax

The syntax is very simple; commands are written with the arguments afterwards, blocks use `[]`, just like Logo, and comments go from `;` to the end of the line. For example:

```
left 90

forever [
	; Fetch the input pixel
	setpos 599 399
	setpencolor pixel
	
	; Completely fill the screen
	repeat 600 [
		forward 599
		setpos 599 minus ycor 1
	]
	
	nextframe
]
```

### The Commands

#### Turtle Commands

- `forward <distance>` moves the turtle in the direction its facing that many pixels. Moving draws a line to the screen.
- `back <distance>` is the same as `forward` but in the opposite direction.
- `left <degrees>` rotates the turtle that many degrees to the left.
- `right <degrees>` is the same as `left` but in the opposite direction.
- `setpos <x> <y>` moves the turtle to that position.
- `setheading <degrees>` sets the turtle's rotation to that angle, with 0° being up.
- `showturtle` shows where the turtle is. The turtle starts hidden.
- `hideturtle` hides where the turtle is.

#### Turtle Expressions
- `xcor` returns the turtle's x coordinate.
- `ycor` returns the turtle's y coordinate.
- `heading` returns the turtle's rotation.
- `pixel` returns the color of the pixel the turtle is on.
- `shownp` return 1 if the turtle is being shown, 0 otherwise.

#### Pen Commands

- `setpencolor <color>` makes the turtle start painting in that color. The starting color is 0.
- `penup` "lifts the pen up", making it so that the turtle doesn't draw anymore when it moves.  The pen starts down.
- `pendown` "puts the pen back down".

#### Pen Expressions
- `pencolor` returns the pen's color.
- `pendownp` returns 1 if the pen is down, 0 otherwise.

#### Reset Commands

- `home` resets the turtle's position and rotation.
- `clean` resets the entire screen.
- `clearscreen` resets both.

#### Math Expressions

- `true` returns 1.
- `false` returns 0.
- `and <number> <number>` returns 1 if both its arguments are nonzero, 0 otherwise.
- `or <number> <number>` returns 1 if either of its arguments are nonzero, 0 otherwise.
- `not <number>` returns 1 if its argument is zero, 0 otherwise.
- `equal <number> <number>` returns 1 if its arguments are equal, 0 otherwise.
- `lessthan <number> <number>` returns 1 if its first argument is less than the second, 0 otherwise.
- `morethan <number> <number>` is the same as `lessthan`, but check for the first argument being more than the second.
- `plus <number> <number>` returns the sum of its arguments.
- `minus <number> <number>` returns the first arguments minus the second.

Numbers can be any int or float value, but when they're stored as the pen's color (likely to save the value on the screen), they're rounded and moduloed by 600 so the pen's color is always valid. The rounding is done to the nearest integer. On the other hand, the turtle's position and rotation have no limits to what numbers they can be. But be careful, reading a pixel from the screen out of bounds will crash the program.

#### Control Flow Commands

- `if <condition> <block>` will the run the block if the condition is nonzero.
- `ifelse <condition> <block> <block>` is the same as `if` but it will run the second block if the condition is `0`.
- `repeat <number> <block>` will run the block that many times.
- `forever <block>` will run the block forever.
- `while <condition> <block>` will run the block until the condition is `0`, reevaluating the condition each time.

#### Time Commands

- `nextframe` will make the screen render immediately, instead of waiting for a frame to pass as the program normally does. Then it will wait for the current frame to finish before resuming the program.

Crest tries to always runs at a set fps, which is by default 30.

### Input

Crest can read keyboard input; when you press down a key, that key's code is put in the bottom-rightmost pixel. When a key is released, if none are currently pressed, that pixel becomes white (599). You can run the interpreter with `keycodes` after the file name to make the program print the keycode when you press a key.

All keys that have ascii characters, have that number as their code. But be careful, the enter key corresponds to the carriage feed character (13), not newline. There are no keys for shifted versions of keys.

Here is a table of some of the other keycodes, because all would be [far, *far* too many](https://www.freepascal-meets-sdl.net/sdl-2-0-key-code-lookup-table/):

| Key | Code |
| --- | --- |
| Backspace | 8 |
| Tab | 9 |
| Enter | 13 |
| Escape | 27 |
| Delete | 127 |
| Caps Lock | 128 |
| F1 | 129 |
| F2 | 130 |
| F3 | 131 |
| F4 | 132 |
| F5 | 133 |
| F6 | 134 |
| F7 | 135 |
| F8 | 136 |
| F9 | 137 |
| F10 | 138 |
| F11 | 139 |
| F12 | 140 |
| Print Screen | 141 |
| Scroll Lock | 142 |
| Pause | 143 |
| Insert | 144 |
| Home | 145 |
| Page Up | 146 |
| End | 148 |
| Page Down | 149 |
| Right Arrow | 150 |
| Left Arrow | 151 |
| Down Arrow | 152 |
| Up Arrow | 153 |
| Num Lock | 154 |
| Application (The menu key) | 172 |
| Left Control | 295 |
| Left Shift | 296 |
| Left Alt | 297 |
| Left Super (The Windows or command key) | 298 |
| Right Control | 299 |
| Right Shift | 300 |
| Right Alt | 301 |
| Right Super | 302 |

## Examples

### `circle.crest` - Draw a Circle

This program draws a circle by slowly rotating the turtle as it moves.

```
penup
setpos 100 300
pendown

forever [
	forward 1
	right 0.25
]
```

### `artist.crest` - Turtle Draws a Star

This program animates the turtle drawing a star over and over. This is done by repeatedly calling `nextframe` to wait a certain amount of time.

```
showturtle

forever [
	clearscreen
	repeat 15 [ nextframe ]
	left 144

	repeat 5 [
		right 144
		forward 100
		repeat 15 [ nextframe ]
	]
	
	repeat 15 [ nextframe ]
]
```

### `palette.crest` - The Color Palette

This program draws all 600 colors to the screen.

```
setpos 0 0

repeat 600 [
	back 599
	setpencolor plus pencolor 1
	penup
	setpos plus xcor 1 0
	pendown
]
```

### `key colors.crest` - Key Colors

This program reads the user input pixel and fills the screen with that color.

```
left 90

forever [
	penup
	setpos 599 599
	pendown
	
	setpencolor pixel
	repeat 600 [
		forward 599
		setpos 599 minus ycor 1
	]
	nextframe
]
```

### `color picker.crest` - Color Picker

This program lets you enter a three digit number from 0-599, one digit at a time (make sure to have no keys pressed to let the program know to move to the next digit). It then displays that number as a color on the screen. Error inputting digits will make the program fill the screen with red. After the screen fill with a color, press enter to reset it.

The input is taken by waiting for the input pixel to change.

```
right 90

forever [
	penup
	setpos 599 599
	pendown
	
	while equal pixel 599 [ nextframe ]
	
	ifelse or
		lessthan pixel 48
		morethan pixel 53
	[
		setpencolor 9
	] [
		setpencolor minus pixel 48
		back 1
		repeat 99 [ setpencolor plus pencolor pixel ]
		forward 1
		
		while not equal pixel 599 [ nextframe ]
		while equal pixel 599 [ nextframe ]
		
		ifelse or
			lessthan pixel 48
			morethan pixel 57
		[
			setpencolor 9
		] [
			setpencolor minus pixel 48
			penup
			back 2
			pendown
			back 0
			repeat 9 [ setpencolor plus pencolor pixel ]
			penup
			forward 1
			setpencolor plus pencolor pixel
			pendown
			forward 1
			
			while not equal pixel 599 [ nextframe ]
			while equal pixel 599 [ nextframe ]
			
			ifelse or
				lessthan pixel 48
				morethan pixel 57
			[
				setpencolor 9
			] [
				setpencolor plus
					pencolor
					minus pixel 48
			]
		]
	]
	
	clean
	setpos 0 0
	repeat 600 [
		forward 599
		setpos 0 plus ycor 1
	]
	
	setpos 599 599
	while not equal pixel 13 [ nextframe ]
	while not equal pixel 599 [ nextframe ]
	clean
]
```

### `walk.crest` - Walking Simulator

This program lets you press the arrow keys to move the turtle around.

It works by always putting the turtle where it needs to be right before calling `nextframe`. The position and rotation are stored in the 3 pixels next to the input. You can even see them change as you move if you look closely enough!

```
showturtle

penup
setpos 596 599
pendown
right 90

setpencolor 90
forward 1
setpencolor 300
forward 1

forever [
	penup
	setpos 599 599
	setheading 90
	
	if equal pixel 150 [
		setpos 596 599
		setpencolor 90
		pendown
		forward 0
		
		penup
		setpos 597 599
		setpencolor plus pixel 8
		pendown
		forward 0
	]
	if equal pixel 151 [
		setpos 596 599
		setpencolor 270
		pendown
		forward 0
		
		penup
		setpos 597 599
		setpencolor minus pixel 8
		pendown
		forward 0
	]
	if equal pixel 152 [
		setpos 596 599
		setpencolor 180
		pendown
		forward 0
		
		penup
		setpos 598 599
		setpencolor plus pixel 8
		pendown
		forward 0
	]
	if equal pixel 153 [
		setpos 596 599
		setpencolor 0
		pendown
		forward 0
		
		penup
		setpos 598 599
		setpencolor minus pixel 8
		pendown
		forward 0
	]
	
	penup
	setpos 596 599
	setheading pixel
	
	setpos 597 599
	setpencolor pixel
	setpos 598 599
	setpos pencolor pixel
	
	nextframe
]
```

### `cantor.crest` - The Cantor Set

This program draws the cantor set fractal with some rounding errors.

```
penup
setpos 0 0
pendown

setpencolor 1
back 0

penup
setpos 1 0
pendown

setpencolor 100
back 1
setpencolor 400
back 0

penup
setpos 0 0
pendown

setheading 90
while lessthan pixel 128 [
	penup
	setpos pixel 0
	
	setpencolor pixel
	while not equal pixel 599 [ forward 1 ]
	pendown
	forward 0
	
	penup
	setpos 0 0
	setpos pixel 1
	
	setpencolor pixel
	setpos xcor 2
	
	pendown
	forward 0
	setpencolor 0
	while lessthan
		plus plus pencolor pencolor pencolor
		pixel
	[
		setpencolor plus pencolor 1
	]
	setpencolor minus pencolor 1
	forward 0
	
	penup
	setpos xcor 1
	while not equal pixel 599 [ forward 1 ]
	pendown
	forward 1
	
	penup
	setpos 0 0
	setpos pixel 0
	
	setpencolor pixel
	setpos xcor 2
	setpencolor plus plus pencolor pixel pixel
	
	setpos xcor 0
	while not equal pixel 599 [ forward 1 ]
	pendown
	forward 0
	
	penup
	setpos 0 0
	setpencolor plus pixel 1
	pendown
	forward 0
]

penup
setpos 0 1
pendown

setpencolor 1
back 0

while lessthan pixel 128 [
	penup
	setpos pixel 1
	
	setpencolor pixel
	setpos xcor 0
	setpos pixel plus 2 3
	setheading 180
	while not equal pixel 599 [ forward 2 ]
	
	setheading 90
	pendown
	forward 0
	setpencolor 0
	forward pixel
	
	penup
	setpos 0 1
	setpencolor plus pixel 1
	pendown
	forward 0
]
```