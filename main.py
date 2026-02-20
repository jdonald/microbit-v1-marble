"""
micro:bit V2 Marble Puzzle

Tilt the micro:bit to roll a marble (bright LED) into a receptacle
(U-shaped pocket of dim wall LEDs with a blinking target inside).
Uses the V2 built-in speaker for collision and victory sound effects.
"""
from microbit import *
import random
import audio

# -- Physics constants --
ACCEL_SCALE = 0.00004   # milli-g to velocity per tick
DAMPING = 0.85           # friction per tick
MAX_SPEED = 0.4          # hard cap to prevent tunneling
DT = 50                  # ms per tick (~20 FPS)

# -- Display constants --
BR_MARBLE = 9
BR_TARGET = 5
BR_WALL = 2
BLINK_MS = 300           # target blink half-period

# -- Level generation --
MIN_DIST = 3             # minimum Manhattan distance marble-to-target

# -- Win animation --
WIN_MS = 1000
STAR = Image("90509:09990:99999:09990:90509")

# -- Sound effects (V2 built-in speaker) --
# Short low thud for wall/edge collisions
SFX_BUMP = SoundEffect(
    freq_start=600, freq_end=150, duration=80,
    vol_start=180, vol_end=0,
    waveform=SoundEffect.WAVEFORM_NOISE,
    shape=SoundEffect.SHAPE_LOG
)
# Rising cheerful tone for victory
SFX_WIN = SoundEffect(
    freq_start=600, freq_end=1400, duration=400,
    vol_start=200, vol_end=200,
    waveform=SoundEffect.WAVEFORM_SINE,
    shape=SoundEffect.SHAPE_CURVE
)
# Minimum speed to trigger a bump sound (avoids spamming while resting against wall)
BUMP_SPEED_MIN = 0.05

# Wall offsets by opening direction (relative to target cell)
# 'N' = open toward top (y-1), walls left/right/below
WALL_OFFSETS = {
    0: [(-1, 0), (1, 0), (0, 1)],   # N
    1: [(-1, 0), (1, 0), (0, -1)],  # S
    2: [(0, -1), (0, 1), (-1, 0)],  # E
    3: [(0, -1), (0, 1), (1, 0)],   # W
}


def rp(v):
    """Round a float position to the nearest grid index (0-4)."""
    r = int(v + 0.5)
    if r < 0:
        return 0
    if r > 4:
        return 4
    return r


def make_walls(tx, ty, d):
    """Return set of wall (x,y) tuples for direction d."""
    s = set()
    for dx, dy in WALL_OFFSETS[d]:
        s.add((tx + dx, ty + dy))
    return s


def gen_receptacle():
    """Generate a random receptacle. Returns (tx, ty, walls_set, direction)."""
    d = random.randint(0, 3)
    # Determine valid ranges so all walls stay in 0..4
    if d == 0:    # N: walls at tx-1, tx+1, ty+1
        tx = random.randint(1, 3)
        ty = random.randint(0, 3)
    elif d == 1:  # S: walls at tx-1, tx+1, ty-1
        tx = random.randint(1, 3)
        ty = random.randint(1, 4)
    elif d == 2:  # E: walls at ty-1, ty+1, tx-1
        tx = random.randint(1, 4)
        ty = random.randint(1, 3)
    else:         # W: walls at ty-1, ty+1, tx+1
        tx = random.randint(0, 3)
        ty = random.randint(1, 3)
    return tx, ty, make_walls(tx, ty, d)


def gen_start(tx, ty, walls):
    """Pick a random start position far from the target, avoiding walls."""
    cands = []
    for x in range(5):
        for y in range(5):
            if (x, y) != (tx, ty) and (x, y) not in walls:
                if abs(x - tx) + abs(y - ty) >= MIN_DIST:
                    cands.append((x, y))
    if not cands:
        # Relax distance constraint
        for x in range(5):
            for y in range(5):
                if (x, y) != (tx, ty) and (x, y) not in walls:
                    cands.append((x, y))
    c = random.choice(cands)
    return float(c[0]), float(c[1])


def new_level():
    tx, ty, walls = gen_receptacle()
    mx, my = gen_start(tx, ty, walls)
    return tx, ty, walls, mx, my, 0.0, 0.0


def update(mx, my, vx, vy, walls):
    """Apply accelerometer forces, move marble, handle collisions.
    Returns (mx, my, vx, vy, hit) where hit is True if a collision occurred."""
    ax = accelerometer.get_x()
    ay = accelerometer.get_y()

    vx = vx * DAMPING + ax * ACCEL_SCALE
    vy = vy * DAMPING + ay * ACCEL_SCALE

    # Clamp speed
    sp = (vx * vx + vy * vy) ** 0.5
    if sp > MAX_SPEED:
        f = MAX_SPEED / sp
        vx *= f
        vy *= f

    # Track pre-collision speed for sound triggering
    pre_speed = (vx * vx + vy * vy) ** 0.5
    hit = False

    # -- X movement + collision --
    nx = mx + vx
    if nx < 0.0:
        nx = 0.0
        hit = True
        vx = 0.0
    elif nx > 4.0:
        nx = 4.0
        hit = True
        vx = 0.0
    if (rp(nx), rp(my)) in walls:
        nx = mx
        hit = True
        vx = 0.0

    # -- Y movement + collision --
    ny = my + vy
    if ny < 0.0:
        ny = 0.0
        hit = True
        vy = 0.0
    elif ny > 4.0:
        ny = 4.0
        hit = True
        vy = 0.0
    if (rp(nx), rp(ny)) in walls:
        ny = my
        hit = True
        vy = 0.0

    # Only count as audible hit if marble was moving fast enough
    hit = hit and pre_speed >= BUMP_SPEED_MIN

    return nx, ny, vx, vy, hit


def render(mx, my, tx, ty, walls, now):
    display.clear()
    # Walls
    for wx, wy in walls:
        display.set_pixel(wx, wy, BR_WALL)
    # Target (blinking)
    if (now // BLINK_MS) % 2 == 0:
        display.set_pixel(tx, ty, BR_TARGET)
    # Marble (drawn last, on top)
    display.set_pixel(rp(mx), rp(my), BR_MARBLE)


def win():
    audio.play(SFX_WIN, wait=False)
    display.show(STAR)
    sleep(WIN_MS)
    display.clear()
    sleep(200)


# -- Main --
tx, ty, walls, mx, my, vx, vy = new_level()

while True:
    t0 = running_time()
    mx, my, vx, vy, hit = update(mx, my, vx, vy, walls)

    if hit:
        audio.play(SFX_BUMP, wait=False)

    if rp(mx) == tx and rp(my) == ty:
        win()
        tx, ty, walls, mx, my, vx, vy = new_level()
        continue

    render(mx, my, tx, ty, walls, running_time())

    el = running_time() - t0
    if el < DT:
        sleep(DT - el)
