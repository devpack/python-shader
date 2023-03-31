from OpenGL.GL.shaders import compileProgram,compileShader
from OpenGL.GL import *

class ShaderProgram:

    def __init__(self):
        self.programs = {}
        #self.programs['world'] = self.get_program('world')
        #self.programs['test'] = self.get_program('test')

    def get_program(self, shader_name):
        with open(f'shaders/{shader_name}_vs.glsl') as file:
            vertex_shader = file.read()

        with open(f'shaders/{shader_name}_fs.glsl') as file:
            fragment_shader = file.read()

        program = compileProgram(compileShader(vertex_shader, GL_VERTEX_SHADER),
                                 compileShader(fragment_shader, GL_FRAGMENT_SHADER))

        return program