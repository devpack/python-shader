#version 330 core

//layout(location = 0) in vec2 in_position;
layout(location = 0) in vec3 vertexPosition;

void main() {
    //gl_Position = vec4(in_position, 0.0, 1.0);
    gl_Position = vec4(vertexPosition, 1.0);
}