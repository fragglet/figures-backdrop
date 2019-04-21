
from __future__ import print_function, generators, division

from PIL import Image
from math import sqrt

import sys

CAMERA_POS = (0.5, -2.5, 1.0)
BEZIER_POINTS = ((0, 0), (0.5, 1.0), (1.0, 0))
SEGMENTS = 50

def bezier(pt1, pt2, pt3):
	(x1, y1), (x2, y2), (x3, y3) = pt1, pt2, pt3
	def f(t):
		x = (1-t)*(1-t)*x1 + 2*(1-t)*t*x2 + t*t*x3
		y = (1-t)*(1-t)*y1 + 2*(1-t)*t*y2 + t*t*y3
		return (x, y)
	return f

def dist(pt1, pt2):
	(x1, y1), (x2, y2) = pt1, pt2
	dx, dy = x2 - x1, y2 - y1
	return sqrt(dx*dx + dy*dy)

def curve_length(curve):
	total = 0.0
	last_total = 0
	for i in range(SEGMENTS):
		t1 = float(i) / SEGMENTS
		t2 = float(i + 1) / SEGMENTS
		pt1, pt2 = curve(t1), curve(t2)
		total += dist(pt1, pt2)
		last_total = total
	return total

def make_ts(curve, length, npoints):
	last_t = 0
	total = 0.0
	last_pt = (0, 0)
	tolerance = 0.1 / npoints
	for i in range(1, npoints):
		want_len = float(i * length) / npoints
		min_t = last_t
		max_t = last_t + 0.1
		last_diff = 1
		while abs(last_diff) > tolerance:
			t = (min_t + max_t) / 2
			pt = curve(t)
			step = dist(pt, last_pt)
			last_diff = (total + step) - want_len
			if last_diff > 0:
				max_t = t
			else:
				min_t = t
		yield t
		total += step
		last_t = t
		last_pt = pt

def project_to_plane(pt1, pt2):
	frac = (0 - pt1[1]) / float(pt2[1] - pt1[1])
	#print("%s to %s, %f" % (pt1, pt2, frac))
	return (
		pt1[0] + frac * (pt2[0] - pt1[0]),
		pt1[1] + frac * (pt2[1] - pt1[1]),
		pt1[2] + frac * (pt2[2] - pt1[2]),
	)

def color_at_world_pt(im, wpt):
	pt = project_to_plane(CAMERA_POS, wpt)
	ix = int(pt[0] * im.width)
	iy = im.height - 1 - int(pt[2] * im.height)
	return im.getpixel((ix, iy))

def make_wall(im):
	curve = bezier(*BEZIER_POINTS)
	curve_len = curve_length(curve)
	backdrop = Image.new('RGBA', (
		int(im.width * curve_len),
		im.height,
	))

	for bx, t in enumerate(make_ts(curve, curve_len, backdrop.width)):
		wx, wy = curve(t)
		for by in range(backdrop.height):
			wz = 1.0 - float(by) / backdrop.height
			p = color_at_world_pt(im, (wx, wy, wz))
			backdrop.putpixel((bx, by), p)

	return backdrop

def make_floor(im):
	floor = Image.new('RGBA', (
		im.width,
		im.width,
	))
	for by in range(floor.height):
		wy = float(by) / im.width
		for bx in range(floor.width):
			wx = float(bx) / im.width
			p = color_at_world_pt(im, (wx, wy, 0))
			floor.putpixel((bx, floor.height - 1 - by), p)
	return floor

if len(sys.argv) != 4 or sys.argv[1] not in ("-w", "-f"):
	print("Usage: %s input.png output.png" % (sys.argv[0],))
	sys.exit(1)

im = Image.open(sys.argv[2])
im = im.convert(mode='RGBA')

if sys.argv[1] == "-w":
	out = make_wall(im)
elif sys.argv[1] == "-f":
	out = make_floor(im)

out.save(sys.argv[3])

