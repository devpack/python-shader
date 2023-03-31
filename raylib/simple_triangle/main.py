import pyray as ray
from raylib import MOUSE_BUTTON_LEFT, MOUSE_BUTTON_RIGHT
from raylib.colors import *

from config import *

# Raylib Shader uniform types: https://github.com/raysan5/raylib/blob/master/src/rlgl.h#L483

# -----------------------------------------------------------------------------------------------------------

class App:

    def __init__(self, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT):

        self.screen_width = screen_width
        self.screen_height = screen_height

        #
        self.lastTime = time.time()
        self.currentTime = time.time()

        self.fps = FPSCounter()

        ray.init_window(self.screen_width, self.screen_height, "")
        ray.set_target_fps(MAX_FPS)

        # position, target, up, fovy, projection
        self.camera = ray.Camera3D((2.0, 3.0, 2.0), [0.0, 1.0, 0.0], [0.0, 1.0, 0.0], 70.0, ray.CAMERA_PERSPECTIVE)
        ray.set_camera_mode(self.camera, ray.CAMERA_ORBITAL)
        #ray.set_camera_mode(self.camera, ray.CAMERA_THIRD_PERSON)
        #ray.set_camera_move_controls(ray.KEY_UP, ray.KEY_DOWN, ray.KEY_RIGHT, ray.KEY_LEFT, ray.KEY_LEFT_SHIFT, ray.KEY_LEFT_CONTROL)

        vertex_data = (
            0.5, -0.5, 0.0,
             -0.5, -0.5, 0.0,
             0,  0.5, 0.0, 0.0
        )

        #self.shader = ray.load_shader('shaders/vertex.glsl', 'shaders/vertex.glsl')
        self.shader = ray.load_shader('shaders/vertex.glsl', 'shaders/fragment.glsl')

        #self.program = ray.rl_load_shader_program(0, 0)
        self.target = ray.load_render_texture(self.screen_width, self.screen_height)

        #ray.set_shader_value(self.shader, 0, "vertexPosition", 2)

    def get_fps(self):
        self.currentTime = time.time()
        delta = self.currentTime - self.lastTime

        if delta >= 1:

            fps = f"Raylib FPS: {self.fps.get_fps():3.0f}"
            ray.set_window_title(fps)

            self.lastTime = self.currentTime

        self.fps.tick()

    def check_events(self):

        # keys
        if ray.is_key_down(ray.KEY_UP):
            pass
        elif ray.is_key_down(ray.KEY_DOWN):
            pass

        if ray.is_key_down(ray.KEY_LEFT):
            pass
        elif ray.is_key_down(ray.KEY_RIGHT):
            pass

        # mouse
        if ray.is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
            pos = ray.get_mouse_position()
            #print("LM pressed at %s %s" % (pos.x, pos.y))
        elif ray.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT):
            pos = ray.get_mouse_position()
            #print("RM pressed at %s %s" % (pos.x, pos.y))

    # main loop
    def run(self):

        while not ray.window_should_close():
            self.check_events()

            #ray.update_camera(self.camera)

            ray.begin_drawing()
            ray.clear_background(BLACK)

            #ray.begin_texture_mode(self.target)
            #ray.clear_background(BLACK)

            #ray.draw_rectangle(0, 0, WIN_W, WIN_H, SKYBLUE)
            #ray.begin_mode_3d(self.camera)
            #ray.draw_grid(20, 1.0)
            #ray.end_mode_3d()

            #ray.end_texture_mode()

            #ray.begin_mode_3d(self.camera)
            ray.begin_shader_mode(self.shader)

            ray.draw_texture_rec(self.target.texture, ray.Rectangle(0, 0, self.screen_width, self.screen_height), ray.Vector2(0, 0), WHITE)
            #ray.draw_texture_ex(self.target.texture, ray.Vector2(0, 0), 0.0, 0.0, WHITE)
            #ray.draw_rectangle(0, 0, self.screen_width, self.screen_height, BLUE)

            ray.end_shader_mode()
            #ray.end_mode_3d()

            #ray.begin_mode_3d(self.camera)
            #ray.draw_grid(20, 1.0)
            #ray.draw_cube((0.0, 0.0, 0.0), 2.0, 2.0, 2.0, RED)
            #ray.end_mode_3d()

            #ray.draw_text("Hello world", 190, 200, 20, VIOLET)

            self.get_fps()

            ray.end_drawing()

        ray.unload_shader(self.shader)
        ray.close_window()

# -----------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    app = App()
    app.run()

