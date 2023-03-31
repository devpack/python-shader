#version 450 core

layout (location = 0) in vec4 in_position;
layout (location = 1) in vec4 in_color;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

//out vec4 body_color;
out float body_color_dist;

void main() {
    vec4 model_pos = m_model * vec4(in_position.xyz, 1.0);
	vec4 view_model_pos = m_view * model_pos;
	gl_Position = m_proj * view_model_pos;

	float dist = length(view_model_pos);
	float psize = 32. / dist;
	gl_PointSize = psize;

	//body_color_dist = model_pos.z;
	body_color_dist = view_model_pos.z;
    //body_color = in_color;
}