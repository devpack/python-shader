import numpy as np

import pyglet, glm
from pyglet.gl import *
from pyglet.graphics import Group
from pyglet.graphics.shader import Shader, ShaderProgram

from config import *

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
        super().__init__(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, vsync=vsync)

        self.screen_width = screen_width
        self.screen_height = screen_height

        #
        self.lastTime = time.time()
        self.currentTime = time.time()
        self.fps = FPSCounter()

        #arcade.set_background_color(arcade.color.BLACK)
        pyglet.gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        #glEnable(GL_DEPTH_TEST)
        #glEnable(GL_CULL_FACE)

        self.dt = 0.0

        # load shaders
        shader_name = "default"
        with open(f'shaders/{shader_name}_vs.glsl') as file:
            vertex_shader = file.read()

        with open(f'shaders/{shader_name}_fs.glsl') as file:
            fragment_shader = file.read()

        vert_shader = Shader(vertex_shader, 'vertex')
        frag_shader = Shader(fragment_shader, 'fragment')
        self.shader_program = ShaderProgram(vert_shader, frag_shader)


        #all_shaders = ShaderProgram(self.ctx)
        #self.program = all_shaders.programs['default']

        # -1, 1, 0 ------------ 1, 1, 0
        #     |                    |
        #     |                    |
        #     |                    |
        #     |                    |
        # -1, -1, 0 ----------- 1, -1, 0

        # x, y, z,  r, g, b, a
        vertex_data = ( 1.0, -1.0, -2.0,  # bottom right
                        -1.0, -1.0, -2.0, # bottom left
                        0.0, 1.0, -2.0,   # top middle
                      )

        color_data  = ( 1.0, 0.0, 0.0, 1.0, # bottom right
                        0.0, 1.0, 0.0, 1.0, # bottom left
                        0.0, 0.0, 1.0, 1.0  # top middle
                      )

        indices = (0, 1, 2)

        # vbo
        self.batch = pyglet.graphics.Batch()
        group = MyRenderGroup(self.shader_program)

        mm = glm.perspective(glm.radians(50), self.screen_width/self.screen_height, 0.1, 100)
        self.shader_program.uniforms["m_proj"].set(pyglet.math.Mat4.perspective_projection(self.screen_width/self.screen_height, z_near=0.1, z_far=255))
        #self.shader_program.uniforms["m_proj"].set(mm)

        vertex_list = self.shader_program.vertex_list_indexed(  3, GL_TRIANGLES, indices, self.batch, group,
                                                                vertexPosition=('f', vertex_data),
                                                                vertexColor=('f', color_data))

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
        pass

    def on_mouse_release(self, x, y, button, key_modifiers):
        pass

    def on_key_press(self, key, key_modifiers):
        pass

    def on_key_release(self, key, key_modifiers):
        pass

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        pass

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """

        self.dt = delta_time

    def on_draw(self):
        self.clear()

        self.batch.draw()

        self.get_fps()

# ----------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app = App(vsync=VSYNC)
    pyglet.app.run(interval=1e-6)