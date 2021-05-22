#!/usr/bin/python
# coding: utf-8

""" Yet another ray caster 2.0 - (C) 2021, hlubenow
    Python/Pygame version of the tutorial code by 3DSage
    (https://github.com/3DSage/OpenGL-Raycaster_v1)
    License: MIT 
"""

import pygame

import math
import os, sys

from mazegenerator import *

RANDOMMAZE      = True
RANDOMMAZE_SIZE = (20, 20)

JOYSTICK        = False

SHADING         = False

SHOWRAYS        = True
NUMRAYS         = 60

FPS             = 50
PI              = 3.1416
WALLSYMBOL      = "1"

COLORS = {"black"      : (0, 0, 0),
          "white"      : (255, 255, 255),
          "darkgrey"   : (76, 76, 76),
          "grey"       : (140, 140, 140),
          "lightgrey"  : (220, 220, 220),
          "bluegreen"  : (0, 255, 255),
          "skyblue"    : (0, 186, 255),
          "red"        : (204, 0, 0),
          "blue"       : (0, 0, 200)}

class Map:

    def __init__(self):

        if RANDOMMAZE:
            self.m = MazeGenerator(RANDOMMAZE_SIZE)
            self.textmap = self.m.maze

        else:

            self.textmap = ( "11111111",
                             "10100001",
                             "10100001",
                             "10100001",
                             "10000001",
                             "10000101",
                             "10000001",
                             "11111111" )

            """
            self.textmap = ( "1111111111111111",
                             "1010000110100001",
                             "1010000000100001",
                             "1010000100100001",
                             "1000000000000001",
                             "1000010010000101",
                             "1000000000000001",
                             "1000000010000001",
                             "1000000010000001",
                             "1010000110100001",
                             "1010000000100001",
                             "1010000100100001",
                             "1000000000000001",
                             "1000010010000101",
                             "1000000010000001",
                             "1111111111111111")
            """

        self.mapX = len(self.textmap[0])
        self.mapY = len(self.textmap)
        self.tilesize = 64

        self.mappart_width  = 8 * self.tilesize
        self.mappart_height = 8 * self.tilesize

        self.mappart_halfwidth  = self.mappart_width // 2
        self.mappart_halfheight = self.mappart_height // 2

        self.lastpart_x = self.mapX * self.tilesize - self.mappart_width
        self.lastpart_y = self.mapY * self.tilesize - self.mappart_height

    def createSurface(self):
        self.surface = pygame.Surface((self.mapX * self.tilesize, self.mapY * self.tilesize))
        self.surface = self.surface.convert()
        self.rect    = pygame.Rect(0, 0, self.mappart_width, self.mappart_height)
        for y in range(self.mapY):
            for x in range(self.mapX):
                xo = x * self.tilesize
                yo = y * self.tilesize
                if self.textmap[y][x] == WALLSYMBOL:
                    c = COLORS["white"]
                else:
                    c = COLORS["black"]
                pygame.draw.rect(self.surface,
                                 c,
                                 pygame.Rect(xo + 1,
                                             yo + 1,
                                             self.tilesize - 2,
                                             self.tilesize - 2))

    def move(self, player):
        self.rect.topleft = (player.x - player.drawx, player.y - player.drawy)


class TwoDimensionalWindow:

    def __init__(self, map, player):
        self.map          = map
        self.player       = player
        self.width        = 512
        self.height       = 512
        self.surface      = pygame.Surface((self.width, self.height))
        self.surface      = self.surface.convert()
        self.rect         = self.surface.get_rect()
        self.rect.topleft = (0, 0)

    def drawMapPart(self):
        self.surface.blit(self.map.surface, (0, 0), self.map.rect)

    def drawPlayer(self):
        
        pygame.draw.rect(self.surface,
                         COLORS["lightgrey"],
                         pygame.Rect(self.player.drawx, self.player.drawy,
                                     8, 8))

    def drawBeam(self):
        pygame.draw.line(self.surface,
                         COLORS["red"],
                         (self.player.drawx + 3, self.player.drawy + 3),
                         (self.player.drawx + 3 + self.player.dx * 20, self.player.drawy + 3 + self.player.dy * 20),
                         4)

    def drawRay(self, color, rx, ry):
        if not SHOWRAYS:
            return
        pygame.draw.line(self.surface,
                         color,
                         (self.player.drawx + 3, self.player.drawy + 3),
                         (self.player.drawx + rx - self.player.x,
                          self.player.drawy + ry - self.player.y),
                         2)

    def draw(self, surface):
        surface.blit(self.surface, (0, 0), self.rect)


