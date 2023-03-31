import sys

import glfw
import numpy as np
import moderngl as mgl

from config import *
from shader_program import ShaderProgram

# ----------------------------------------------------------------------------------------------------------------------

class App:

    def __init__(self, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT):

        self.screen_width  = screen_width
        self.screen_height = screen_height

        #
        self.lastTime = time.time()
        self.currentTime = time.time()
        self.numFrames = 0
        self.frameTime = 0

        self.fps = FPSCounter()

        #
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        self.window = glfw.create_window(self.screen_width, self.screen_height, "", None, None)
        glfw.make_context_current(self.window)

        # no vsync
        glfw.swap_interval(0)

        # OpenGL context / options
        self.ctx = mgl.create_context()
        #self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)

        # load shaders
        all_shaders = ShaderProgram(self.ctx)
        self.program = all_shaders.programs['default']

        # -1, 1, 0 ------------ 1, 1, 0
        #     |                    |
        #     |                    |
        #     |                    |
        #     |                    |
        # -1, -1, 0 ----------- 1, -1, 0

        # x, y, z,  r, g, b, a
        vertex_data = ( 1.0, -1.0, 0.0,   1.0, 0.0, 0.0, 1.0, # bottom right
                        -1.0, -1.0, 0.0,  0.0, 1.0, 0.0, 1.0, # bottom left
                        0.0, 1.0, 0.0,    0.0, 0.0, 1.0, 1.0  # top middle
                    )
        vertex_data = np.array(vertex_data, dtype=np.float32)

        self.vbo = self.ctx.buffer(vertex_data) #self.vbo = self.ctx.buffer(vertex_data.tobytes())
        self.vao = self.ctx.vertex_array(self.program, [(self.vbo, '3f 4f', 'vertexPosition', 'vertexColor')])

        # uniforms
        #self.set_uniform('u_resolution', (self.screen_width, self.screen_height))
        #self.set_uniform('u_mouse', (0, 0))

    def destroy(self):
        self.vbo.release()
        self.program.release()
        self.vao.release()

    def set_uniform(self, u_name, u_value):
        try:
            self.program[u_name] = u_value
        except KeyError:
            pass
        
    def get_fps_old(self):
        self.currentTime = time.time()
        delta = self.currentTime - self.lastTime

        if delta >= 1:

            framerate = max(1, int(self.numFrames // delta))
            glfw.set_window_title(self.window, f"FPS: {framerate:3.0f}")

            self.lastTime = self.currentTime
            self.numFrames = -1
            self.frameTime = 1000.0 / framerate

        self.numFrames += 1

    def get_fps(self):
        self.currentTime = time.time()
        delta = self.currentTime - self.lastTime

        if delta >= 1:

            fps = f"GLFW FPS: {self.fps.get_fps():3.0f}"
            glfw.set_window_title(self.window, fps)

            self.lastTime = self.currentTime

        self.fps.tick()

    def run(self):

        while not glfw.window_should_close(self.window):

            self.ctx.clear(0.0, 0.0, 0.0)
            self.vao.render()
            
            glfw.poll_events()
            glfw.swap_buffers(self.window)
                
            self.get_fps()

        glfw.terminate()

# ----------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    if not glfw.init():
        sys.exit()

    app = App()
    app.run()

