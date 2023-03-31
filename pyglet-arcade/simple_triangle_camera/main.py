import arcade
from arcade.gl import Program
from array import array
import numpy as np
import pyglet 
from pyglet.math import Mat4, Vec2, Vec3

from config import *
from shader_program import ShaderProgram

from camera import Camera

# INDIRECT RENDER: https://github.com/pythonarcade/arcade/blob/development/arcade/examples/gl/render_indirect.py
# OFF SCREEN: https://github.com/pythonarcade/arcade/blob/development/arcade/examples/perspective.py

# -----------------------------------------------------------------------------------------------

class App(arcade.Window):

    def __init__(self, screen_width = SCREEN_WIDTH, screen_height = SCREEN_HEIGHT):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, center_window=True, antialiasing=False, vsync=False, resizable=True)

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

        # camera
        self.camera = Camera(self, fov=FOV, near=NEAR, far=FAR, position=CAM_POS, speed=SPEED, sensivity=SENSITIVITY)

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

        # vbo
        self.buffer = self.ctx.buffer(data=np.array(vertex_data, dtype=np.float32))
        # self.buffer = self.ctx.buffer(data=array('f', vertex_data))
        self.buffer_description = arcade.gl.BufferDescription(self.buffer, '3f 4f', ['vertexPosition', 'vertexColor'])

        # vao
        self.vao = self.ctx.geometry([self.buffer_description], mode=self.ctx.TRIANGLE_STRIP)

        #
        #self.m_model = Mat4.from_translation((0, 0, -3))
        self.m_model = Mat4()
        self.program["m_model"] = self.m_model
        self.program["m_proj"] = self.camera.get_projection_matrix()
        self.program["m_view"] = self.camera.get_view_matrix()

        #self.program.set_uniform_safe(name="m_proj", value=mm)

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self.program["m_proj"] = self.camera.get_projection_matrix()

    def setup(self):
        """ Set up the game variables. Call to re-start the game. """
        # Create your sprites and sprite lists here
        pass

    def get_fps(self):
        self.currentTime = time.time()
        delta = self.currentTime - self.lastTime

        if delta >= 1:

            fps = f"Arcade FPS: {self.fps.get_fps():3.0f}"
            self.set_caption(fps)

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

    def on_draw(self):
        self.clear()

        ry = Mat4.from_rotation(self.time, (0, 1, 0))
        self.program["m_model"] = ry @ self.m_model

        self.program["m_view"] = self.camera.get_view_matrix()
        self.camera.update(self.mouse_dx, self.mouse_dy, self.forward, self.backward, self.left, self.right, self.up, self.down)

        self.vao.render(self.program, mode=self.ctx.TRIANGLES)

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