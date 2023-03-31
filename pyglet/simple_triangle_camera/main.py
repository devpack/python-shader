import numpy as np

import pyglet
from pyglet.gl import *
from pyglet.graphics import Group
from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.math import Mat4, Vec2, Vec3

from config import *
from camera import Camera

# https://github.com/pyglet/pyglet/blob/master/examples/opengl/opengl_shader.py
# https://pyglet.readthedocs.io/en/latest/programming_guide/graphics.html#

# ----------------------------------------------------------------------------------------------------------------------

class MyRenderGroup(Group):
    """A Group that enables and binds a Texture and ShaderProgram.
    RenderGroups are equal if their Texture and ShaderProgram
    are equal.
    """
    def __init__(self, program, order=0, parent=None):
        """Create a RenderGroup.
        :Parameters:
            `program` : `~pyglet.graphics.shader.ShaderProgram`
                ShaderProgram to use.
            `order` : int
                Change the order to render above or below other Groups.
            `parent` : `~pyglet.graphics.Group`
                Parent group.
        """
        super().__init__(order, parent)
        self.program = program

    def set_state(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.program.use()

    def unset_state(self):
        glDisable(GL_BLEND)

    def __hash__(self):
        return hash((self.order, self.parent, self.program))

    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                self.order == other.order and
                self.program == other.program and
                self.parent == other.parent)

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

class App(pyglet.window.Window):

    def __init__(self, screen_width = SCREEN_WIDTH, screen_height = SCREEN_HEIGHT, vsync=False):
        super().__init__(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, vsync=vsync, resizable=True)

        self.screen_width = screen_width
        self.screen_height = screen_height

        #
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

        #arcade.set_background_color(arcade.color.BLACK)
        pyglet.gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        #glEnable(GL_DEPTH_TEST)
        #glEnable(GL_CULL_FACE)

        self.dt = 0.0
        self.time = 0

        # camera
        self.camera = Camera(self, fov=FOV, near=NEAR, far=FAR, position=CAM_POS, speed=SPEED, sensivity=SENSITIVITY)

        # load shaders
        shader_name = "default"
        with open(f'shaders/{shader_name}_vs.glsl') as file:
            vertex_shader = file.read()

        with open(f'shaders/{shader_name}_fs.glsl') as file:
            fragment_shader = file.read()

        vert_shader = Shader(vertex_shader, 'vertex')
        frag_shader = Shader(fragment_shader, 'fragment')
        self.program = ShaderProgram(vert_shader, frag_shader)


        #all_shaders = ShaderProgram(self.ctx)
        #self.program = all_shaders.programs['default']

        # -1, 1, 0 ------------ 1, 1, 0
        #     |                    |
        #     |                    |
        #     |                    |
        #     |                    |
        # -1, -1, 0 ----------- 1, -1, 0

        # x, y, z,  r, g, b, a
        vertex_data = ( 1.0, -1.0, 0.0,  # bottom right
                        -1.0, -1.0, 0.0, # bottom left
                        0.0, 1.0, 0.0,   # top middle
                      )

        color_data  = ( 1.0, 0.0, 0.0, 1.0, # bottom right
                        0.0, 1.0, 0.0, 1.0, # bottom left
                        0.0, 0.0, 1.0, 1.0  # top middle
                      )

        indices = (0, 1, 2)

        # vbo
        self.batch = pyglet.graphics.Batch()
        group = MyRenderGroup(self.program)

        #self.program.uniforms["m_proj"].set(pyglet.math.Mat4.perspective_projection(self.screen_width/self.screen_height, z_near=0.1, z_far=255))
        #self.program.uniforms["m_proj"].set(mm)

        vertex_list = self.program.vertex_list_indexed(  3, GL_TRIANGLES, indices, self.batch, group,
                                                                vertexPosition=('f', vertex_data),
                                                                vertexColor=('f', color_data))

        #
        #self.m_model = Mat4.from_translation((0, 0, -2))
        self.m_model = Mat4()
        #self.program["m_model"] = self.m_model
        self.program.uniforms["m_model"].set(self.m_model)
        self.program["m_proj"] = self.camera.get_projection_matrix()
        self.program["m_view"] = self.camera.get_view_matrix()

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

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self.program["m_proj"] = self.camera.get_projection_matrix()
        return pyglet.event.EVENT_HANDLED

    def on_mouse_drag(self, x, y, dx, dy, buttons, mod):
        self.mouse_dx = -dx
        self.mouse_dy = dy

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_mouse_release(self, x, y, button, key_modifiers):
        pass

    def on_key_press(self, key, key_modifiers):
        if key == pyglet.window.key.ESCAPE:
            return pyglet.event.EVENT_HANDLED

        if key == pyglet.window.key.UP:
            self.forward = True
        if key == pyglet.window.key.DOWN:
            self.backward = True
        if key == pyglet.window.key.LEFT:
            self.left = True
        if key == pyglet.window.key.RIGHT:
            self.right = True
        if key == pyglet.window.key.LCTRL:
            self.up = True
        if key == pyglet.window.key.LSHIFT:
            self.down = True

    def on_key_release(self, key, key_modifiers):
        if key == pyglet.window.key.UP:
            self.forward = False
        if key == pyglet.window.key.DOWN:
            self.backward = False
        if key == pyglet.window.key.LEFT:
            self.left = False
        if key == pyglet.window.key.RIGHT:
            self.right = False
        if key == pyglet.window.key.LCTRL:
            self.up = False
        if key == pyglet.window.key.LSHIFT:
            self.down = False

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        pass

    def on_refresh(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """

        self.dt = delta_time
        self.time += self.dt

    def on_draw(self):
        self.clear()

        #print(self.time)

        ry = Mat4.from_rotation(self.time, (0, 1, 0))
        self.program["m_model"] = ry @ self.m_model

        self.program["m_view"] = self.camera.get_view_matrix()
        self.camera.update(self.mouse_dx, self.mouse_dy, self.forward, self.backward, self.left, self.right,
                           self.up, self.down)

        self.mouse_dx = 0
        self.mouse_dy = 0

        self.batch.draw()

        self.get_fps()

# ----------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app = App(vsync=VSYNC)
    pyglet.app.run(1e-6)