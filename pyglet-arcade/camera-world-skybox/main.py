import arcade, random
from arcade.gl import Program
from array import array
import numpy as np
import pyglet 
from pyglet.math import Mat4, Vec2, Vec3

from config import *
from shader_program import ShaderProgram
from skybox import *
from model import *
from camera import Camera
from light import Light

# INDIRECT RENDER: https://github.com/pythonarcade/arcade/blob/development/arcade/examples/gl/render_indirect.py
# OFF SCREEN: https://github.com/pythonarcade/arcade/blob/development/arcade/examples/perspective.py

# -----------------------------------------------------------------------------------------------

class App(arcade.Window):

    def __init__(self, screen_width = SCREEN_WIDTH, screen_height = SCREEN_HEIGHT):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, center_window=True, antialiasing=False, gl_version=(3, 3), vsync=False, resizable=True)

        self.screen_width = screen_width
        self.screen_height = screen_height

        # time
        self.lastTime = time.time()
        self.currentTime = time.time()
        self.fps = FPSCounter()

        # camera
        self.forward = False
        self.backward = False
        self.right = False
        self.left = False
        self.up = False
        self.down = False

        self.mouse_x, self.mouse_y = 0, 0
        self.mouse_dx, self.mouse_dy = 0, 0
        self.mouse_button_down = False

        #
        arcade.set_background_color(arcade.color.BLACK)

        self.dt = 0.0
        self.time = 0

        self.ctx.enable(self.ctx.BLEND, self.ctx.DEPTH_TEST, self.ctx.CULL_FACE)

        # load shaders
        all_shaders = ShaderProgram(self.ctx)
        self.program = all_shaders.programs['world']
        self.skybox_program = all_shaders.get_program("skybox")

        # light
        self.light = Light(position=LIGHT_POS)

        # camera
        self.camera = Camera(self, fov=FOV, near=NEAR, far=FAR, position=CAM_POS, speed=SPEED, sensivity=SENSITIVITY)

        # scene object
        self.scene = []
        self.scene.append( Model(self, self.program, pos=Vec3(0, 0, 0), rot=Vec3(1, 1, 1), scale=Vec3(1, 1, 1), texture_color=None) )
        #self.scene.append( Model(self, self.program, pos=Vec3(0, 0, -2), rot=Vec3(0, 0, 0), scale=Vec3(1, 1, 1), texture_color=(255, 0, 0)) )

        self.sky = SkyBox(self, self.skybox_program, pos=Vec3(0, 0, 0), rot=Vec3(0, 0, 0), scale=Vec3(1, 1, 1))

        # shader uniforms
        self.m_model = Mat4()
        self.program.set_uniform_safe(name="m_model", value=self.m_model)
        self.program.set_uniform_safe(name="m_proj", value=self.camera.m_proj)
        self.program.set_uniform_safe(name="m_view", value=self.camera.m_view)


        # prime specific
        self.last_t = self.get_time()
        self.num = 1
        self.all_dir = ["f", "b", "l", "r", "u", "d"]
        self.dir_pair = {"f":"b", "b":"f", "l":"r", "r":"l", "u":"d", "d":"u"}
        self.cur_dir = "f"
        self.obj_z = 0
        self.obj_x = 0
        self.obj_y = 0

        self.primes = self.prime_list(max=MAX_PRIME)


    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        #self.program.set_uniform_safe(name="m_proj", value=self.camera.m_proj)

    def get_fps(self):
        self.currentTime = time.time()
        delta = self.currentTime - self.lastTime

        if delta >= 1:

            fps = f"Arcade FPS: {self.fps.get_fps():3.0f}"
            cam_pos = f"CamPos: {int(self.camera.position.x)}, {int(self.camera.position.y)}, {int(self.camera.position.z)}"

            self.set_caption(fps + " | " + cam_pos)

            self.lastTime = self.currentTime

        self.fps.tick()

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            pass
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            pass

    def on_mouse_release(self, x, y, button, key_modifiers):
        pass

    def on_key_press(self, key, key_modifiers):
        if key == arcade.key.ESCAPE:
            arcade.close_window()

        if key == arcade.key.UP:
            self.forward = True
        if key == arcade.key.DOWN:
            self.backward = True
        if key == arcade.key.LEFT:
            self.left = True
        if key == arcade.key.RIGHT:
            self.right = True
        if key == arcade.key.LCTRL:
            self.up = True
        if key == arcade.key.LSHIFT:
            self.down = True

    def on_key_release(self, key, key_modifiers):
        if key == arcade.key.UP:
            self.forward = False
        if key == arcade.key.DOWN:
            self.backward = False
        if key == arcade.key.LEFT:
            self.left = False
        if key == arcade.key.RIGHT:
            self.right = False
        if key == arcade.key.LCTRL:
            self.up = False
        if key == arcade.key.LSHIFT:
            self.down = False

    def on_mouse_drag(self, x, y, dx, dy, buttons, mod):
        self.mouse_dx = -dx
        self.mouse_dy = dy

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        pass

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here. Normally, you'll call update() on the sprite lists that need it.
        """

        self.dt = delta_time
        self.time += self.dt
        #print(self.time)

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

    def get_time(self):
        return time.time()

    def on_draw(self):
        pyglet.gl.glClear(pyglet.gl.GL_COLOR_BUFFER_BIT | pyglet.gl.GL_DEPTH_BUFFER_BIT)
        self.clear(color=(20, 40, 60))

        if 0:
            # PRIMES
            if self.get_time() - self.last_t > 0.01:
                self.last_t = self.get_time()

                factor = 1
                if self.cur_dir == "f":
                    self.obj_z -= factor
                elif self.cur_dir == "b":
                    self.obj_z += factor
                if self.cur_dir == "l":
                    self.obj_x -= factor
                elif self.cur_dir == "r":
                    self.obj_x += factor
                if self.cur_dir == "u":
                    self.obj_y -= factor
                elif self.cur_dir == "d":
                    self.obj_y += factor

                # cube_col = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                # if self.is_prime(num):
                if self.num < MAX_PRIME:
                    if self.num in self.primes:
                        a = ["f", "b", "l", "r", "u", "d"]
                        a.remove(self.cur_dir)
                        a.remove(self.dir_pair[self.cur_dir])
                        self.cur_dir = a[random.randint(0, 3)]
                        # self.cur_dir = a[num % 6]

                        cube_col = (255, 0, 0)
                        scale = Vec3(1, 1, 1)
                    else:
                        cube_col = (0, 255, 0)
                        scale = Vec3(1, 1, 1)

                    self.scene.append(
                        Model(self, self.program, pos=Vec3(self.obj_x, self.obj_y, self.obj_z), rot=Vec3(0, 0, 0),
                              scale=scale, texture_color=cube_col))

                self.num += 1

        #
        self.camera.update(self.mouse_dx, self.mouse_dy, self.forward, self.backward, self.left, self.right, self.up, self.down)

        #pyglet.gl.glDepthFunc(pyglet.gl.GL_LEQUAL)
        #pyglet.gl.glDepthFunc(pyglet.gl.GL_LESS)

        self.sky.update()
        self.sky.render()

        for obj in self.scene:
            obj.update()
            obj.render()



        self.mouse_dx = 0
        self.mouse_dy = 0

        #arcade.draw_text()

        self.get_fps()

# -----------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app = App()
    #app.run()
    #arcade.run()
    #pyglet.app.run()
    pyglet.app.run(1e-6)