#! /usr/bin/env python3

from rpi_ws281x import *
import time
import datetime
import traceback
import sys
import random
import enum
import math

class Module:
	pin = 18
	row = 16
	col = 16
	count = row * col

strip = Adafruit_NeoPixel(Module.count, Module.pin, 800000, 10, False, 6, 0)
strip.begin()

class Screen:
	w = Module.col
	h = Module.row
	s = w * h
	p = [[0]*3]*s

class Pixel:
	x = 0
	y = 0
	c = (255,0,0)
	def set(r,g,b):
		Pixel.x = abs(Pixel.x)
		Pixel.y = abs(Pixel.y)
		pos =  Pixel.x + ((Pixel.y % Screen.w) * Screen.w)
		if Pixel.y % 2:
			pos = (Pixel.y + 1)* Module.col - Pixel.x - 1

		# print("({:d},{:d}) -> {:d}".format(Pixel.x,Pixel.y,pos))
		Screen.p[abs(pos)] = (r,g,b)

	def display():
		for i in range(Module.count):
			strip.setPixelColor(i, Color(Screen.p[i][0], Screen.p[i][1], Screen.p[i][2]))
		strip.show()

	def flush():
		for i in range(Screen.s):
			Screen.p[i] = (0,0,0)


def flush():
	for i in range(Module.count):
		strip.setPixelColor(i, Color(0,0,0))
	strip.show()

def draw_box(x,y,w,h,c):
	for i in range(x,x+w):
		for j in range(y,y+h):
			Pixel.x = i
			Pixel.y = j
			Pixel.set(c[0],c[1],c[2])

def delay(fps,t,dt):
	frame = (dt - t) / fps
	time.sleep(frame * 0.75)

def timestamp():
    return int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)

#	################
#	##### Game #####
#	################

def get_distance(x1,y1,x2,y2):
	xdst = x1-x2
	ydst = y1-y2
	return math.sqrt(xdst*xdst+ydst-ydst)

def get_color(m,v,r,g,b):
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

class Colors:
	r = 240
	g = 64
	b = 0

class Snek:
	x = 5
	y = 5
	xset = False
	yset = False
	delta = 4
	r = 0
	g = 240
	b = 0

class Body:
	def __init__(self,x,y,r,g,b):
		self.x = x
		self.y = y
		self.lastx = x
		self.lasty = y
		self.r = r
		self.g = g
		self.b = b
	x = 0
	y = 0
	lastx = 0
	lasty = 0
	index = 4
	moved = False
	r = 0
	g = 240
	b = 0

parts = []
for i in range(Body.index):
	Colors.r,Colors.g,Colors.b = get_color(240,4,Colors.r,Colors.g,Colors.b)
	parts.append(Body(Snek.x, Snek.y-1-i,Colors.r,Colors.g,Colors.b))

def is_blocked(x,y):
	for i in range(Body.index):
		if parts[i].x == x and parts[i].y == y:
			return True
	return False

def get_apple_pos():
	x = random.randint(4, Screen.w-4)
	y = random.randint(4, Screen.h-4)
	while is_blocked(x, y):
		x = random.randint(4, Screen.w-4)
		y = random.randint(4, Screen.h-4)
	return x,y

class Apple:
	x,y = get_apple_pos()	

def get_new_pos(x,y):
	backfire = False
	if Snek.delta == 4:
		backfire = True
	if Snek.delta == 1:
		if not is_blocked(Snek.x+1,Snek.y):
			return Snek.x+1,Snek.y
		Snek.delta = 2
	if Snek.delta == 2:
		if not is_blocked(Snek.x-1,Snek.y):
			return Snek.x-1,Snek.y
		Snek.delta = 3
	if Snek.delta == 3:
		if not is_blocked(Snek.x,Snek.y-1):
			return Snek.x,Snek.y-1
		Snek.delta = 4
	if Snek.delta == 4:
		if not is_blocked(Snek.x,Snek.y+1):
			return Snek.x,Snek.y+1
	if not backfire:
		return Snek.x,Snek.y+1
	return Snek.x+1,Snek.y

def update():
	for part in parts:
		part.moved = True

	if Snek.x == Apple.x and Snek.y == Apple.y:
		Apple.x, Apple.y = get_apple_pos()
		Colors.r,Colors.g,Colors.b = get_color(240,4,Colors.r,Colors.g,Colors.b)
		parts.append(Body(parts[Body.index-1].x,parts[Body.index-1].y,Colors.r,Colors.g,Colors.b))
		Body.index += 1
		Snek.xset = False
		Snek.yset = False

	for i in reversed(range(Body.index)):
		if not parts[i].moved:
			continue
		if i > 0:
			parts[i].x = parts[i-1].lastx
			parts[i].y = parts[i-1].lasty
		else:
			parts[i].x = Snek.x
			parts[i].y = Snek.y
		parts[i].lastx = parts[i].x
		parts[i].lasty = parts[i].y

	if random.randint(1,6) == 3 and Snek.xset == False and Snek.yset == False:
		if Snek.delta == 1 or Snek.delta == 2:
			Snek.delta = random.choice([3,4])
		else:
			Snek.delta = random.choice([1,2])

	if not Snek.xset and Snek.x == Apple.x and abs(Snek.y - Apple.y) < 3:
		if Snek.y > Apple.y:
			Snek.delta = 3
		else:
			Snek.delta = 4
		Snek.yset = True
	if not Snek.yset and Snek.y == Apple.y and abs(Snek.x - Apple.x) < 5:
		if Snek.x > Apple.x:
			Snek.delta = 2
		else:
			Snek.delta = 1


	#if Snek.delta == 1:
	#	Snek.x += 1
	#elif Snek.delta == 2:
	#	Snek.x -= 1
	#elif Snek.delta == 3:
	#	Snek.y -= 1
	#else:
	#	Snek.y += 1

	Snek.x,Snek.y = get_new_pos(Snek.x,Snek.y)

	if Snek.x > Screen.w-1:
		Snek.x = 0
	elif Snek.x < 0:
		Snek.x = Screen.w-1
	if Snek.y > Screen.h-1:
		Snek.y = 0
	elif Snek.y < 0:
		Snek.y = Screen.h-1
	
def render():
	Pixel.flush()


	for i in reversed(range(Body.index)):
		draw_box(parts[i].x,parts[i].y,1,1,(parts[i].r,parts[i].g,parts[i].b))

	draw_box(Apple.x, Apple.y, 1, 1, (Snek.g,Snek.b,Snek.r))
#	draw_box(Apple.x + 1, Apple.y, 1, 1, (240,240,240))
#	draw_box(Apple.x, Apple.y + 1, 1, 1, (240,240,240))
#	draw_box(Apple.x - 1, Apple.y, 1, 1, (240,240,240))
#	draw_box(Apple.x, Apple.y - 1, 1, 1, (240,240,240))
	
	draw_box(Snek.x, Snek.y, 1, 1, (Snek.r,Snek.g,Snek.b))

	Pixel.display()

def main():
	frames = 0
	try:
		while True:
			frames += 1
			t = timestamp()
			
			update()
			render()
		
			dt = timestamp()
			delay(90, t, dt)
	except Exception:
		print("Oh no :(")
		traceback.print_exc()
	finally:
		flush()
		quit()

if __name__ == "__main__":
	main()

