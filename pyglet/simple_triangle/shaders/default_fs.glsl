#version 450

in vec4 fragColor;
out vec4 finalColor;
//void main()
//{
//    finalColor = fragColor;
//}

//in vec4 texture_coords;
//out vec4 final_colors;

//uniform sampler2D our_texture;

void main()
{
    //final_colors = texture(our_texture, texture_coords.xy);
    finalColor = fragColor;
    //finalColor = vec4(1.0, 0.0, 0.0, 1.0);
}