#! /usr/bin python3

# |-------------------------------------------------------------------------|
# |  ____                 _     _      ____                        _        |
# | |  _ \ ___ _   _  ___| |__ (_) ___|  _ \ ___ _ __   __ _ _   _(_)_ __   |
# | | |_) / __| | | |/ __| '_ \| |/ __| |_) / _ \ '_ \ / _` | | | | | '_ \  |
# | |  __/\__ \ |_| | (__| | | | | (__|  __/  __/ | | | (_| | |_| | | | | | |
# | |_|   |___/\__, |\___|_| |_|_|\___|_|   \___|_| |_|\__, |\__,_|_|_| |_| |
# |           |___/                                   |___/                 |
# |-------------------------------------------------------------------------| 

# |> Raspberry Pi 1 B+, Raspberry Pi 1 A+, Raspberry Pi 2, Raspberry Pi Zero, Raspberry Pi Zero W
# |> Raspberry Pi 3, Raspberry Pi 3 B+, Raspberry Pi 3 A+, Raspberry Pi 4, Raspberry Pi 400

# |-----------------------------------------------------------------------------------------------------------------------|
# | 39. | 37. | 35. | 33. | 31. | 29. | 27. | 25. | 23. | 21. | 19. | 17. | 15. | 13. | 11. | 09. | 07. | 05. | 03. | 01. |
# |-----------------------------------------------------------------------------------------------------------------------|
# | 40. | 38. | 36. | 34. | 32. | 30. | 28. | 26. | 24. | 22. | 20. | 18. | 16. | 14. | 12. | 10. | 08. | 06. | 04. | 02. |
# |-----------------------------------------------------------------------------------------------------------------------|
# |-----------------------------------------------------------------------------------------------------------------------|
# | GND | G26 | G19 | G13 | G06 | G05 | DNC | GND | G11 | G09 | G10 | ~3V | G22 | G27 | G17 | GND | G04 | G03 | G02 | ~3V |
# |-----------------------------------------------------------------------------------------------------------------------|
# | G21 | G20 | G16 | GND | G12 | GND | DNC | G07 | G08 | G25 | GND | G24 | G23 | GND | G18 | G15 | G14 | GND | ~5V | ~5V |
# |-----------------------------------------------------------------------------------------------------------------------|

from rpi_ws281x import *
import random
import time
import os

class Module:
	running = True
	count = 256
	pin = 18
	mode = 0
	speed = 50 
	seed = 24

class LED:
	def __init__(self, id, r, g, b):
		self.id = id
		self.r = r
		self.g = g
		self.b = b
	id = 0
	r = 0
	g = 0
	b = 0

#	------------
#	--- INIT ---
#	------------

strip = Adafruit_NeoPixel(Module.count, Module.pin, 800000, 10, False, 24, 0)
strip.begin()
led_strip = []
bg_led_strip = []

def flush():
	print("Flushing LEDs ... ", end="")
	for i in range(Module.count):
		led_strip[i].r = 0 
		led_strip[i].g = 0
		led_strip[i].b = 0 
	print("Done")

def init_mode():
	r = 240
	g = 0
	b = 0

	#	Static
	if Module.mode == 0:
		prompt = input(">>> ")
		color = prompt.split()
		for i in range(2):
			if int(color[i]) > 240:
				color[i] = "240"
			elif int(color[i]) < 0:
				color[i] = "0"
		for i in range(Module.count):
			led_strip[i].r = int(color[0])
			led_strip[i].g = int(color[1])
			led_strip[i].b = int(color[2])
	#	Fading
	elif Module.mode == 1:
		print("Setting Mode 1 ... ", end="")
		for i in range(Module.count):
			led_strip[i].r = 240
			led_strip[i].g = 0
			led_strip[i].b = 0
		print("Done")
		print("Mode:	Fading")
	#	Rainbow
	elif Module.mode == 2:
		print("Setting Mode 2 ... ", end="")
		for i in range(Module.count):
			r,g,b = cycle(r,g,b,Module.seed,240)
			led_strip[i].r = r
			led_strip[i].g = g
			led_strip[i].b = b
		print("Done")
		print("Mode:	Rainbow")
	#	Ice
	elif Module.mode == 3:
		print("Setting mode 3 ... ", end="")
		r = 0
		g = 240
		b = 240
		v = Module.seed
		w = 0
		for i in range(Module.count):
			if w == 0:
				if g > 0:
					g -= v
				else:
					r += v
					if r == 240:
						w = 1
			else:
				if r > 0:
					r -= v
				else:
					g += v
					if g == 240:
						w = 0
			led_strip[i].r = r
			led_strip[i].g = g
			led_strip[i].b = b
		print("Done")
		print("Mode:	Ice")
	#	Chase
	elif Module.mode == 4:
		print("Setting mode 4 ... ", end="")
		copy()
		flush()
		for i in range(Module.count):
			if i % 18 == 0:
				for j in range(6):
					led_strip[i-j].r = bg_led_strip[i-j].r
					led_strip[i-j].g = bg_led_strip[i-j].g
					led_strip[i-j].b = bg_led_strip[i-j].b
		print("Done")
		print("Mode:	Chase")
	# Lamp
	elif Module.mode == 5:
		print("Setting mode 5 ...", end="")
		r = 255
		g = 255
		b = 128
		for i in range(Module.count):
			led_strip[i].r = r
			led_strip[i].g = g
			led_strip[i].b = b
		print("Done")
		print("Mode:	Lamp")
	elif Module.mode == 6:
		print("Setting mode 6 ...", end="")
		for i in range(Module.count):
			led_strip[i].r = r
			led_strip[i].g = g
			led_strip[i].b = b
		print("Done")
		print("Mode:	Hunt")
	else:
		invalid_input(Module.mode)
	sep()

