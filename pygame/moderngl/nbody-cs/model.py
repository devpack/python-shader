from config import *
import pygame as pg
import numpy as np
import moderngl as mgl
import glm, math
import pywavefront
import random, copy
import numba

# -----------------------------------------------------------------------------------------------------------

class Bodies:

    def __init__(self, app, program):
        self.app = app
        self.ctx = app.ctx

        self.program = program

        self.m_model = glm.mat4()

        self.program['m_model'].write(self.m_model)
        self.program['m_proj'].write(self.app.camera.m_proj)
        self.program['m_view'].write(self.app.camera.m_view)
        #self.program['cam_pos'].write(self.app.camera.position)

        # Body
        # {
        #    vec4 pos; // x, y, z, w = mass
        #    vec4 col; // r, g, b, a
        #    vec4 vel; // vx, vy, vz, w = radius
        #    vec4 acc; // ax, ay, az, w = bodyID
        # };

        particles_array = self.get_particles()
        self.ssbo_in    = self.ctx.buffer(data    = particles_array)
        self.ssbo_out   = self.ctx.buffer(reserve = particles_array.nbytes)

        self.vao        = self.ctx.vertex_array(self.program, [(self.ssbo_in, '4f 4f 8x4', 'in_position', 'in_color')])

    @staticmethod
    @numba.njit(fastmath=True)
    def calc_bodies(bodies):

        bodies = bodies.reshape(NB_BODY, 16)

        # leap 1/2
        for body in bodies:
            body[VELX] += body[ACCX] * HALF_DT
            body[VELY] += body[ACCY] * HALF_DT
            body[VELZ] += body[ACCZ] * HALF_DT

            body[POSX] += body[VELX] * DT
            body[POSY] += body[VELY] * DT
            body[POSZ] += body[VELZ] * DT

        # O2
        for pi in bodies:
            for pj in bodies:
                if pi[BODY_ID] != pj[BODY_ID]:
                    DRX = pj[POSX] - pi[POSX]
                    DRY = pj[POSY] - pi[POSY]
                    DRZ = pj[POSZ] - pi[POSZ]

                    DR2 = DRX * DRX + DRY * DRY + DRZ * DRZ
                    DR2 += EPS2

                    PHI = pj[MASS] / (math.sqrt(DR2) * DR2)

                    pi[ACCX] += DRX * PHI
                    pi[ACCY] += DRY * PHI
                    pi[ACCZ] += DRZ * PHI

        # leap 1/2
        for body in bodies:
            body[VELX] += body[ACCX] * HALF_DT
            body[VELY] += body[ACCY] * HALF_DT
            body[VELZ] += body[ACCZ] * HALF_DT

            body[ACCX] = body[ACCY] = body[ACCZ] = 0.0

        return bodies

    def update(self):
        self.program['m_model'].write(self.m_model)
        self.program['m_view'].write(self.app.camera.m_view)
        #self.program['cam_pos'].write(self.app.camera.position)

        if not USE_COMPUTE_SHADER:
            a = self.ssbo_in.read_chunks(4, 0, 4, 16 * NB_BODY)
            d = np.frombuffer(a, dtype='f4')

            bodies = self.calc_bodies(copy.copy(d))

            self.ssbo_in.write(bodies)

    def render(self):
        self.vao.render(mgl.POINTS)

    def destroy(self):
        self.ssbo_in.release()
        self.vao.release()

    def set_uniform(self, u_name, u_value):
        try:
            self.program[u_name] = u_value
        except KeyError:
            pass

    def get_particles(self):

        # Body
        # {
        #    vec4 pos; // x, y, z, w = mass
        #    vec4 col; // r, g, b, a
        #    vec4 vel; // vx, vy, vz, w = radius
        #    vec4 acc; // ax, ay, az, w = bodyID
        # };

        #bodies = [ -1, -1, 0, 1,  1, 1, 1, 1,  0, 0, 0, 1,  0, 0, 0, 0]

        bodies = []
        for i in range(0, NB_BODY):
            posx, posy, posz = self.pickball(8.0)

            # pos =  x, y, z, w = mass
            if i == 0:
                mass = 100.0
            else:
                mass = 1.0

            bodies.extend((posx, posy, posz, mass))

            # col = r, g, b, a
            #bodies.extend((random.uniform(0.5, 1.0), random.uniform(0.5, 1.0), random.uniform(0.5, 1.0), 1.0))
            bodies.extend((1.0, 1.0, 1.0, 1.0))

            # vel = vx, vy, vz, w = radius
            bodies.extend((0.0, 0.0, 0.0, 1.0))

            # acc = ax, ay, az, w = bodyID
            bodies.extend((0.0, 0.0, 0.0, i))


        vertex_data = np.asarray(bodies, dtype='f4') #vertex_data = np.array(bodies, dtype='f4')

        #print("vertex_data=", vertex_data)

        return vertex_data

    def pickball(self, radius):

        while True:
            rsq = 0.0

            posx = random.uniform(-1.0, 1.0)
            posy = random.uniform(-1.0, 1.0)
            posz = random.uniform(-1.0, 1.0)

            rsq = (posx * posx) + (posy * posy) + (posz * posz)

            if rsq <= 1.0:
                break

        posx = posx * radius
        posy = posy * radius
        posz = posz * radius

        return posx, posy, posz

# -----------------------------------------------------------------------------------------------------------

class Model:

    def __init__(self, app, program, pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), texture_color=(255, 0, 255)):
        self.app = app
        self.ctx = app.ctx

        self.pos = pos
        self.rot = glm.vec3([glm.radians(a) for a in rot])
        self.scale = scale
        self.texture_color = texture_color

        self.program = program
        self.texture = self.get_texture("textures/test.png")

        self.vbo = self.ctx.buffer( self.cube_vertex_data(load_rig=True) )
        self.vao = self.ctx.vertex_array(self.program,
                                       [(self.vbo, '2f 3f 3f', 'in_texcoord_0', 'in_normal', 'in_position')])

        # Shader uniforms var
        #self.program['u_resolution'].write(glm.vec2(self.app.WIN_SIZE))

        self.m_model = self.get_model_matrix()

        self.program['m_proj'].write(self.app.camera.m_proj)
        self.program['m_view'].write(self.app.camera.m_view)
        self.program['m_model'].write(self.m_model)

        self.program['u_texture_0'] = 0
        self.texture.use(location=0)

        #self.program['m_view_light'].write(self.app.light.m_view_light)
        self.program['light.position'].write(self.app.light.position)
        self.program['light.Ia'].write(self.app.light.Ia)
        self.program['light.Id'].write(self.app.light.Id)
        self.program['light.Is'].write(self.app.light.Is)

    def update(self):
        self.texture.use(location=0)

        # rotate on Y axis
        #self.m_model = glm.rotate(self.m_model, self.app.time, glm.vec3(1, 1, 1))

        self.program['m_model'].write(self.m_model)
        self.program['m_view'].write(self.app.camera.m_view)
        self.program['camPos'].write(self.app.camera.position)

    def render(self):
        self.vao.render(self.app.mode) # points, lines, triangles etc

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