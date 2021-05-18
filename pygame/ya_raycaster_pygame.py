#!/usr/bin/python
# coding: utf-8

""" Yet another ray caster 1.1 - (C) 2021, hlubenow
    Python/Pygame version of the tutorial code by 3DSage
    (https://github.com/3DSage/OpenGL-Raycaster_v1)

    License: MIT 
"""

import pygame

import math
import os

COLORS = {"black"      : (0, 0, 0),
          "white"      : (255, 255, 255),
          "grey"       : (76, 76, 76),
          "yellow"     : (255, 255, 0),
          "bluegreen"  : (0, 255, 255),
          "green"      : (0, 204, 0),
          "dark_green" : (0, 153, 0),
          "blue"       : (0, 0, 255)}

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
        self.screen = pygame.display.set_mode((1024, 510))
        pygame.display.set_caption("YouTube-3DSage")
        pygame.init()
        self.clock = pygame.time.Clock()

        while True:
            self.clock.tick(50)
            self.screen.fill(COLORS["grey"])
            if self.processEvents() == "quit":
                break
            self.drawMap2D()
            self.drawPlayer2D()
            self.drawRays2DandScenery3D()
            pygame.display.flip()
        pygame.quit()

    def processEvents(self):
        pygame.event.pump()
        pressed = pygame.key.get_pressed()
        for i in self.movements.keys():
            if pressed[i]:
                self.player.move(self.movements[i])
        if pressed[pygame.K_q]:
            return "quit"
        return 0

    def drawMap2D(self):
        for y in range(self.mapY):
            for x in range(self.mapX):
                xo = x * self.mapS
                yo = y * self.mapS
                if self.map[y * self.mapX + x] == 1:
                    c = COLORS["white"]
                else:
                    c = COLORS["black"]
                pygame.draw.rect(self.screen,
                                 c,
                                 pygame.Rect(xo + 1,
                                             yo + 1,
                                             self.mapS - 2,
                                             self.mapS - 2))

    def fixAngle(self, a):
        if a > 359:
            a -= 360
        if a < 0:
            a += 360
        return a

    def drawPlayer2D(self):
        
        pygame.draw.rect(self.screen,
                         COLORS["yellow"],
                         pygame.Rect(self.player.x, self.player.y,
                                     8, 8))
        pygame.draw.line(self.screen,
                         COLORS["yellow"],
                         (self.player.x + 3, self.player.y + 3),
                         (self.player.x + 3 + self.player.dx * 20, self.player.y + 3 + self.player.dy * 20),
                         4)

    def distance(self, ax, ay, bx, by, ang):
        return math.cos(math.radians(ang)) * (bx-ax) - math.sin(math.radians(ang)) * (by-ay)

    def drawRays2DandScenery3D(self):

        # Sky:
        pygame.draw.rect(self.screen,
                         COLORS["bluegreen"],
                         pygame.Rect(526, 0, 480, 160))
        # Floor: 
        pygame.draw.rect(self.screen,
                         COLORS["blue"],
                         pygame.Rect(526, 160, 480, 160))

        # Ray set back 30 degrees:
        ra = self.fixAngle(self.player.angle + 30)
        for r in range(60):
            # ---Vertical--- 
            dof = 0
            side = 0
            disV = 100000
            Tan = math.tan(math.radians(ra))
            if math.cos(math.radians(ra)) > 0.001:
                # Looking left:
                rx = ((int(self.player.x) >> 6) << 6) + 64
                ry = (self.player.x - rx) * Tan + self.player.y
                xo = 64
                yo = -xo * Tan 
            elif math.cos(math.radians(ra)) < -0.001:
                # Looking right:
                rx = ((int(self.player.x) >> 6) << 6) - 0.0001
                ry = (self.player.x - rx) * Tan + self.player.y
                xo = -64
                yo = -xo * Tan 
            else:
                # Looking up or down. no hit:
                rx = self.player.x
                ry = self.player.y
                dof = 8 
  
            while dof < 8:
                mx = int(rx) >> 6
                my = int(ry) >> 6
                mp = my * self.mapX + mx
                if mp > 0 and mp < self.mapX * self.mapY and self.map[mp] == 1:
                    # Hit:
                    dof=8
                    disV = math.cos(math.radians(ra)) * (rx - self.player.x) - math.sin(math.radians(ra)) * (ry - self.player.y)
                else:
                    # Check next horizontal:
                    rx += xo
                    ry += yo
                    dof += 1
            vx = rx
            vy = ry
 
            # ---Horizontal---
            dof = 0
            disH = 100000
            if Tan == 0:
                Tan = 100000
            else:
                Tan = 1.0 / Tan
            if math.sin(math.radians(ra)) > 0.001:
                # Looking up:
                ry = ((int(self.player.y) >> 6) << 6) - 0.0001
                rx = (self.player.y - ry) * Tan + self.player.x
                yo = -64
                xo = -yo * Tan 
            elif math.sin(math.radians(ra)) < -0.001:
                # Looking down:
                ry = ((int(self.player.y) >> 6) << 6) + 64
                rx = (self.player.y - ry) * Tan + self.player.x
                yo = 64
                xo = -yo * Tan 
            else:
                # Looking straight left or right:
                rx = self.player.x
                ry = self.player.y
                dof = 8 
 
            while dof < 8:
                mx = int(rx) >> 6
                my = int(ry) >> 6
                mp = my * self.mapX + mx
                if mp > 0 and mp < self.mapX * self.mapY and self.map[mp] == 1:
                    # Hit:
                    dof = 8
                    disH = math.cos(math.radians(ra)) * (rx - self.player.x) - math.sin(math.radians(ra)) * (ry - self.player.y)
                else:
                    # Check next horizontal:
                    rx += xo
                    ry += yo
                    dof += 1 
  
            c = COLORS["green"]

            if disV < disH:
                rx = vx
                ry = vy
                disH = disV
                # Horizontal hit first:
                c = COLORS["dark_green"]

            # Draw 2D beam:
            pygame.draw.line(self.screen,
                             c,
                             (self.player.x + 3, self.player.y + 3),
                             (rx, ry),
                             2)

            ca = self.fixAngle(self.player.angle - ra)
            # Fix fish eye:
            disH = disH * math.cos(math.radians(ca))
            lineH = int((self.mapS * 320) / (disH))
            # Line height and limit:
            if lineH > 320:
                lineH = 320 
            # Line offset:
            lineOff = 160 - (lineH >> 1) 
  
            # Draw 3D walls:
            pygame.draw.line(self.screen,
                             c,
                             (r * 8 + 530, lineOff),
                             (r * 8 + 530, lineOff + lineH),
                             8)
            # Go to next ray:
            ra = self.fixAngle(ra - 1)


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


if __name__ == '__main__':
    Main()
