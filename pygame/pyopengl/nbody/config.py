import time, collections

# ----------------------------------------------------------------------------------------------------------------------

SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 800
FONT_SIZE     = 32
MAX_FPS       = 512

# camera
CAM_POS = (0, 0, 20)
FOV = 50
NEAR = 0.1
FAR = 2000
SPEED = 0.01
SENSITIVITY = 0.07

GRAB_MOUSE = False

# ----------------------------------------------------------------------------------------------------------------------
USE_COMPUTE_SHADER = 1

XGROUPSIZE = 32 # compute shader nb threads
YGROUPSIZE = 1
ZGROUPSIZE = 1

NB_BODY = 1024 *1

EPS     = 0.3      # soft
DT      = 1.0/256.0 # time step
EPS2    = EPS * EPS
HALF_DT = 0.5 * DT

POSX    = 0
POSY    = 1
POSZ    = 2
MASS    = 3
COLR    = 4
COLG    = 5
COLB    = 6
COLA    = 7
VELX    = 8
VELY    = 9
VELZ    = 10
RADIUS  = 11
ACCX    = 12
ACCY    = 13
ACCZ    = 14
BODY_ID = 15

# ----------------------------------------------------------------------------------------------------------------------

class FPSCounter:
    def __init__(self):
        self.time = time.perf_counter()
        self.frame_times = collections.deque(maxlen=60)

    def tick(self):
        t1 = time.perf_counter()
        dt = t1 - self.time
        self.time = t1
        self.frame_times.append(dt)

    def get_fps(self):
        total_time = sum(self.frame_times)
        if total_time == 0:
            return 0
        else:
            return len(self.frame_times) / sum(self.frame_times)
