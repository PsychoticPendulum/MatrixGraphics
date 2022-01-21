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

class Birb:
	x = Screen.w - int(Screen.w / 4)
	y = int(Screen.h / 4)
	dy = 1
	health = 4

class Pipe:
	gap = 4
	x = 0
	yt = 0
	ht = random.randint(4,8)
	yb = ht + gap
	hb = Screen.h - gap - ht
	c = (0,240,0)

def set_pipe():
	Pipe.ht = random.randint(4,8)
	Pipe.yb = Pipe.ht + Pipe.gap
	Pipe.hb = Screen.h - Pipe.gap - Pipe.ht

def update():
	if Birb.dy < 2:
		Birb.dy += 1
	
	if Pipe.x > int(Screen.w / 4) or Birb.y >= Screen.h - int(Screen.h / 8):
		if Birb.y >= Pipe.yb - Pipe.gap / 2 and Birb.dy >= 0:
			Birb.dy = -1
	Birb.y += Birb.dy
	Pipe.x += 1

	if Birb.x == Pipe.x:
		if Birb.y > Pipe.ht and Birb.y < Pipe.yb:
			Pipe.c = (0,240,240)
		else:
			Birb.health -= 1
			Pipe.c = (240,0,0)
	else:
		Pipe.c = (0,240,0)

	if Pipe.x >= Screen.w:
		Pipe.x = 0
		set_pipe()

def render():
	Pixel.flush()
	
	draw_box(6,1,4,1,(240,0,0))
	for i in range(Birb.health):
		draw_box(Screen.w - 7 - i,1,1,1,(0,240,0))

	draw_box(Pipe.x, Pipe.yt, 1, Pipe.ht,Pipe.c) 
	draw_box(Pipe.x, Pipe.yb, 1, Pipe.hb,Pipe.c) 
	draw_box(Birb.x, Birb.y, 1, 1, (240,240,0))

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
			
			if Birb.health == 0:
				lost()

	except Exception:
		print("Oh no :(")
		traceback.print_exc()
	finally:
		flush()
		quit()

def sad_face(tear):
	Pixel.flush()
	draw_box(3, Screen.h - 6, 10, 1, (240,0,0))
	draw_box(3, Screen.h - 5, 1, 1, (240,0,0))
	draw_box(Screen.w - 4, Screen.h - 5, 1, 1, (240,0,0))
	draw_box(3,3,3,3,(240,0,0))
	draw_box(Screen.w-6,3,3,3,(240,0,0))
	if tear < Screen.h - 5:
		draw_box(5, tear - 1, 1, 1, (0,240,240))
	Pixel.display()

def lost():
	tear = 6
	for i in range(5):
		sad_face(tear)
		tear += 1
		time.sleep(00.55)
	sad_face(14)
	time.sleep(1)
	Birb.health = 4

if __name__ == "__main__":
	main()