class ThreeDimensionalWindow:

    def __init__(self):
        self.width        = 480
        self.height       = 320
        self.wallwidth    = 8
        self.surface      = pygame.Surface((self.width, self.height))
        self.surface      = self.surface.convert()
        self.rect         = self.surface.get_rect()
        self.rect.topleft = (530, 0)

    def drawBackground(self):

        # Sky:
        pygame.draw.rect(self.surface,
                         COLORS["skyblue"],
                         pygame.Rect(0, 0, self.width, self.height / 2))
        # Floor: 
        pygame.draw.rect(self.surface,
                         COLORS["blue"],
                         pygame.Rect(0, self.height / 2, self.width, self.height / 2))


    def drawWallRay(self, color, r, lineOff, lineH):
        pygame.draw.line(self.surface,
                         color,
                         (r * self.wallwidth, lineOff),
                         (r * self.wallwidth, lineOff + lineH),
                         self.wallwidth)

    def draw(self, surface):
        surface.blit(self.surface, self.rect)


class Main:

    def __init__(self):

        self.map = Map()
        
        self.keystates = {}
        for i in (pygame.K_a, pygame.K_LEFT, pygame.K_d, pygame.K_RIGHT,
                  pygame.K_w, pygame.K_UP, pygame.K_s, pygame.K_DOWN,
                  pygame.K_q, pygame.K_ESCAPE):
            self.keystates[i] = False

        if JOYSTICK:
            self.joystickstates = {}
            for i in ("left", "right", "up", "down", "firing"):
                self.joystickstates[i] = False

        os.environ['SDL_VIDEO_WINDOW_POS'] = "112, 72"
        self.screen = pygame.display.set_mode((1024, 510))
        pygame.display.set_caption("Yet another raycaster")
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        self.map.createSurface()

        if JOYSTICK:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        self.sounds = {}
        self.sounds["wallhit"] = pygame.mixer.Sound("sound/wallhit.wav")
        self.player = Player(self.map, self.sounds)
        self.d2window = TwoDimensionalWindow(self.map, self.player)
        self.d3window = ThreeDimensionalWindow()
        self.clock = pygame.time.Clock()

        while True:
            self.clock.tick(FPS)
            self.screen.fill(COLORS["darkgrey"])
            if self.processEvents() == "quit":
                break
            self.d2window.drawMapPart()
            self.d2window.drawPlayer()
            self.drawRays2DandScenery3D()
            self.d2window.drawBeam()
            self.d2window.draw(self.screen)
            self.d3window.draw(self.screen)
            pygame.display.flip()
        pygame.quit()

    def processEvents(self):

        for event in pygame.event.get():

            if event.type == pygame.KEYDOWN:
                for i in self.keystates:
                    if event.key == i:
                        self.keystates[i] = True

            if event.type == pygame.KEYUP:
                for i in self.keystates:
                    if event.key == i:
                        self.keystates[i] = False

            if JOYSTICK:

                if event.type == pygame.JOYBUTTONDOWN:
                    self.joystickstates["firing"] = True

                if event.type == pygame.JOYBUTTONUP:
                    self.joystickstates["firing"] = False

                if event.type == pygame.JOYAXISMOTION:

                    # Joystick pushed:
                    if event.axis == 0 and int(event.value) == -1:
                        self.joystickstates["left"] = True
                    if event.axis == 0 and int(event.value) == 1:
                        self.joystickstates["right"] = True
                    if event.axis == 1 and int(event.value) == -1:
                        self.joystickstates["up"] = True
                    if event.axis == 1 and int(event.value) == 1:
                        self.joystickstates["down"] = True

                    # Joystick released:
                    if event.axis == 0 and int(event.value) == 0:
                        self.joystickstates["left"] = False
                        self.joystickstates["right"] = False

                    if event.axis == 1 and int(event.value) == 0:
                        self.joystickstates["up"] = False
                        self.joystickstates["down"] = False

        if self.keystates[pygame.K_q] or self.keystates[pygame.K_ESCAPE]:
            return "quit"
        if self.keystates[pygame.K_a]:
            self.player.move("strafe_left")
        if self.keystates[pygame.K_d]:
            self.player.move("strafe_right")
        if self.keystates[pygame.K_LEFT]:
            self.player.move("turn_left")
        if self.keystates[pygame.K_RIGHT]:
            self.player.move("turn_right")
        if self.keystates[pygame.K_UP] or self.keystates[pygame.K_w]:
            self.player.move("forward")
        if self.keystates[pygame.K_DOWN] or self.keystates[pygame.K_s]:
            self.player.move("backwards")

        if JOYSTICK:
            if self.joystickstates["firing"]:
                self.player.setSpeed("fast")
            else:
                self.player.setSpeed("normal")
            if self.joystickstates["left"]:
                self.player.move("turn_left")
            if self.joystickstates["right"]:
                self.player.move("turn_right")
            if self.joystickstates["up"]:
                self.player.move("forward")
            if self.joystickstates["down"]:
                self.player.move("backwards")

        return 0

    def fixAngle(self, a):
        if a > 2 * PI:
            a -=  2 * PI
        if a < 0:
            a +=  2 * PI
        return a

    def distance(self, ax, ay, bx, by, ang):
        return math.cos(ang) * (bx-ax) - math.sin(ang) * (by-ay)

    def drawRays2DandScenery3D(self):

        self.d3window.drawBackground()

        if NUMRAYS == 1:
            ray_angle = self.player.angle
        else:
            # Ray set back 30 degrees:
            ray_angle = self.fixAngle(self.player.angle + PI / 6)
        for r in range(NUMRAYS):
            # ---Vertical--- 
            dof = 0
            side = 0
            disV = 100000
            Tan = math.tan(ray_angle)
            if math.cos(ray_angle) > 0.001:
                # Looking left:
                rx = ((int(self.player.x) // self.map.tilesize) * self.map.tilesize) + self.map.tilesize
                ry = (self.player.x - rx) * Tan + self.player.y
                xo = self.map.tilesize
                yo = -xo * Tan 
            elif math.cos(ray_angle) < -0.001:
                # Looking right:
                rx = ((int(self.player.x) // self.map.tilesize) * self.map.tilesize) - 0.0001
                ry = (self.player.x - rx) * Tan + self.player.y
                xo = -self.map.tilesize
                yo = -xo * Tan 
            else:
                # Looking up or down. no hit:
                rx = self.player.x
                ry = self.player.y
                dof = 8 
  
            while dof < 8:
                mx = int(rx) // self.map.tilesize
                my = int(ry) // self.map.tilesize
                if mx >= 0 and mx < self.map.mapX and my >= 0 and my < self.map.mapY and self.map.textmap[my][mx] == WALLSYMBOL:
                    # Hit:
                    dof  = 8
                    disV = math.cos(ray_angle) * (rx - self.player.x) - math.sin(ray_angle) * (ry - self.player.y)
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
            if math.sin(ray_angle) > 0.001:
                # Looking up:
                ry = ((int(self.player.y) // self.map.tilesize) * self.map.tilesize) - 0.0001
                rx = (self.player.y - ry) * Tan + self.player.x
                yo = -self.map.tilesize
                xo = -yo * Tan 
            elif math.sin(ray_angle) < -0.001:
                # Looking down:
                # ry = ((int(self.player.y) // self.map.tilesize) * self.map.tilesize) + self.map.tilesize
                ry = ((int(self.player.y) // self.map.tilesize) * self.map.tilesize) + self.map.tilesize
                rx = (self.player.y - ry) * Tan + self.player.x
                yo = self.map.tilesize
                xo = -yo * Tan 
            else:
                # Looking straight left or right:
                rx = self.player.x
                ry = self.player.y
                dof = 8 
 
            while dof < 8:
                mx = int(rx) // self.map.tilesize
                my = int(ry) // self.map.tilesize
                if mx >= 0 and mx < self.map.mapX and my >= 0 and my < self.map.mapY and self.map.textmap[my][mx] == WALLSYMBOL:
                    # Hit:
                    dof = 8
                    disH = math.cos(ray_angle) * (rx - self.player.x) - math.sin(ray_angle) * (ry - self.player.y)
                else:
                    # Check next horizontal:
                    rx += xo
                    ry += yo
                    dof += 1 
  
            if NUMRAYS == 1:
                beamcolor = COLORS["red"]
            else:
                beamcolor = COLORS["bluegreen"]

            if not SHADING:
                wallcolor = COLORS["lightgrey"]

            if disV < disH:
                rx = vx
                ry = vy
                disH = disV
                # Horizontal hit first:
                if not SHADING:
                    wallcolor = COLORS["grey"]
                beamcolor = COLORS["skyblue"]

            # Draw 2D beam:

            self.d2window.drawRay(beamcolor, rx, ry)

            ca = self.fixAngle(self.player.angle - ray_angle)
            # Fix fish eye:
            disH = disH * math.cos(ca)
            lineH = int((self.map.tilesize * 320) / (disH))
            # Line height and limit:
            if lineH > 320:
                lineH = 320 
            # Line offset:
            lineOff = 160 - (lineH // 2)

            if SHADING:
                # Simple but effective shading code from:
                # https://github.com/StanislavPetrovV/Raycasting-3d-game-tutorial
                c = 255 / (1 + disH * disH * 0.00002)
                wallcolor = (c, c, c)
  
            # Draw 3D walls:
            self.d3window.drawWallRay(wallcolor, r, lineOff, lineH)

            # Go to next ray:
            ray_angle = self.fixAngle(ray_angle - math.radians(1))

class Player:

    def __init__(self, map, sounds):
        self.map    = map
        self.sounds = sounds
        if RANDOMMAZE:
            self.putPlayerInEntrance()
        else:
            self.x = 96
            self.y = 96
            self.drawx  = self.x
            self.drawy  = self.y
        # Init position: Facing down (270 degrees)
        self.angle  = 1.5 * PI
        self.dx     =  math.cos(self.angle)
        self.dy     = -math.sin(self.angle)
        self.speed = 5
        self.check  = []
        self.destination = []
        self.soundplayed = 0

    def getMapPosition(self):
        return (int(self.x // self.map.tilesize),
                int(self.y // self.map.tilesize))

    def putPlayerInEntrance(self):
        xs = 0
        for i in self.map.textmap[1]:
            if i == "s":
                break
            xs += 1
        self.x = xs * self.map.tilesize + self.map.tilesize / 2
        self.y = self.map.tilesize * 1.5
        self.setDrawCoordinates()
        self.map.move(self)

    def setSpeed(self, description):
        if description == "normal":
            self.speed = 5
        else:
            self.speed = 10

    def fixAngle(self, a):
        if a > 2 * PI:
            a -=  2 * PI
        if a < 0:
            a +=  2 * PI
        return a

    def setDrawCoordinates(self):

        if self.x < self.map.mappart_halfwidth:
            self.drawx = self.x

        elif self.x >= self.map.mappart_halfwidth and self.x < self.map.lastpart_x + self.map.mappart_halfwidth:
            self.drawx = self.map.mappart_halfwidth
        else:
            self.drawx = self.x - self.map.lastpart_x

        if self.y < self.map.mappart_halfheight:
            self.drawy = self.y

        elif self.y >= self.map.mappart_halfheight and self.y < self.map.lastpart_y + self.map.mappart_halfheight:
            self.drawy = self.map.mappart_halfheight
        else:
            self.drawy = self.y - self.map.lastpart_y

    def checkAndMove(self):

        if self.soundplayed > 0:
            self.soundplayed += 1
            if self.soundplayed >= 30:
                self.soundplayed = 0

        if self.map.textmap[int(self.check[1]) // self.map.tilesize][int(self.check[0]) // self.map.tilesize] == WALLSYMBOL:
            if self.soundplayed == 0:
                self.sounds["wallhit"].play()
                self.soundplayed = 1
            return
        else:
            self.x = self.destination[0]
            self.y = self.destination[1]
            self.setDrawCoordinates()
            self.map.move(self)
            # Player is in the map row, where there's only field "e":
            if RANDOMMAZE:
                if int(self.y // self.map.tilesize) == self.map.mapY - 2:
                    print "Exit found!"

    def move(self, movement):

        if movement == "turn_left":
            self.angle += math.radians(5)
            self.angle =  self.fixAngle(self.angle)
            self.dx    =  math.cos(self.angle)
            self.dy    = -math.sin(self.angle)

        if movement == "turn_right":
            self.angle -= math.radians(5)
            self.angle =  self.fixAngle(self.angle)
            self.dx    =  math.cos(self.angle)
            self.dy    = -math.sin(self.angle)

        if movement == "forward":
            self.check       = (self.x + self.dx * 20, self.y + self.dy * 20)
            self.destination = (self.x + self.dx * self.speed, self.y + self.dy * self.speed)
            self.checkAndMove()

        if movement == "backwards":
            self.check       = (self.x - self.dx * 20, self.y - self.dy * 20)
            self.destination = (self.x - self.dx * self.speed, self.y - self.dy * self.speed)
            self.checkAndMove()

        if movement == "strafe_left":
            self.check       = (self.x + self.dy * 20, self.y - self.dx * 20)
            self.destination = (self.x + self.dy * 5, self.y - self.dx * 5)
            self.checkAndMove()

        if movement == "strafe_right":
            self.check       = (self.x - self.dy * 20, self.y + self.dx * 20)
            self.destination = (self.x - self.dy * 5, self.y + self.dx * 5)
            self.checkAndMove()


if __name__ == '__main__':
    Main()
