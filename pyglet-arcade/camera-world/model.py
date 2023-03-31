import arcade, array
import numpy as np
import moderngl as mgl
import pywavefront
from pyglet.math import Mat4, Vec3
from math import cos, sin, radians
import PIL.Image

# -----------------------------------------------------------------------------------------------------------

class Model:

    def __init__(self, app, program, pos=Vec3(0, 0, 0), rot=Vec3(0, 0, 0), scale=Vec3(1, 1, 1), texture_color=None):
        self.app = app
        self.ctx = app.ctx

        self.pos = pos
        self.rot = rot
        self.scale = scale
        self.texture_color = texture_color

        self.program = program
        self.texture = self.get_texture("textures/test.png")

        # vbo
        self.buffer = self.ctx.buffer(data=np.array(self.cube_vertex_data(load_rig=0), dtype=np.float32))
        self.buffer_description = arcade.gl.BufferDescription(self.buffer, '2f 3f 3f', ['in_texcoord_0', 'in_normal', 'in_position'])

        # vao
        self.vao = self.ctx.geometry([self.buffer_description], mode=self.ctx.TRIANGLE_STRIP)

        self.m_model = self.get_model_matrix()

        self.program.set_uniform_safe(name="m_proj", value=self.app.camera.m_proj)
        self.program.set_uniform_safe(name="m_view", value=self.app.camera.m_view)
        self.program.set_uniform_safe(name="m_model", value=self.m_model)

        self.program.set_uniform_safe(name="u_texture_0", value=0)
        #self.texture.use(location=0)
        self.texture.use()

        #self.program['m_view_light'].write(self.app.light.m_view_light)
        self.program.set_uniform_safe(name="light.position", value=self.app.light.position)
        self.program.set_uniform_safe(name="light.Ia", value=self.app.light.Ia)
        self.program.set_uniform_safe(name="light.Id", value=self.app.light.Id)
        self.program.set_uniform_safe(name="light.Is", value=self.app.light.Is)

    def update(self):
        #self.texture.use(location=0)
        self.texture.use()

        # rotate on Y axis
        self.m_model = self.m_model.from_rotation(self.app.time, Vec3(0, 1, 0)) #@ self.m_model

        self.program.set_uniform_safe(name="m_view", value=self.app.camera.m_view)
        self.program.set_uniform_safe(name="m_model", value=self.m_model)
        self.program.set_uniform_safe(name="camPos", value=self.app.camera.position)

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

    def get_model_matrix_id(self):
        m_model = Mat4()
        return m_model

    def get_texture(self, path):

        #data = array.array('B', [0, 0, 255, 255])
        #image = PIL.Image.new("RGBA", (100, 100), color=(0, 255, 0, 255))

        #texture = arcade.Texture("test", image=image)

        #texture = self.ctx.texture((512, 512), components=4, image=image)
        #texture.filter = self.ctx.LINEAR_MIPMAP_LINEAR, self.ctx.LINEAR

        #texture.fill(color=self.texture_color)
        #texture = self.ctx.texture(size=texture.get_size(), components=3, data=pg.image.tostring(texture, 'RGB'))

        if self.texture_color:
            #data = array.array('f', [0., 1., 0., 0.])
            #texture = self.ctx.texture((1, 1), components=4, data=data, dtype="f4")

            data = array.array('B', [self.texture_color[0], self.texture_color[1], self.texture_color[2], 255])
            texture = self.ctx.texture((1, 1), components=4, data=data, dtype="f1")
        else:
            texture = self.ctx.load_texture(path, build_mipmaps=True)

        texture.filter = self.ctx.LINEAR, self.ctx.LINEAR
        texture.anisotropy = 32

        return texture

    def cube_vertex_data(self, load_rig=False):

        if load_rig:
            objs = pywavefront.Wavefront('objects/cube_rig/CubeRig.obj', cache=True, parse=True)
            obj = objs.materials.popitem()[1]
            vertex_data = obj.vertices
            vertex_data = np.array(vertex_data, dtype='f4')
            return vertex_data
        else:
            # X, Y, Z [-1, 1]
            vertices = [(-1, -1, 1), ( 1, -1,  1), (1,  1,  1), (-1, 1,  1),
                        (-1, 1, -1), (-1, -1, -1), (1, -1, -1), ( 1, 1, -1)]

            indices = [(0, 2, 3), (0, 1, 2),
                    (1, 7, 2), (1, 6, 7),
                    (6, 5, 4), (4, 7, 6),
                    (3, 4, 5), (3, 5, 0),
                    (3, 7, 4), (3, 2, 7),
                    (0, 6, 1), (0, 5, 6)]

            vertex_data = np.array( [vertices[ind] for triangle in indices for ind in triangle] , dtype='f4')

            # texture UV [0, 1]
            tex_coord_vertices = [(0, 0), (1, 0), (1, 1), (0, 1)]
            tex_coord_indices = [(0, 2, 3), (0, 1, 2),
                                 (0, 2, 3), (0, 1, 2),
                                 (0, 1, 2), (2, 3, 0),
                                 (2, 3, 0), (2, 0, 1),
                                 (0, 2, 3), (0, 1, 2),
                                 (3, 1, 2), (3, 0, 1),]

            tex_coord_data = np.array( [tex_coord_vertices[ind] for triangle in tex_coord_indices for ind in triangle] , dtype='f4')

            # X Y Z
            normals = [( 0, 0, 1) * 6,
                       ( 1, 0, 0) * 6,
                       ( 0, 0,-1) * 6,
                       (-1, 0, 0) * 6,
                       ( 0, 1, 0) * 6,
                       ( 0,-1, 0) * 6,]

            normals = np.array(normals, dtype='f4').reshape(36, 3)

            vertex_data = np.hstack([normals, vertex_data])
            vertex_data = np.hstack([tex_coord_data, vertex_data])

            return vertex_data