def init():
	print("Initializing Module ... ", end="")
	# Fill led_strip array with LED objects
	for i in range(Module.count):
		led_strip.append(LED(i, 0,0,255))
		bg_led_strip.append(LED(i,255,0,255))
	

	Module.mode = 2
	init_mode()
	for i in range(Module.count):
		strip.setPixelColor(i, Color(led_strip[i].r, led_strip[i].g, led_strip[i].b))
		strip.show()
	print("Done")


#	------------
#	--- CMDS ---
#	------------

def translate_mode(cypher):
	if cypher == "manual":
		return 0
	elif cypher == "fade":
		return 1
	elif cypher == "rainbow":
		return 2
	elif cypher == "ice":
		return 3
	elif cypher == "chase":
		return 4
	elif cypher == "lamp":
		return 5
	elif cypher == "hunt":
		return 6
	return -1

def prompt():
	while True:
		cmd = input(">> ")
		if cmd == "exit":
			Module.running = False
			break
		elif cmd == "help":
			help("help")
			break
		elif cmd == "mode":
			help("mode")
			break
		elif "mode " in cmd:
			mode = cmd.split()
			try:
				Module.mode = int(mode[1])
				init_mode()
			except:
				Module.mode = translate_mode(mode[1])
				if Module.mode > -1: 
					init_mode()
				else:
					invalid_input(mode[1])
			break
		elif "bright" in cmd:
			bright = cmd.split()
			try:
				strip.setBrightness(int(bright[1]))
			except:
				invalid_input(bright[1])
			sep()
			break
		elif "speed" in cmd:
			speed = cmd.split()
			try:
				Module.speed = 100 - int(speed[1])
				if Module.speed < 0:
					Module.speed = 0
			except:
				invalid_input(speed[1])
			sep()
			break
		elif "seed" in cmd:
			seed = cmd.split()
			try:
				Module.seed = int(seed[1])
			except:
				invalid_input(seed[1])
			sep()
			break

def poweroff():
	sep()
	print("Poweroff ...")
	for i in range(Module.count):
		strip.setPixelColor(Module.count - 1 - i, Color(0,0,0))
		strip.show()
	sep()

def help(type):
	sep()
	if (type == "help"):
		print("->	exit")	
		print("->	bright [val]")
		print("->	speed [val]")
		print("->	seed [val]")
	elif (type == "mode"):
		print("0	manual")
		print("1	fade")
		print("2	rainbow")
		print("3	ice")
		print("4	chase")
		print("5	lamp")
		print("6	hunt")
	sep()

def sep():
	os.system("sep")

#	------------
#	--- SHOW ---
#	------------

def copy():
	for i in range(Module.count):
		if i == 0:
			bg_led_strip[i].r = led_strip[Module.count-1].r
			bg_led_strip[i].g = led_strip[Module.count-1].g
			bg_led_strip[i].b = led_strip[Module.count-1].b
		else:
			bg_led_strip[i].r = led_strip[i-1].r
			bg_led_strip[i].g = led_strip[i-1].g
			bg_led_strip[i].b = led_strip[i-1].b

def move():
	if Module.speed == 100:
		return
	copy()
	for i in range(Module.count):
		if i == 0:
			led_strip[i].r = bg_led_strip[Module.count-1].r
			led_strip[i].g = bg_led_strip[Module.count-1].g
			led_strip[i].b = bg_led_strip[Module.count-1].b
		else:
			led_strip[i].r = bg_led_strip[i-1].r
			led_strip[i].g = bg_led_strip[i-1].g
			led_strip[i].b = bg_led_strip[i-1].b

def cycle(r,g,b,v,m):
	if r == m and b == 0:
		g += v
	if g == m and r > 0:
		r -= v
	if g == m and r == 0:
		b += v
	if b == m and g > 0:
		g -= v
	if b == m and g == 0:
		r += v
	if r == m and b > 0:
		b -= v
	return r,g,b

def show():
	# FADING
	if Module.mode == 1:
		for i in range(Module.count):
			led_strip[i].r, led_strip[i].g, led_strip[i].b = cycle(led_strip[i].r, led_strip[i].g, led_strip[i].b, 1, 240)
	elif Module.mode == 6:
		for i in range(Module.count):
			strip.setPixelColor(i, Color(led_strip[i].r, led_strip[i].g, led_strip[i].b))
			strip.show
		return
	else:
		move()
	# SET LEDS		
	for i in range(Module.count):
		strip.setPixelColor(i, Color(led_strip[i].r, led_strip[i].g, led_strip[i].b))
	strip.show()

#	-----------
#	--- MSG ---
#	-----------

def invalid_input(input):
	print("ERROR: Invalid Input ", input)
	sep()

def main():
	init()

	while Module.running:
		try:
			show()
			time.sleep(Module.speed / 386)
		except KeyboardInterrupt:
			prompt()
	poweroff()

if __name__ == "__main__":
	main()
