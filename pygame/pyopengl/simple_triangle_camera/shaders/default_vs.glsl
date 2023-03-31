#version 330 core

layout (location=0) in vec3 vertexPos;
layout (location=1) in vec3 vertexColor;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

out vec3 fragmentColor;

void main()
{
    vec4 model_pos = m_model * vec4(vertexPos, 1.0);
	gl_Position = m_proj * m_view * model_pos;

    fragmentColor = vertexColor;
}