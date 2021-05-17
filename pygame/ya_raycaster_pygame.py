#!/usr/bin/python
# coding: utf-8

""" Yet another ray caster 1.0 - (C) 2021, hlubenow
    Python/Pygame version of the tutorial code by 3DSage
    (https://github.com/3DSage/OpenGL-Raycaster_v1)

    License: MIT
"""

import pygame

import math
import os

class Main:

    def __init__(self):
        self.player = Player(self)
        self.mapX = 8
        self.mapY = 8
        self.mapS = 64
        self.map = ( 1,1,1,1,1,1,1,1,
                     1,0,1,0,0,0,0,1,
                     1,0,1,0,0,0,0,1,
                     1,0,1,0,0,0,0,1,
                     1,0,0,0,0,0,0,1,
                     1,0,0,0,0,1,0,1,
                     1,0,0,0,0,0,0,1,
                     1,1,1,1,1,1,1,1 )

        self.draw = PygameBackend(self, (1024, 510), "YouTube-3DSage")
        self.draw.mainloop()

    def movePlayer(self, movement):
        self.player.move(movement)

    def drawMap2D(self):
        for y in range(self.mapY):
            for x in range(self.mapX):
                if self.map[y * self.mapX + x] == 1:
                    self.draw.setColor("white")
                else:
                    self.draw.setColor("black")
                xo = x * self.mapS
                yo = y * self.mapS
                self.draw.drawQuad(((0 + xo + 1, 0 + yo + 1),
                                    (0 + xo + 1, self.mapS + yo-1),
                                    (self.mapS + xo - 1, self.mapS + yo-1),
                                    (self.mapS + xo - 1, 0 + yo + 1)))

    def fixAngle(self, a):
        if a > 359:
            a -= 360
        if a < 0:
            a += 360
        return a

    def drawPlayer2D(self):
        self.draw.setColor("yellow")
        self.draw.drawPoint((self.player.x, self.player.y), 8)
        self.draw.drawLine(((self.player.x + 3, self.player.y + 3),
                           (self.player.x + 3 + self.player.dx * 20, self.player.y + 3 + self.player.dy * 20)),
                           4)

    def distance(self, ax, ay, bx, by, ang):
        return math.cos(math.radians(ang)) * (bx-ax) - math.sin(math.radians(ang)) * (by-ay)

    def drawRays2D(self):
        self.draw.setColor("turquoise")
        self.draw.drawQuad(((526, 0), (1006, 0), (1006, 160), (526, 160)))

        self.draw.setColor("blue")
        self.draw.drawQuad(((526, 160), (1006, 160), (1006, 320), (526, 320)))
        
        ra = self.fixAngle(self.player.angle + 30) # ray set back 30 degrees
 
        for r in range(60):
            # ---Vertical--- 
            dof = 0
            side = 0
            disV = 100000
            Tan = math.tan(math.radians(ra))
            if math.cos(math.radians(ra)) > 0.001:
                rx = ((int(self.player.x) >> 6) << 6) + 64
                ry = (self.player.x - rx) * Tan + self.player.y
                xo = 64
                yo = -xo * Tan # looking left
            elif math.cos(math.radians(ra)) < -0.001:
                rx = ((int(self.player.x) >> 6) << 6) - 0.0001
                ry = (self.player.x - rx) * Tan + self.player.y
                xo = -64
                yo = -xo * Tan # looking right
            else:
                rx = self.player.x
                ry = self.player.y
                dof = 8 # looking up or down. no hit  
  
            while dof < 8:
                mx = int(rx) >> 6
                my = int(ry) >> 6
                mp = my * self.mapX + mx
                if mp > 0 and mp < self.mapX * self.mapY and self.map[mp] == 1:
                    dof=8
                    disV = math.cos(math.radians(ra)) * (rx - self.player.x) - math.sin(math.radians(ra)) * (ry - self.player.y) # hit         
                else:
                    rx += xo
                    ry += yo
                    dof += 1 # check next horizontal
            vx = rx
            vy = ry
 
            # ---Horizontal---
            dof = 0
            disH = 100000
            # A division by zero also happened in the C original.
            # We avoid it here:
            if Tan == 0:
                Tan = 100000 # Just some big number.
            else:
                Tan = 1.0 / Tan
            if math.sin(math.radians(ra)) > 0.001:
                ry = ((int(self.player.y) >> 6) << 6) - 0.0001
                rx = (self.player.y - ry) * Tan + self.player.x
                yo = -64
                xo = -yo * Tan # looking up 
            elif math.sin(math.radians(ra)) < -0.001:
                ry = ((int(self.player.y) >> 6) << 6) + 64
                rx = (self.player.y - ry) * Tan + self.player.x
                yo = 64
                xo = -yo * Tan # looking down
            else:
                rx = self.player.x
                ry = self.player.y
                dof = 8 # looking straight left or right
 
            while dof < 8:
                mx = int(rx) >> 6
                my = int(ry) >> 6
                mp = my * self.mapX + mx
                if mp > 0 and mp < self.mapX * self.mapY and self.map[mp] == 1:
                    dof = 8
                    disH = math.cos(math.radians(ra)) * (rx - self.player.x) - math.sin(math.radians(ra)) * (ry - self.player.y) # hit         
                else:
                    rx += xo
                    ry += yo
                    dof += 1 # check next horizontal
  
            self.draw.setColor("green")
            if disV < disH:
                rx = vx
                ry = vy
                disH = disV
                self.draw.setColor("dark_green") # horizontal hit first
            self.draw.drawLine(((self.player.x, self.player.y), (rx, ry)), 2)

            ca = self.fixAngle(self.player.angle - ra)
            disH = disH * math.cos(math.radians(ca)) # fix fisheye 
            lineH = int((self.mapS * 320) / (disH))
            if lineH > 320:
                lineH = 320 # line height and limit
            lineOff = 160 - (lineH >> 1) # line offset
  
            # draw vertical wall:
            self.draw.drawLine(((r * 8 + 530, lineOff), (r * 8 + 530, lineOff + lineH)), 8)

            ra = self.fixAngle(ra - 1) # go to next ray


