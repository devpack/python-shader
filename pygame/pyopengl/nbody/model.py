from config import *
import pygame as pg
import numpy as np
import moderngl as mgl
import glm, math
import pywavefront
import random, copy
import numba
from OpenGL.GL.shaders import compileProgram,compileShader
from OpenGL.GL import *
import gl_utils as gl_utils

# -----------------------------------------------------------------------------------------------------------

class Bodies:

    def __init__(self, app):
        self.app = app

        glUseProgram(self.app.nbody_program)

        glEnable(GL_VERTEX_PROGRAM_POINT_SIZE)

        glUniformMatrix4fv(
            glGetUniformLocation(self.app.nbody_program, "m_proj"),
            1, GL_FALSE, glm.value_ptr(self.app.camera.m_proj)
        )

        glUniformMatrix4fv(
            glGetUniformLocation(self.app.nbody_program, "m_view"),
            1, GL_FALSE, glm.value_ptr(self.app.camera.m_view)
        )

        self.m_model = glm.mat4()

        glUniformMatrix4fv(
            glGetUniformLocation(self.app.nbody_program, "m_model"),
            1, GL_FALSE, glm.value_ptr(self.m_model)
        )

        # Body
        # {
        #    vec4 pos; // x, y, z, w = mass
        #    vec4 col; // r, g, b, a
        #    vec4 vel; // vx, vy, vz, w = radius
        #    vec4 acc; // ax, ay, az, w = bodyID
        # };

        #bodies = [ -1, -1, 0, 1,  1, 1, 1, 1,  0, 0, 0, 1,  0, 0, 0, 0]

        particles_array = self.get_particles()

        self.bodies_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.bodies_vbo)
        glBufferData(GL_ARRAY_BUFFER, particles_array.nbytes, particles_array, GL_STATIC_DRAW)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # in_position, location = 0
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 16*4, ctypes.c_void_p(0))

        # in_color, location = 1
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 16*4, ctypes.c_void_p(16))

        if USE_COMPUTE_SHADER:
            glUseProgram(self.app.compute_shader_program)
            self.bodies_ssbo = glGenBuffers(1)
            glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.bodies_ssbo)

            # particles_array.nbytes = 16*4*NB_BODY
            glBufferStorage(GL_SHADER_STORAGE_BUFFER, 16*4*NB_BODY, particles_array.data, GL_MAP_READ_BIT | GL_MAP_WRITE_BIT | GL_MAP_PERSISTENT_BIT | GL_MAP_COHERENT_BIT)
            glUseProgram(0)

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
        glUseProgram(self.app.nbody_program)

        glUniformMatrix4fv(
            glGetUniformLocation(self.app.nbody_program, "m_model"),
            1, GL_FALSE, glm.value_ptr(self.m_model)
        )

        glUniformMatrix4fv(
            glGetUniformLocation(self.app.nbody_program, "m_view"),
            1, GL_FALSE, glm.value_ptr(self.app.camera.m_view)
        )

        if not USE_COMPUTE_SHADER:
            print(type(self.bodies_vbo))
            print(dir(self.bodies_vbo))
            a = self.bodies_vbo.read(components=16, dtype='f4')
            d = np.frombuffer(a, dtype='f4')

            bodies = self.calc_bodies(copy.copy(d))

            #self.bodies_vbo.write(bodies)

    def render(self):
        glUseProgram(self.app.nbody_program)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_POINTS, 0, NB_BODY)

    def destroy(self):
        glUseProgram(self.app.nbody_program)
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1,(self.bodies_vbo,))

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
