#!/usr/bin/python
# coding: utf-8

# Translation to Python (2.7) / PyOpenGL by hlubenow (2021).
# License: MIT

"""
------------------------YouTube-3DSage----------------------------------------
Full video: https://www.youtube.com/watch?v=gYRrGTC7GtA 
WADS to move player.

"""

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import math
import sys

# Global variables: mapX, mapY, mapS, map, window, px, py, pa, pdx, pdy.

# -----------------------------MAP----------------------------------------------
mapX = 8
mapY = 8
mapS = 64

map = ( 1,1,1,1,1,1,1,1,
        1,0,1,0,0,0,0,1,
        1,0,1,0,0,0,0,1,
        1,0,1,0,0,0,0,1,
        1,0,0,0,0,0,0,1,
        1,0,0,0,0,1,0,1,
        1,0,0,0,0,0,0,1,
        1,1,1,1,1,1,1,1 )

window = None

def drawMap2D():
    for y in range(mapY):
        for x in range(mapX):
            if map[y * mapX + x] == 1:
                glColor3f(1, 1, 1)
            else:
                glColor3f(0, 0, 0)
            xo = x * mapS
            yo = y * mapS
            glBegin(GL_QUADS)
            glVertex2f(0 + xo +1, 0 + yo + 1); 
            glVertex2f(0 + xo +1, mapS + yo - 1)
            glVertex2f(mapS + xo - 1, mapS + yo-1)
            glVertex2f(mapS + xo - 1, 0 + yo + 1) 
            glEnd()

# ------------------------PLAYER------------------------------------------------

def FixAng(a):
    if a > 359:
        a -= 360
    if a < 0:
        a += 360
    return a

px  = 0
py  = 0
pa  = 0
pdx = 0
pdy = 0


def drawPlayer2D():

    glColor3f(1, 1, 0)
    glPointSize(8)
    glLineWidth(4)
    glBegin(GL_POINTS)
    glVertex2f(px, py)
    glEnd()

    glBegin(GL_LINES)
    glVertex2f(px, py)
    glVertex2f(px + pdx * 20, py + pdy * 20)
    glEnd()


def Buttons(key, x, y):

    global px
    global py
    global pa
    global pdx
    global pdy

    if key == 'a':
        pa += 5
        pa  = FixAng(pa)
        pdx = math.cos(math.radians(pa))
        pdy = -math.sin(math.radians(pa))

    if key=='d':
        pa -= 5
        pa = FixAng(pa)
        pdx = math.cos(math.radians(pa))
        pdy = -math.sin(math.radians(pa))

    if key=='w':
        px += pdx * 5
        py += pdy * 5

    if key == 's':
        px -= pdx * 5
        py -= pdy*5

    if key == 'q':
        glutDestroyWindow(window)
        sys.exit()

    glutPostRedisplay()

# ---------------------------Draw Rays and Walls--------------------------------

def distance(ax, ay, bx, by, ang):
    return math.cos(math.radians(ang)) * (bx-ax) - math.sin(math.radians(ang)) * (by-ay)


def drawRays2D():
    glColor3f(0,1,1)
    glBegin(GL_QUADS)
    glVertex2f(526, 0)
    glVertex2f(1006,  0)
    glVertex2f(1006,160)
    glVertex2f(526,160)
    glEnd()
    glColor3f(0, 0, 1)
    glBegin(GL_QUADS)
    glVertex2f(526,160)
    glVertex2f(1006,160)
    glVertex2f(1006,320)
    glVertex2f(526,320)
    glEnd()

    ra = FixAng(pa + 30) # ray set back 30 degrees

    for r in range(60):
        # ---Vertical--- 
        dof = 0
        side = 0
        disV = 100000
        Tan = math.tan(math.radians(ra))
        if math.cos(math.radians(ra)) > 0.001:
            rx = ((int(px) >> 6) << 6) + 64
            ry = (px - rx) * Tan + py
            xo = 64
            yo = -xo * Tan # looking left
        elif math.cos(math.radians(ra)) < -0.001:
            rx = ((int(px) >> 6) << 6) - 0.0001
            ry = (px - rx) * Tan + py
            xo = -64
            yo = -xo * Tan # looking right
        else:
            rx = px
            ry = py
            dof = 8 # looking up or down. no hit  

        while dof < 8:
            mx = int(rx) >> 6
            my = int(ry) >> 6
            mp = my * mapX + mx
            if mp > 0 and mp < mapX * mapY and map[mp] == 1:
                dof=8
                disV = math.cos(math.radians(ra)) * (rx - px) - math.sin(math.radians(ra)) * (ry - py) # hit         
            else:
                rx += xo
                ry += yo
                dof += 1 # check next horizontal
        vx = rx
        vy = ry

        # ---Horizontal---
        dof = 0
        disH = 100000
        if Tan == 0:
            Tan = 100000. # Just some big number to avoid division by 0.
        else:
            Tan = 1.0 / Tan
        if math.sin(math.radians(ra)) > 0.001:
            ry = ((int(py) >> 6) << 6) - 0.0001
            rx = (py - ry) * Tan + px
            yo = -64
            xo = -yo * Tan # looking up 
        elif math.sin(math.radians(ra)) < -0.001:
            ry = ((int(py) >> 6) << 6) + 64
            rx = (py - ry) * Tan + px
            yo = 64
            xo = -yo * Tan # looking down
        else:
            rx = px
            ry = py
            dof = 8 # looking straight left or right

        while dof < 8:
            mx = int(rx) >> 6
            my = int(ry) >> 6
            mp = my * mapX + mx
            if mp > 0 and mp < mapX * mapY and map[mp] == 1:
                dof = 8
                disH = math.cos(math.radians(ra)) * (rx - px) - math.sin(math.radians(ra)) * (ry - py) # hit         
            else:
                rx += xo
                ry += yo
                dof += 1 # check next horizontal

        glColor3f(0, 0.8, 0)
        if disV < disH:
            rx = vx
            ry = vy
            disH = disV
            glColor3f(0, 0.6 ,0) # horizontal hit first
        glLineWidth(2)
        glBegin(GL_LINES)
        glVertex2f(px, py)
        glVertex2f(rx, ry)
        glEnd() # draw 2D ray

        ca = FixAng(pa - ra)
        disH = disH * math.cos(math.radians(ca)) # fix fisheye 
        lineH = int((mapS * 320) / (disH))
        if lineH > 320:
            lineH = 320 # line height and limit
        lineOff = 160 - (lineH >> 1) # line offset

        glLineWidth(8)
        glBegin(GL_LINES)
        glVertex2f(r * 8 + 530, lineOff)
        glVertex2f(r * 8 + 530, lineOff + lineH)
        glEnd() # draw vertical wall  

        ra = FixAng(ra - 1) # go to next ray

#-----------------------------------------------------------------------------

def init():
    # We need to use the "global" keyword, if we want to change
    # (or declare) a global variable inside a function.
    glClearColor(0.3, 0.3, 0.3, 0)
    gluOrtho2D(0, 1024, 510, 0)
    global px
    global py
    global pa
    global pdx
    global pdy
    px = 150
    py = 400
    pa = 90
    pdx = math.cos(math.radians(pa))
    pdy = -math.sin(math.radians(pa))


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    drawMap2D()
    drawPlayer2D()
    drawRays2D()
    glutSwapBuffers()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB);
    glutInitWindowSize(1024, 510)
    # glutInitWindowPosition(100, 50)
    global window
    window = glutCreateWindow("YouTube-3DSage")
    init()
    glutDisplayFunc(display)
    glutKeyboardFunc(Buttons)
    glutMainLoop()


main()
