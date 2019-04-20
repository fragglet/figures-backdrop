
from __future__ import print_function, generators, division

from PIL import Image
from math import sqrt

import sys

CAMERA_POS = (0.5, -2.5, 1.0)
BEZIER_POINTS = ((0, 0), (0.5, 2.0), (1.0, 0))
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

curve = bezier(*BEZIER_POINTS)
curve_len = curve_length(curve)

im = Image.open(sys.argv[1])
im = im.convert(mode='RGBA')
backdrop = Image.new('RGBA', (
	int(im.width * curve_len),
	im.height,
))

for bx, t in enumerate(make_ts(curve, curve_len, backdrop.width)):
	wx, wy = curve(t)
	for by in range(backdrop.height):
		wz = 1.0 - float(by) / backdrop.height
		pt = project_to_plane(CAMERA_POS, (wx, wy, wz))
		ix = int(pt[0] * im.width)
		iy = im.height - int(pt[2] * im.height)
		p = im.getpixel((ix, iy))
		backdrop.putpixel((bx, by), p)

backdrop.save('backdrop.png')
