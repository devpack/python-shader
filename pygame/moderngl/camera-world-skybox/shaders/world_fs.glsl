#version 330 core

layout (location = 0) out vec4 fragColor;

in vec2 uv_0;
in vec3 normal;
in vec3 fragPos;

uniform vec3 camPos;

uniform sampler2D u_texture_0;
uniform vec2 u_resolution;

struct Light {
    vec3 position;
    vec3 Ia;
    vec3 Id;
    vec3 Is;
};

uniform Light light;

const int SPECULAR_STRENGHT = 32;

vec3 getLight(vec3 color) {
    vec3 Normal = normalize(normal);

    // ambient light
    vec3 ambient = light.Ia;

    // diffuse light
    vec3 lightDir = normalize(light.position - fragPos);
    float diff = max(0, dot(lightDir, Normal));
    vec3 diffuse = diff * light.Id;

    // specular light
    vec3 viewDir = normalize(camPos - fragPos);
    vec3 reflectDir = reflect(-lightDir, Normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0), SPECULAR_STRENGHT);
    vec3 specular = spec * light.Is;

    //return color * (ambient + (diffuse + specular) * shadow);

    return color * (ambient + diffuse + specular);
}


void main() {
    //vec3 color = vec3(1.0, 0.0, 0.0); // solid red
    //vec3 color = vec3(uv_0, 0.0); // rg shade

    vec3 color = texture(u_texture_0, uv_0).rgb;
    color = getLight(color);
    fragColor = vec4(color, 1.0);
}









