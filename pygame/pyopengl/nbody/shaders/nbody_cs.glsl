#version 450 core

#define XGROUPSIZE  XGROUPSIZE_VAL
#define YGROUPSIZE  YGROUPSIZE_VAL
#define ZGROUPSIZE  ZGROUPSIZE_VAL
#define NB_BODY     NB_BODY_VAL

// TODO set as uniform
const float EPS     = 0.3;
const float DT      = 1.0/256.0;
const float EPS2    = EPS * EPS;
const float HALF_DT = 0.5 * DT;

//uniform int nb_body;

layout(local_size_x=XGROUPSIZE, local_size_y=YGROUPSIZE, local_size_z=ZGROUPSIZE) in;

struct Body
{
    vec4 pos; // x, y, z, w=mass
    vec4 col; // r, g, b, a
    vec4 vel; // vx, vy, vz, w=radius
    vec4 acc; // ax, ay, az, w=bodyID
};

layout(std430, binding=0) buffer bodies_in
{
    Body bodies[];
} IN;


void main()
{
    int current_index = int(gl_GlobalInvocationID);

    // if went past number of particles, skip
    //if (current_index >= NB_BODY_VAL + XGROUPSIZE) return;

    // leap 1/2
    IN.bodies[current_index].vel.xyz += IN.bodies[current_index].acc.xyz * HALF_DT;
    IN.bodies[current_index].pos.xyz += IN.bodies[current_index].vel.xyz * DT;

    // acc
    for (int j=0; j < IN.bodies.length(); j++) {
        if(IN.bodies[current_index].acc.w != IN.bodies[j].acc.w) { // body ID

            vec3 dr = IN.bodies[j].pos.xyz - IN.bodies[current_index].pos.xyz;

            float dr2 = dot(dr, dr);
            dr2 += EPS2;

            float phi = IN.bodies[j].pos.w / (sqrt(dr2) * dr2);

            IN.bodies[current_index].acc.xyz += dr.xyz * phi;
       }
    }

    // leap 1/2
    IN.bodies[current_index].vel.xyz += IN.bodies[current_index].acc.xyz * HALF_DT;
    IN.bodies[current_index].acc = vec4(0, 0, 0, IN.bodies[current_index].acc.w);

    // ensure that all threads are done reading particle data before continuing
    barrier();
    memoryBarrier();
}