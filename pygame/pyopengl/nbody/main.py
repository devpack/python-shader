import pygame as pg
import numpy as np
import sys

from OpenGL.GL.shaders import compileProgram,compileShader
from OpenGL.GL import *

import glm

from config import *
from shader_program import ShaderProgram
from camera import Camera
from model import *
import gl_utils as gl_utils

# -----------------------------------------------------------------------------------------------------------

class App:

    def __init__(self, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT):

        self.screen_width = screen_width
        self.screen_height = screen_height

        #
        print("USE_COMPUTE_SHADER=", USE_COMPUTE_SHADER)
        print("XGROUPSIZE=", XGROUPSIZE)
        print("YGROUPSIZE=", YGROUPSIZE)
        print("ZGROUPSIZE=", ZGROUPSIZE)
        print("NB_BODY=", NB_BODY)

        #
        self.lastTime = time.time()
        self.currentTime = time.time()

        self.fps = FPSCounter()

        # pygame init
        pg.init()

        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 4)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 5)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

        pg.display.set_mode((self.screen_width, self.screen_height), flags=pg.OPENGL | pg.HWSURFACE | pg.DOUBLEBUF)  # | pg.FULLSCREEN)

        gl_utils.print_gl_version()

        # camera control: keys + mouse
        pg.event.set_grab(GRAB_MOUSE)
        pg.mouse.set_visible(True)

        self.forward = False
        self.backward = False
        self.right = False
        self.left = False
        self.up = False
        self.down = False

        self.mouse_x, self.mouse_y = 0, 0
        self.mouse_button_down = False

        # time objects
        self.clock = pg.time.Clock()
        self.time = 0
        self.delta_time = 0
        self.num_frames = 0

        # load shaders
        all_shaders = ShaderProgram()
        self.nbody_program = all_shaders.get_program("nbody")

        # compute shader
        if USE_COMPUTE_SHADER:
            with open(f'shaders/nbody_cs.glsl') as file:
                compute_shader_source = file.read()

            compute_shader_source = compute_shader_source.replace("XGROUPSIZE_VAL", str(XGROUPSIZE)) \
                                                         .replace("YGROUPSIZE_VAL", str(YGROUPSIZE)) \
                                                         .replace("ZGROUPSIZE_VAL", str(ZGROUPSIZE)) \
                                                         .replace("NB_BODY_VAL", str(NB_BODY)) \

            self.compute_shader_program = compileProgram(compileShader(compute_shader_source, GL_COMPUTE_SHADER))

        # camera
        self.camera = Camera(self, fov=FOV, near=NEAR, far=FAR, position=CAM_POS, speed=SPEED, sensivity=SENSITIVITY)

        # scene object
        self.scene = []

        self.bodies = Bodies(self)
        self.scene.append(self.bodies)

    def destroy(self):
        glMemoryBarrier(GL_ALL_BARRIER_BITS)
        glDeleteProgram(self.nbody_program)

        for obj in self.scene:
            obj.destroy()

        pg.quit()

    def get_time(self):
        self.time = pg.time.get_ticks() * 0.001

    def get_fps(self):
        self.currentTime = time.time()
        delta = self.currentTime - self.lastTime

        if delta >= 1:
            fps = f"PyGame FPS: {self.fps.get_fps():3.0f}"
            pg.display.set_caption(fps)

            self.lastTime = self.currentTime

        self.fps.tick()

    def check_events(self):

        # self.up = False
        # self.down = False

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

            if event.type == pg.MOUSEMOTION:
                mouse_position = pg.mouse.get_pos()
                #self.mouse_pos(mouse_position[0], mouse_position[1])

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


    # main loop
    def run(self):

        glUseProgram(self.nbody_program)
        glClearColor(0.1, 0.2, 0.2, 1)

        while True:
            self.num_frames += 1

            self.get_time()

            self.check_events()

            glClear(GL_COLOR_BUFFER_BIT)

            glUseProgram(self.nbody_program)
            glBindVertexArray(self.bodies.vao)

            self.camera.update(self.mouse_dx, self.mouse_dy, self.forward, self.backward, self.left, self.right, self.up, self.down)

            if USE_COMPUTE_SHADER:
                glUseProgram(self.compute_shader_program)
                glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, self.bodies.bodies_ssbo)

                if NB_BODY > XGROUPSIZE:
                    glDispatchCompute(NB_BODY // XGROUPSIZE, 1, 1)
                else:
                    glDispatchCompute(1, 1, 1)

                #glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)
                glUseProgram(0)

                # wait for compute shader to finish
                gl_utils.gl_sync()

            for obj in self.scene:
                obj.update()
                obj.render()

            pg.display.flip()

            self.delta_time = self.clock.tick(MAX_FPS)

            self.get_fps()

# -----------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app = App()
    app.run()

