import pygame as pg
import numpy as np
import sys

from OpenGL.GL.shaders import compileProgram,compileShader
from OpenGL.GL import *

from config import *
from shader_program import ShaderProgram

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

        pg.event.set_grab(False)
        pg.mouse.set_visible(True)

        self.u_scroll = 5.0  # mouse

        # time objects
        self.clock = pg.time.Clock()
        self.time = 0
        self.delta_time = 0
        self.num_frames = 0

        # load shaders
        all_shaders = ShaderProgram()

        self.program = all_shaders.programs['default']

        # -1, 1, 0 ------------ 1, 1, 0
        #     |                    |
        #     |                    |
        #     |                    |
        #     |                    |
        # -1, -1, 0 ----------- 1, -1, 0

        # x, y, z,  r, g, b, a
        vertex_data = (1.0, -1.0, 0.0, 1.0, 0.0, 0.0,  # bottom right
                       -1.0, -1.0, 0.0, 0.0, 1.0, 0.0,  # bottom left
                       0.0, 1.0, 0.0, 0.0, 0.0, 1.0  # top middle
                       )

        vertex_data = np.array(vertex_data, dtype=np.float32)

        self.vertex_count = 3

        # VBO
        self.vbo = glGenBuffers(1)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

        # VAO
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # vertexPos, location = 0
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))

        # vertexColor, location = 1
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

        # uniforms
        self.set_uniform('u_resolution', (self.screen_width, self.screen_height))
        self.set_uniform('u_mouse', (0, 0))

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1,(self.vbo,))
        glDeleteProgram(self.program)

        pg.quit()

    # TODO
    def set_uniform(self, u_name, u_value):
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

        for event in pg.event.get():

            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.destroy()
                pg.quit()
                sys.exit()

            if event.type == pg.MOUSEMOTION:
                x, y = pg.mouse.get_pos()
                dx, dy = pg.mouse.get_rel()
                self.mouse_pos(x, y, dx, dy)

            if event.type == pg.MOUSEWHEEL:  # which, flipped, x, y, touch, precise_x, precise_y
                self.mouse_scroll(event.x, event.y)

    def mouse_pos(self, x, y, dx, dy):
        self.set_uniform('u_mouse', (x, y))

    def mouse_scroll(self, x, y):
        self.u_scroll = max(1.0, self.u_scroll + y)
        self.set_uniform('u_scroll', self.u_scroll)

    # main loop
    def run(self):

        glClearColor(0.1, 0.2, 0.2, 1)

        while True:
            self.num_frames += 1

            self.get_time()

            self.check_events()

            self.set_uniform('u_time', pg.time.get_ticks() * 0.001)
            self.set_uniform('u_frames', self.num_frames)

            glClear(GL_COLOR_BUFFER_BIT)
            glUseProgram(self.program)

            #draw the triangle
            glBindVertexArray(self.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

            pg.display.flip()

            self.delta_time = self.clock.tick(MAX_FPS)

            self.get_fps()

# -----------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app = App()
    app.run()

