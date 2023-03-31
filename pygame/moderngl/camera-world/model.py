import pygame as pg
import numpy as np
import moderngl as mgl
import glm
import pywavefront

# -----------------------------------------------------------------------------------------------------------

class Model:

    def __init__(self, app, shader_program, pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), texture_color=(255, 0, 255)):
        self.app = app
        self.ctx = app.ctx

        self.pos = pos
        self.rot = glm.vec3([glm.radians(a) for a in rot])
        self.scale = scale
        self.texture_color = texture_color

        self.shader_program = shader_program
        self.texture = self.get_texture("textures/test.png")

        self.vbo = self.ctx.buffer( self.cube_vertex_data(load_rig=True) )
        self.vao = self.ctx.vertex_array(self.shader_program,
                                              [(self.vbo, '2f 3f 3f', 'in_texcoord_0', 'in_normal', 'in_position')])

        # Shader uniforms var
        #self.program['u_resolution'].write(glm.vec2(self.app.WIN_SIZE))

        self.m_model = self.get_model_matrix()

        self.shader_program['m_proj'].write(self.app.camera.m_proj)
        self.shader_program['m_view'].write(self.app.camera.m_view)
        self.shader_program['m_model'].write(self.m_model)

        self.shader_program['u_texture_0'] = 0
        self.texture.use(location=0)

        #self.shader_program['m_view_light'].write(self.app.light.m_view_light)
        self.shader_program['light.position'].write(self.app.light.position)
        self.shader_program['light.Ia'].write(self.app.light.Ia)
        self.shader_program['light.Id'].write(self.app.light.Id)
        self.shader_program['light.Is'].write(self.app.light.Is)

    def update(self):
        self.texture.use(location=0)

        # rotate on Y axis
        #self.m_model = glm.rotate(self.m_model, self.app.time, glm.vec3(1, 1, 1))

        self.shader_program['m_model'].write(self.m_model)
        self.shader_program['m_view'].write(self.app.camera.m_view)
        self.shader_program['camPos'].write(self.app.camera.position)

    def render(self):
        self.vao.render(self.app.mode) # points, lines, triangles etc

    def destroy(self):
        self.vbo.release()
        self.vao.release()

    def set_uniform(self, u_name, u_value):
        try:
            self.shader_program[u_name] = u_value
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

    def get_model_matrix_id(self):
        m_model = glm.mat4()
        return m_model

    def get_texture(self, path):
        texture = pg.image.load(path).convert()
        texture = pg.transform.flip(texture, flip_x=False, flip_y=True)
        texture.fill(color=self.texture_color)
        texture = self.ctx.texture(size=texture.get_size(), components=3, data=pg.image.tostring(texture, 'RGB'))
        # mipmaps
        texture.filter = (mgl.LINEAR_MIPMAP_LINEAR, mgl.LINEAR)
        texture.build_mipmaps()
        # AF
        texture.anisotropy = 32.0
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
