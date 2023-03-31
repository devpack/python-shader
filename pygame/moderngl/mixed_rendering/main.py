import sys, random

import pygame as pg
import numpy as np
import moderngl as mgl
import glm
from array import array

from config import *
from shader_program import ShaderProgram

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

        self.mode = MODE

        self.fps = FPSCounter()

        # pygame init
        pg.init()

        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 4)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 6)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

        pg.display.set_mode((self.screen_width, self.screen_height),
                            flags=pg.OPENGL | pg.HWSURFACE | pg.DOUBLEBUF)  # | pg.FULLSCREEN)

        # pg.draw on this surface. then this surface is converted into a texture
        # then this texture is sampled2D in the FS and rendered into the screen (which is a 2 triangles  => quad)
        self.display = pg.Surface((screen_width, screen_height))

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

        # OpenGL context / options
        self.ctx = mgl.create_context()

        if self.mode == mgl.POINTS:
            self.ctx.enable_only(mgl.PROGRAM_POINT_SIZE | mgl.BLEND)

        #self.ctx.wireframe = True
        #self.ctx.front_face = 'cw'
        #self.ctx.enable(flags=mgl.DEPTH_TEST)
        #self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)
        self.ctx.enable(flags=mgl.BLEND)

        quad = [
            # pos (x, y), uv coords (x, y)
            -1.0, 1.0, 0.0, 0.0,
            1.0, 1.0, 1.0, 0.0,
            -1.0, -1.0, 0.0, 1.0,
            1.0, -1.0, 1.0, 1.0,
        ]

        quad_buffer = self.ctx.buffer(data=np.array(quad, dtype='f4'))

        self.all_shaders = ShaderProgram(self.ctx)
        self.screen_program = self.all_shaders.get_program("screen")

        self.vao = self.ctx.vertex_array(self.screen_program, [(quad_buffer, '2f 2f', 'vert', 'texcoord')])

        self.frame_tex = self.surf_to_texture(self.display)
        self.frame_tex.use(0)
        self.screen_program['tex'] = 0

        # time objects
        self.clock = pg.time.Clock()
        self.time = 0
        self.delta_time = 0
        self.num_frames = 0

        self.ctx.clear(color=(0.0, 0.0, 0.0))

    def surf_to_texture(self, surf):
        tex = self.ctx.texture(surf.get_size(), 4)
        tex.filter = (mgl.NEAREST, mgl.NEAREST)
        tex.swizzle = 'BGRA'
        # tex.write(surf.get_view('1'))
        return tex

    def destroy(self):
        self.frame_tex.release()

    def set_uniform(self, program, u_name, u_value):
        try:
            program[u_name] = u_value
        except KeyError:
            pass

    def get_fps(self):
        self.currentTime = time.time()
        delta = self.currentTime - self.lastTime

        if delta >= 1:
            fps = f"PyGame World FPS: {self.fps.get_fps():3.0f}"
            pg.display.set_caption(fps)

            self.lastTime = self.currentTime

        self.fps.tick()

    def check_events(self):

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
        pass
        #self.set_uniform(self.world_program, 'u_mouse', (x, y))

    def get_time(self):
        return pg.time.get_ticks() * 0.001

    def set_time(self):
        self.time = pg.time.get_ticks() * 0.001

    def run(self):

        while True:
            # app.time used for object model motion
            self.set_time()

            # pygame events
            self.check_events()

            #self.ctx.clear(color=(0.0, 0.0, 0.0))

            x = random.randint(0, self.screen_width - 1)
            y = random.randint(0, self.screen_height - 1)

            red = random.randint(0, 255)
            green = random.randint(0, 255)
            blue = random.randint(0, 255)

            pg.draw.circle(self.display, (red, green, blue), (x, y), 3)

            self.frame_tex.write(self.display.get_view('1'))
            #self.frame_tex.write(self.display.get_buffer())

            self.set_uniform(self.screen_program, "time", self.num_frames)

            self.vao.render(mode=self.mode) # tri strip

            pg.display.flip()

            self.delta_time = self.clock.tick(MAX_FPS)

            self.get_fps()
            self.num_frames += 1

# -----------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app = App()
    app.run()

