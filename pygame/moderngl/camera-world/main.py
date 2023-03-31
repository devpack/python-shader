import sys, random

import pygame as pg
import numpy as np
import moderngl as mgl
import glm

from camera import Camera
from model import *

from config import *
from shader_program import ShaderProgram
from light import Light

# -----------------------------------------------------------------------------------------------------------

class App:

    def __init__(self, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT):

        self.screen_width = screen_width
        self.screen_height = screen_height

        #
        self.lastTime = time.time()
        self.currentTime = time.time()

        self.fps = FPSCounter()

        self.mode = MODE
        
        # pygame init
        pg.init()

        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

        pg.display.set_mode((self.screen_width, self.screen_height), flags=pg.OPENGL | pg.HWSURFACE | pg.DOUBLEBUF) # | pg.FULLSCREEN)

        # camera control: keys + mouse
        pg.event.set_grab(GRAB_MOUSE)
        pg.mouse.set_visible(True)
        self.u_scroll = 5.0

        self.forward = False
        self.backward = False
        self.right = False
        self.left = False
        self.up = False
        self.down = False

        self.mouse_x, self.mouse_y = 0, 0
        self.mouse_button_down = False

        # OpenGL context / options
        self.ctx = mgl.create_context()
        
        if self.mode == mgl.POINTS:
            self.ctx.enable(mgl.PROGRAM_POINT_SIZE)
            #self.ctx.enable_only(mgl.PROGRAM_POINT_SIZE | mgl.BLEND)

        #self.ctx.wireframe = True
        #self.ctx.front_face = 'cw'
        self.ctx.enable(flags=mgl.DEPTH_TEST)
        #self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)

        # time objects
        self.clock = pg.time.Clock()
        self.time = 0
        self.delta_time = 0
        self.num_frames = 0

        # light
        self.light = Light(position=LIGHT_POS)

        self.all_shaders = ShaderProgram(self.ctx)
        self.world_program = self.all_shaders.get_program("world")

        # camera
        self.camera = Camera(self, fov=FOV, near=NEAR, far=FAR, position=CAM_POS, speed=SPEED, sensivity=SENSITIVITY)

        # scene object
        self.scene = []
        #self.scene.append( Model(self, self.world_program, pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), texture_color=(255, 0, 0)) )

        # uniforms
        self.set_uniform('u_resolution', (self.screen_width, self.screen_height))
        self.set_uniform('u_mouse', (0, 0))

    def destroy(self):
        self.all_shaders.destroy()

        for obj in self.scene:
            obj.destroy()

    def set_uniform(self, u_name, u_value):
        try:
            self.world_program[u_name] = u_value
        except KeyError:
            pass

    def get_fps(self):
        self.currentTime = time.time()
        delta = self.currentTime - self.lastTime

        if delta >= 1:
            fps = f"PyGame World FPS: {self.fps.get_fps():3.0f}"
            cam_pos = f"CamPos: {int(self.camera.position.x)}, {int(self.camera.position.y)}, {int(self.camera.position.z)}"
            pg.display.set_caption(fps + " | " + cam_pos)

            self.lastTime = self.currentTime

        self.fps.tick()

    def check_events(self):

        #self.up = False
        #self.down = False

        #
        for event in pg.event.get():

            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.destroy()
                pg.quit()
                sys.exit()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.forward = True
                if event.key == pg.K_DOWN:
                    self.backward = True
                if event.key == pg.K_RIGHT:
                    self.right = True
                if event.key == pg.K_LEFT:
                    self.left = True
                if event.key == pg.K_LCTRL:
                    self.up = True
                if event.key == pg.K_LSHIFT:
                    self.down = True
                
            if event.type == pg.KEYUP:
                if event.key == pg.K_UP:
                    self.forward = False
                if event.key == pg.K_DOWN:
                    self.backward = False
                if event.key == pg.K_RIGHT:
                    self.right = False
                if event.key == pg.K_LEFT:
                    self.left = False
                if event.key == pg.K_LCTRL:
                    self.up = False
                if event.key == pg.K_LSHIFT:
                    self.down = False
                    
            if event.type == pg.MOUSEBUTTONDOWN:
                self.mouse_button_down = True

            if event.type == pg.MOUSEBUTTONUP:
                self.mouse_button_down = False

            if event.type == pg.MOUSEWHEEL: # which, flipped, x, y, touch, precise_x, precise_y
                self.mouse_scroll(event.x, event.y)

            if event.type == pg.MOUSEMOTION:
                mouse_position = pg.mouse.get_pos()
                self.mouse_pos(mouse_position[0], mouse_position[1])

        # mouse camera control
        if self.mouse_button_down:
            mx, my = pg.mouse.get_pos()

            if self.mouse_x:
                self.mouse_dx = self.mouse_x - mx
            else:
                self.mouse_dx = 0

            if self.mouse_y:
                self.mouse_dy = self.mouse_y - my
            else:
                self.mouse_dy = 0

            self.mouse_x = mx
            self.mouse_y = my

        else:
            self.mouse_x = 0
            self.mouse_y = 0
            self.mouse_dx, self.mouse_dy = 0, 0

    def mouse_pos(self, x, y, dx=0, dy=0):
        self.set_uniform('u_mouse', (x, y))

    def mouse_scroll(self, x, y):
        self.u_scroll = max(1.0, self.u_scroll + y)
        self.set_uniform('u_scroll', self.u_scroll)
        
        #if y == 1:
        #    self.down = True
        #if y == -1:
        #    self.up = True

    #
    def render(self):
        self.ctx.clear(color = (0.1, 0.2, 0.3))

        for obj in self.scene:
            obj.update()
            obj.render()

        pg.display.flip()

    #
    def update(self):
        self.set_uniform('u_time', pg.time.get_ticks() * 0.001)
        self.set_uniform('u_frames', self.num_frames)

    def get_time(self):
        return pg.time.get_ticks() * 0.001

    def set_time(self):
        self.time = pg.time.get_ticks() * 0.001

    def is_prime(self, num):
        if num == 2 or num == 3: return True
        if num < 2 or not num % 2: return False
        for i in range(3, int(num ** 0.5 + 1), 2):
            if not num % i:
                return False
        return True

    def prime_list(self, max=3000):
        primes = []
        for x in range(1, max):
            if self.is_prime(x):
                primes.append(x)
        return primes
    #
    def run(self):

        # prime specific
        self.last_t = self.get_time()
        num = 1
        self.all_dir = ["f", "b", "l", "r", "u", "d"]
        self.dir_pair = {"f":"b", "b":"f", "l":"r", "r":"l", "u":"d", "d":"u"}
        self.cur_dir = "f"
        self.obj_z = 0
        self.obj_x = 0
        self.obj_y = 0

        self.primes = self.prime_list(max=MAX_PRIME)

        while True:
            # app.time used for object model motion
            self.set_time()


            # PRIMES
            if self.get_time() - self.last_t > 0.001:
                self.last_t = self.get_time()

                factor = 1
                if self.cur_dir == "f":
                    self.obj_z -=factor
                elif self.cur_dir == "b":
                    self.obj_z += factor
                if self.cur_dir == "l":
                    self.obj_x -=factor
                elif self.cur_dir == "r":
                    self.obj_x += factor
                if self.cur_dir == "u":
                    self.obj_y -=factor
                elif self.cur_dir == "d":
                    self.obj_y += factor

                #cube_col = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                #if self.is_prime(num):
                if num < MAX_PRIME:
                    if num in self.primes:
                        a = ["f", "b", "l", "r", "u", "d"]
                        a.remove(self.cur_dir)
                        a.remove(self.dir_pair[self.cur_dir])
                        self.cur_dir = a[random.randint(0, 3)]
                        #self.cur_dir = a[num % 6]

                        cube_col = (255, 0, 0)
                        scale = (1, 1, 1)
                    else:
                        cube_col = (0, 255, 0)
                        scale = (1, 1, 1)

                    self.scene.append(Model(self, self.world_program, pos=(self.obj_x, self.obj_y, self.obj_z), rot=(0, 0, 0), scale=scale, texture_color=cube_col))

                num += 1


            # pygame events
            self.check_events()

            self.camera.update(self.mouse_dx, self.mouse_dy, self.forward, self.backward, self.left, self.right, self.up, self.down)

            self.update()
            self.render()

            self.delta_time = self.clock.tick(0)

            self.get_fps()
            self.num_frames += 1

# -----------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app = App()
    app.run()