class Player:

    def __init__(self, main):
        self.main  = main
        self.x     = 150
        self.y     = 400
        self.angle = 90
        self.dx    =  math.cos(math.radians(self.angle))
        self.dy    = -math.sin(math.radians(self.angle))

    def move(self, movement):

        if movement == "turn_left":
            self.angle += 5
            self.angle =  self.main.fixAngle(self.angle)
            self.dx    =  math.cos(math.radians(self.angle))
            self.dy    = -math.sin(math.radians(self.angle))

        if movement == "turn_right":
            self.angle -= 5
            self.angle =  self.main.fixAngle(self.angle)
            self.dx    =  math.cos(math.radians(self.angle))
            self.dy    = -math.sin(math.radians(self.angle))

        if movement == "forward":
            self.x += self.dx * 5
            self.y += self.dy * 5

        if movement == "backwards":
            self.x -= self.dx * 5
            self.y -= self.dy * 5

        if movement == "strafe_left":
            self.x += self.dy * 5
            self.y -= self.dx * 5

        if movement == "strafe_right":
            self.x -= self.dy * 5
            self.y += self.dx * 5


class PygameBackend:

    def __init__(self, main, screensize, windowtitle):
        self.main = main
        # Pygame color values just seem to be OpenGL color values multiplied by 255:
        self.colors = {"black"      : (0, 0, 0),
                       "white"      : (255, 255, 255),
                       "grey"       : (76, 76, 76),
                       "yellow"     : (255, 255, 0),
                       "turquoise"  : (0, 255, 255),
                       "green"      : (0, 204, 0),
                       "dark_green" : (0, 153, 0),
                       "blue"       : (0, 0, 255)}

        self.color = None

        self.movements = { pygame.K_a      : "strafe_left",
                           pygame.K_LEFT   : "turn_left",
                           pygame.K_d      : "strafe_right",
                           pygame.K_RIGHT  : "turn_right",
                           pygame.K_w      : "forward",
                           pygame.K_UP     : "forward",
                           pygame.K_s      : "backwards",
                           pygame.K_DOWN   : "backwards",
                           pygame.K_q      : "quit",
                           pygame.K_ESCAPE : "quit"}

        os.environ['SDL_VIDEO_WINDOW_POS'] = "112, 72"
        self.screen = pygame.display.set_mode((screensize[0], screensize[1]))
        pygame.display.set_caption(windowtitle)
        pygame.init()
        self.clock = pygame.time.Clock()

    def mainloop(self):

        while True:
            self.clock.tick(50)
            self.screen.fill(self.colors["grey"])
            if self.processEvents() == "quit":
                return
            self.main.drawMap2D()
            self.main.drawPlayer2D()
            self.main.drawRays2D()
            pygame.display.flip()

    def processEvents(self):
        pygame.event.pump()
        pressed = pygame.key.get_pressed()
        for i in self.movements.keys():
            if pressed[i]:
                self.main.movePlayer(self.movements[i])
        if pressed[pygame.K_q]:
            quit()
            return "quit"
        return 0

    def setColor(self, colorname):
        self.color = self.colors[colorname]

    def drawQuad(self, points):
        rect = pygame.Rect(points[0][0],
                           points[0][1],
                           points[2][0] - points[0][0],
                           points[2][1] - points[0][1])
        pygame.draw.rect(self.screen, self.color, rect)

    def drawPoint(self, point, size):
        rect = pygame.Rect(point[0],
                           point[1],
                           size, size)
        pygame.draw.rect(self.screen, self.color, rect)

    def drawLine(self, points, linewidth):
        pygame.draw.line(self.screen, self.color, points[0], points[1], linewidth)


if __name__ == '__main__':
    Main()
