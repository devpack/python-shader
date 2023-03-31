#version 330 core
in vec3 vertexPosition;
in vec4 vertexColor;

out vec4 fragColor;

uniform mat4 m_proj;
uniform mat4 m_model;
uniform mat4 m_view;

//in vec3 tex_coords;
//out vec4 texture_coords;

uniform WindowBlock
{                       // This UBO is defined on Window creation, and available
    mat4 projection;    // in all Shaders. You can modify these matrixes with the
    mat4 view;          // Window.view and Window.projection properties.
} window;

void main()
{
    vec4 model_pos = m_model * vec4(vertexPosition, 1.0);
	//gl_Position = m_proj * model_pos;
	gl_Position = m_proj * m_view * model_pos;

    //gl_Position = m_proj * vec4(vertexPosition, 1.0);
    //gl_Position = vec4(vertexPosition, 1.0);

    //texture_coords = tex_coords;
    fragColor = vertexColor;
}
