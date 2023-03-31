#version 330 core

layout (location=0) in vec3 vertexPosition;
layout (location=1) in vec4 vertexColor;

uniform mat4 m_proj;
uniform mat4 m_model;

out vec4 fragColor;

void main()
{
    vec4 model_pos = m_model * vec4(vertexPosition, 1.0);
	//gl_Position = m_proj * model_pos;
	gl_Position = m_proj * m_view * model_pos;

    fragColor = vertexColor;
}