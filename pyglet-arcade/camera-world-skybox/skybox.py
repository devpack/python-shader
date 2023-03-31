import arcade
import numpy as np
import moderngl as mgl
from pyglet.math import Vec3, Mat4, Mat3
from arcade.resources import resolve_resource_path
from PIL import Image

# -----------------------------------------------------------------------------------------------------------

class SkyBox:

    def __init__(self, app, program, pos=Vec3(0, 0, 0), rot=Vec3(0, 0, 0), scale=Vec3(1, 1, 1)):

        self.app = app
        self.ctx = app.ctx

        self.pos = pos
        self.rot = rot
        self.scale = scale

        self.program = program
        self.texture = self.get_texture_cube("textures/skybox2/")

        # vbo
        self.buffer = self.ctx.buffer(data=np.array(self.skybox_vertex_data(), dtype=np.float32))
        self.buffer_description = arcade.gl.BufferDescription(self.buffer, '3f', ['in_position'])

        # vao
        self.vao = self.ctx.geometry([self.buffer_description], mode=self.ctx.TRIANGLE_STRIP)

        self.m_model = self.get_model_matrix()

        self.program['u_texture_skybox'] = 0
        self.texture.use()

    def update(self):
        #self.texture.use()

        #m_view = glm.mat4(glm.mat3(self.app.camera.m_view))
        #self.program['m_invProjView'].write(glm.inverse(self.app.camera.m_proj * m_view))

        cm4 = Mat4([self.app.camera.m_view[0], self.app.camera.m_view[1], self.app.camera.m_view[2],  0.0,
                    self.app.camera.m_view[4], self.app.camera.m_view[5], self.app.camera.m_view[6],  0.0,
                    self.app.camera.m_view[8], self.app.camera.m_view[9], self.app.camera.m_view[10], 0.0,
                                          0.0,                       0.0,                        0.0, 1.0
                    ])

        self.program.set_uniform_safe(name="m_invProjView", value = Mat4.__invert__(cm4 @ self.app.camera.m_proj))

    def render(self):
        self.vao.render(self.program, mode=self.ctx.TRIANGLES)

    def destroy(self):
        pass
        #self.vbo.release()
        #self.vao.release()

    def get_model_matrix(self):
        m_model = Mat4()
        m_model = m_model.translate(self.pos) @ m_model
        m_model = m_model.from_rotation(self.rot.z, Vec3(0, 0, 1)) @ m_model
        m_model = m_model.from_rotation(self.rot.y, Vec3(0, 1, 0)) @ m_model
        m_model = m_model.from_rotation(self.rot.x, Vec3(1, 0, 0)) @ m_model
        m_model = m_model.scale(self.scale)

        return m_model

    def load_tex(self, path, build_mipmaps=0, flip_x=0, flip_y=0):
        path = resolve_resource_path(path)

        image = Image.open(str(path))

        if flip_x:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)

        if flip_y:
            image = image.transpose(Image.FLIP_TOP_BOTTOM)

        texture = self.ctx.texture(image.size, components=4, data=image.convert("RGBA").tobytes())
        image.close()

        if build_mipmaps:
            texture.build_mipmaps()

        return texture

    def get_texture_cube(self, dir_path, ext='png'):
        faces = ['right', 'left', 'top', 'bottom'] + ['front', 'back'][::-1]

        textures = []
        for face in faces:
            if face in ['right', 'left', 'front', 'back']:
                texture = self.load_tex(dir_path + f'{face}.{ext}', build_mipmaps=0, flip_x=1)
            else:
                texture = self.load_tex(dir_path + f'{face}.{ext}', build_mipmaps=0, flip_y=1)

            textures.append(texture)

        size = textures[0].size
        c = mgl.create_context()
        texture_cube = c.texture_cube(size=size, components=4, data=None)

        for i in range(6):
            texture_data = textures[i].read()
            texture_cube.write(face=i, data=texture_data)

        return texture_cube

    def skybox_vertex_data(self):
        # in clip space
        z = 0.9999
        vertices = [(-1, -1, z), (3, -1, z), (-1, 3, z)]
        vertex_data = np.array(vertices, dtype='f4')
        return vertex_data
