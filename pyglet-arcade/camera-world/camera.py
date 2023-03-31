from pyglet.math import Mat4, Vec3
from math import cos, sin, radians

# -----------------------------------------------------------------------------------------------------------

class Camera:
    
    def __init__(self, app, fov=50, near=0.1, far=100, position=Vec3(0, 0, 5), speed=0.009, sensivity=0.07, yaw=-90, pitch=0):
        self.app = app

        self.fov = fov 
        self.near = near 
        self.far = far 
        self.position = position
        self.aspect_ratio = app.screen_width / app.screen_height

        self.speed = speed
        self.sensivity = sensivity

        self.up = Vec3(0, 1, 0)
        self.right = Vec3(1, 0, 0)
        self.forward = Vec3(0, 0, -1)
        self.yaw = yaw
        self.pitch = pitch

        self.m_view = self.get_view_matrix()
        self.m_proj = self.get_projection_matrix()

    def look_at(self, position: Vec3, target: Vec3, up: Vec3):
        f = (target - position).normalize()
        u = up.normalize()
        s = f.cross(u)
        u = s.cross(f)

        return Mat4([s.x, u.x, -f.x, 0.0,
                    s.y, u.y, -f.y, 0.0,
                    s.z, u.z, -f.z, 0.0,
                    -s.dot(position), -u.dot(position), f.dot(position), 1.0])

    def rotate(self, mouse_dx, mouse_dy):
        self.yaw += mouse_dx * self.sensivity
        self.pitch -= mouse_dy * self.sensivity
        self.pitch = max(-89, min(89, self.pitch))

    def update_camera_vectors(self):
        yaw, pitch = radians(self.yaw), radians(self.pitch)

        self.forward.x = cos(yaw) * cos(pitch)
        self.forward.y = sin(pitch)
        self.forward.z = sin(yaw) * cos(pitch)

        self.forward = self.forward.normalize()
        self.right = self.forward.cross(self.up).normalize()
        self.up = self.right.cross(self.forward).normalize()

    def update(self, mouse_dx, mouse_dy, forward, backward, left, right, up, down):
        self.move(forward, backward, left, right, up, down)
        self.rotate(mouse_dx, mouse_dy)

        self.update_camera_vectors()
        self.m_view = self.get_view_matrix()

    def move(self, forward, backward, left, right, up, down):
        v = self.speed * self.app.dt
        velocity = Vec3(v, v, v)

        if forward:
            self.position += self.forward * velocity
        if backward:
            self.position -= self.forward * velocity
        if right:
            self.position += self.right * velocity
        if left:
            self.position -= self.right * velocity
        if up:
            self.position -= self.up * velocity
        if down:
            self.position += self.up * velocity

    def get_view_matrix(self):
        return self.look_at(position=self.position, target=self.position + self.forward, up=self.up)

    def get_projection_matrix(self):
        return Mat4.perspective_projection(self.aspect_ratio, self.near, self.far, self.fov)


