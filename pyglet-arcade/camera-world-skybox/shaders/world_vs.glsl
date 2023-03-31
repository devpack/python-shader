#version 330 core

in vec2 in_texcoord_0;
in vec3 in_normal;
in vec3 in_position;

out vec2 uv_0;
out vec3 normal;
out vec3 fragPos;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_view_light;
uniform mat4 m_model;

varying vec3 point_color;

void main() {
    uv_0 = in_texcoord_0;
    fragPos = vec3(m_model * vec4(in_position, 1.0));
    normal = mat3(transpose(inverse(m_model))) * normalize(in_normal);

    vec4 model_pos = m_model * vec4(in_position, 1.0);
	gl_Position = m_proj * m_view * model_pos;
}