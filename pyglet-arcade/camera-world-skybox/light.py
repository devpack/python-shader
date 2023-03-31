from pyglet.math import Mat4, Vec3

class Light:
    def __init__(self, position=Vec3(50, 50, -10), color=Vec3(1, 1, 1)):
        self.position = position
        self.color = color
        self.direction = Vec3(0, 0, 0)
        # intensities
        self.Ia = Vec3(0.2, 0.2, 0.2) * self.color  # ambient
        self.Id = Vec3(0.8, 0.8, 0.8) * self.color  # diffuse
        self.Is = Vec3(1.0, 1.0, 1.0) * self.color  # specular
        # view matrix
        self.m_view_light = self.get_view_matrix()

    def look_at(self, position: Vec3, target: Vec3, up: Vec3):
        f = (target - position).normalize()
        u = up.normalize()
        s = f.cross(u)
        u = s.cross(f)

        return Mat4([s.x, u.x, -f.x, 0.0,
                    s.y, u.y, -f.y, 0.0,
                    s.z, u.z, -f.z, 0.0,
                    -s.dot(position), -u.dot(position), f.dot(position), 1.0])

    def get_view_matrix(self):
        return self.look_at(self.position, self.direction, Vec3(0, 1, 0))