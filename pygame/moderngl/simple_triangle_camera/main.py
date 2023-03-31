import pygame as pg
import numpy as np
import moderngl as mgl
import glm

import sys

MODEL = 0  # fragment: model 0 = basic, 1 = prime, 2 = cardio

from config import *
from shader_program import ShaderProgram
from camera import Camera

# -----------------------------------------------------------------------------------------------------------

class App:

    def __init__(self, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT):

        self.screen_width = screen_width
        self.screen_height = screen_height

        #
        self.lastTime = time.time()
        self.currentTime = time.time()

        self.fps = FPSCounter()

        # pygame init
        pg.init()

        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

        pg.display.set_mode((self.screen_width, self.screen_height), flags=pg.OPENGL | pg.HWSURFACE | pg.DOUBLEBUF)  # | pg.FULLSCREEN)

        # camera control: keys + mouse
        pg.event.set_grab(False)
        pg.mouse.set_visible(True)

        self.forward = False
        self.backward = False
        self.right = False
        self.left = False
        self.up = False
        self.down = False

        self.mouse_x, self.mouse_y = 0, 0
        self.mouse_button_down = False
        self.u_scroll = 5.0  # mouse

        # OpenGL context / options
        self.ctx = mgl.create_context()
        # self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)

        # time objects
        self.clock = pg.time.Clock()
        self.time = 0
        self.delta_time = 0
        self.num_frames = 0

        # load shaders
        all_shaders = ShaderProgram(self.ctx)

        if MODEL == 1:
            self.program = all_shaders.programs['test']
        else:
            self.program = all_shaders.programs['default']

        # camera
        self.camera = Camera(self, fov=FOV, near=NEAR, far=FAR, position=CAM_POSITION, speed=SPEED, sensivity=SENSITIVITY)

        # -1, 1, 0 ------------ 1, 1, 0
        #     |                    |
        #     |                    |
        #     |                    |
        #     |                    |
        # -1, -1, 0 ----------- 1, -1, 0

        # x, y, z,  r, g, b, a
        vertex_data = (1.0, -1.0, 0.0, 1.0, 0.0, 0.0, 1.0,  # bottom right
                       -1.0, -1.0, 0.0, 0.0, 1.0, 0.0, 1.0,  # bottom left
                       0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0  # top middle
                       )

        if MODEL == 1:
            vertex_data = [(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0), (-1, -1, 0), (1, 1, 0)]

        vertex_data = np.array(vertex_data, dtype=np.float32)

        self.vbo = self.ctx.buffer(vertex_data)  # self.vbo = self.ctx.buffer(vertex_data.tobytes())

        if MODEL == 1:
            self.vao = self.ctx.vertex_array(self.program, [(self.vbo, '3f', 'vertexPosition')])
        else:
            self.vao = self.ctx.vertex_array(self.program, [(self.vbo, '3f 4f', 'vertexPosition', 'vertexColor')])

        # uniforms
        self.set_uniform('u_resolution', (self.screen_width, self.screen_height))
        self.set_uniform('u_mouse', (0, 0))
        self.set_uniform('u_model', MODEL)

        self.m_model = glm.mat4()
        self.program['m_proj'].write(self.camera.m_proj)
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)

    def destroy(self):
        self.vbo.release()
        self.program.release()
        self.vao.release()

    def set_uniform(self, u_name, u_value):
        try:
            self.program[u_name] = u_value
        except KeyError:
            pass

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

            if event.type == pg.MOUSEWHEEL:  # which, flipped, x, y, touch, precise_x, precise_y
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

        # if y == 1:
        #    self.down = True
        # if y == -1:
        #    self.up = True

    #
    def render(self):
        self.ctx.clear()
        self.vao.render()
        pg.display.flip()

    #
    def update(self):
        self.set_uniform('u_time', pg.time.get_ticks() * 0.001)
        self.set_uniform('u_frames', self.num_frames)

        self.m_model = glm.rotate(self.m_model, 0.0001, glm.vec3(0, 1, 0))
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)

    #
    def run(self):
        while True:
            self.num_frames += 1

            self.get_time()

            self.check_events()
            self.camera.update(self.mouse_dx, self.mouse_dy, self.forward, self.backward, self.left, self.right, self.up, self.down)

            self.update()
            self.render()

            self.delta_time = self.clock.tick(MAX_FPS)

            self.get_fps()


# -----------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app = App()
    app.run()

