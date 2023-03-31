import pygame as pg
import numpy as np
import moderngl as mgl
import glm

# -----------------------------------------------------------------------------------------------------------

class SkyBox:

    def __init__(self, app, program, pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
        self.app = app
        self.ctx = app.ctx

        self.pos = pos
        self.rot = glm.vec3([glm.radians(a) for a in rot])
        self.scale = scale

        self.program = program
        self.texture = self.get_texture_cube("textures/skybox2/")

        self.vbo = self.ctx.buffer( self.skybox_vertex_data() )
        self.vao = self.ctx.vertex_array(self.program, [(self.vbo, '3f', 'in_position')])

        self.m_model = self.get_model_matrix()

        self.program['u_texture_skybox'] = 0
        self.texture.use(location=0)

    def update(self):
        #self.texture.use(location=0)

        m_view = glm.mat4(glm.mat3(self.app.camera.m_view))
        self.program['m_invProjView'].write(glm.inverse(self.app.camera.m_proj * m_view))

    def render(self):
        self.vao.render()

    def destroy(self):
        self.vbo.release()
        self.vao.release()

    def set_uniform(self, u_name, u_value):
        try:
            self.program[u_name] = u_value
        except KeyError:
            pass

    def get_model_matrix(self):
        m_model = glm.mat4()
        m_model = glm.translate(m_model, self.pos)
        m_model = glm.rotate(m_model, self.rot.z, glm.vec3(0, 0, 1))
        m_model = glm.rotate(m_model, self.rot.y, glm.vec3(0, 1, 0))
        m_model = glm.rotate(m_model, self.rot.x, glm.vec3(1, 0, 0))
        m_model = glm.scale(m_model, self.scale)

        return m_model

    def get_texture_cube(self, dir_path, ext='png'):
        faces = ['right', 'left', 'top', 'bottom'] + ['front', 'back'][::-1]
        # textures = [pg.image.load(dir_path + f'{face}.{ext}').convert() for face in faces]
        textures = []
        for face in faces:
            texture = pg.image.load(dir_path + f'{face}.{ext}').convert()
            if face in ['right', 'left', 'front', 'back']:
                texture = pg.transform.flip(texture, flip_x=True, flip_y=False)
            else:
                texture = pg.transform.flip(texture, flip_x=False, flip_y=True)
            textures.append(texture)

        size = textures[0].get_size()
        texture_cube = self.ctx.texture_cube(size=size, components=3, data=None)

        for i in range(6):
            texture_data = pg.image.tostring(textures[i], 'RGB')
            texture_cube.write(face=i, data=texture_data)

        return texture_cube

    def skybox_vertex_data(self):
        # in clip space
        z = 0.9999
        vertices = [(-1, -1, z), (3, -1, z), (-1, 3, z)]
        vertex_data = np.array(vertices, dtype='f4')
        return vertex_data
