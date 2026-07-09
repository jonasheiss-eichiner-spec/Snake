import pygame
import random
import sys
import math
import os

VIRTUAL_W = 768
VIRTUAL_H = 432

UI_THEMES = [
    {"name": "Dark Mode",   "bg": (45, 49, 56),    "top": (28, 31, 36),    "border": (30, 34, 40),    "text": (255, 255, 255)},
    {"name": "Light Mode",  "bg": (230, 235, 240), "top": (200, 205, 210), "border": (180, 185, 190), "text": (30, 30, 30)},
    {"name": "Hacker",      "bg": (10, 15, 10),    "top": (5, 8, 5),       "border": (20, 35, 20),    "text": (0, 255, 0)}
]

HUD_LAYOUTS = ["Top Bar", "Bottom Bar", "Left Panel", "Right Panel"]

SNAKE_SHADOW = (0, 0, 0, 35)
BG_LIGHT = (170, 215, 81)
BG_DARK = (162, 209, 73)
MENU_HIGHLIGHT = (255, 215, 0)

STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2
STATE_SETTINGS = 3
STATE_SHOP = 4
STATE_INDEX = 5

global_coins = 0
unlocked_skins = ["classic"]
p1_skin = "classic"
p2_skin = "classic"
num_players = 1
current_theme_idx = 0
hud_layout_idx = 0
DEFAULT_P1_KEYS = {'up': pygame.K_w, 'down': pygame.K_s, 'left': pygame.K_a, 'right': pygame.K_d}
DEFAULT_P2_KEYS = {'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT}
P1_KEYS = DEFAULT_P1_KEYS.copy()
P2_KEYS = DEFAULT_P2_KEYS.copy()

# --- SOUND SETTINGS ---
sound_enabled = True
sounds = {}

def safe_key_name(k):
    try:
        return pygame.key.name(k).upper()
    except Exception:
        return "KEY"

MAIN_MODES = [
    {"id": "classic", "name": "Classic Mode"},
    {"id": "portal",  "name": "Portal Mode"},
    {"id": "maze",    "name": "Labyrinth"},
    {"id": "swarm",   "name": "Swarm Mode"},
    {"id": "turbo",   "name": "Turbo Speed"},
    {"id": "custom",  "name": "Custom Game"}
]

SIZE_MODES = [
    {"id": "6",  "name": "Tiny (6x6)",       "grid": 6},
    {"id": "8",  "name": "Small (8x8)",      "grid": 8},
    {"id": "12", "name": "Medium (12x12)",   "grid": 12},
    {"id": "16", "name": "Standard (16x16)", "grid": 16},
    {"id": "20", "name": "Large (20x20)",    "grid": 20},
    {"id": "24", "name": "Huge (24x24)",     "grid": 24},
    {"id": "32", "name": "Giant (32x32)",    "grid": 32},
    {"id": "back", "name": "< Back",         "grid": 0}
]

SPEED_MODES = [
    {"id": "0.5x",    "name": "Slow (0.5x)",        "speed_mult": 0.5},
    {"id": "0.75x",   "name": "Chill (0.75x)",      "speed_mult": 0.75},
    {"id": "1.0x",    "name": "Normal (1.0x)",      "speed_mult": 1.0},
    {"id": "1.25x",   "name": "Fast (1.25x)",       "speed_mult": 1.25},
    {"id": "1.5x",    "name": "Very Fast (1.5x)",   "speed_mult": 1.5},
    {"id": "1.75x",   "name": "Insane (1.75x)",     "speed_mult": 1.75},
    {"id": "2.0x",    "name": "God Mode (2.0x)",    "speed_mult": 2.0},
    {"id": "back",    "name": "< Back",             "speed_mult": 0}
]

custom_cfg = {
    "grid": 16, "speed": 10.0, "apples": 3, 
    "gold_pct": 10, "magic_pct": 15, 
    "wrap": False, "maze": False
}

def get_mode_config(base_mode, size_mode, speed_mode=None):
    grid = size_mode["grid"]
    base_id = base_mode["id"]
    speed, apples, inc, wrap, maze = 6.0, 1, 0.0, False, False
    mode_id, mode_name = f"{base_id}_{grid}", f"{base_mode['name']} ({grid}x{grid})"
    if base_id == "classic": 
        speed = 5.0 + (grid / 8.0)
        apples = max(3, grid // 5)
    elif base_id == "portal": 
        speed = 6.0 + (grid / 8.0)
        apples = max(3, grid // 5)
        wrap = True
    elif base_id == "maze": 
        speed = 4.5 + (grid / 10.0)
        apples = max(3, grid // 4)
        maze = True
    elif base_id == "swarm": 
        speed = 5.5 + (grid / 10.0)
        apples = max(5, (grid * grid) // 12)
    elif base_id == "turbo":
        speed = 15.0
        apples = max(3, grid // 5)
    if speed_mode and speed_mode["id"] != "back":
        speed *= speed_mode["speed_mult"]
        mode_id = f"{base_id}_{grid}_{speed_mode['id']}"
        mode_name = f"{base_mode['name'].split()[0]} ({grid}x{grid}) {speed_mode['id']}"
    return {
        "id": mode_id, "name": mode_name, "grid": grid, "speed": speed, "apples": apples, 
        "inc": inc, "wrap": wrap, "maze": maze, "gold_chance": 0.10, "magic_chance": 0.15
    }

def get_apple_color(atype):
    if atype == 'gold': return (255, 200, 0)
    if atype == 'ghost': return (180, 50, 255)
    if atype == 'ice': return (50, 255, 255)
    if atype == 'magnet': return (50, 100, 255)
    return (231, 71, 29)

def get_apple_texture(cell_size, atype='red'):
    cell_size = max(1, cell_size)
    surf = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
    art = [
        "..gg......", "...g......", ".rrrrr....", "rrwwrrr...", "rrwwrrrr..",
        "rrrrrrrr..", "rrrrrrrr..", ".rrrrrr...", "..rrrr....", ".........."
    ]
    color_map = {'g': (75, 156, 43), 'r': get_apple_color(atype), 'w': (255, 255, 255)}
    for y, row in enumerate(art):
        for x, char in enumerate(row):
            if char in color_map:
                px_start, py_start = int((x / 10.0) * cell_size), int((y / 10.0) * cell_size)
                px_end, py_end = int(((x + 1) / 10.0) * cell_size), int(((y + 1) / 10.0) * cell_size)
                pygame.draw.rect(surf, color_map[char], (px_start, py_start, px_end - px_start, py_end - py_start))
    return surf

def get_wall_texture(cell_size):
    cell_size = max(1, cell_size)
    surf = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
    pygame.draw.rect(surf, (90, 95, 100), (0, 0, cell_size, cell_size))
    pygame.draw.rect(surf, (120, 125, 130), (0, 0, cell_size, cell_size), max(1, cell_size//8))
    pygame.draw.rect(surf, (60, 65, 70), (0, cell_size - cell_size//8, cell_size, cell_size//8))
    pygame.draw.rect(surf, (60, 65, 70), (cell_size - cell_size//8, 0, cell_size//8, cell_size))
    return surf

def spawn_foods(players, count, grid_size, walls, gold_chance=0.10, magic_chance=0.15):
    foods = []
    for _ in range(count):
        f = spawn_single_food(players, foods, grid_size, walls, gold_chance, magic_chance)
        if f: foods.append(f)
    return foods

def spawn_single_food(players, current_foods, grid_size, walls, gold_chance=0.10, magic_chance=0.15):
    occupied = set([(f['x'], f['y']) for f in current_foods] + walls)
    for p in players: occupied.update(p.body)
    if len(occupied) >= grid_size * grid_size: return None 
    while True:
        pos = (random.randint(0, grid_size - 1), random.randint(0, grid_size - 1))
        if pos not in occupied:
            r = random.random()
            if r < gold_chance: atype = 'gold'
            elif r < gold_chance + magic_chance: atype = random.choice(['ghost', 'ice', 'magnet'])
            else: atype = 'red'
            return {'x': pos[0], 'y': pos[1], 'type': atype}

class Player:
    def __init__(self, pid, grid, skin, keys):
        self.pid = pid
        cx = grid // 2
        cy = grid // 2 + (2 if pid == 2 else -2) if num_players == 2 else grid // 2
        self.body = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.old_body = self.body.copy()
        self.dir = (1, 0)
        self.queue = []
        self.score = 0
        self.pending_growth = 0
        self.alive = True
        self.skin = skin
        self.keys = keys
        self.ghost_timer = 0.0
        self.magnet_timer = 0.0

def hsv_to_rgb(h, s, v):
    h = float(h); s = float(s) / 100.0; v = float(v) / 100.0
    h60 = h / 60.0
    h60f = math.floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if hi == 0: r, g, b = v, t, p
    elif hi == 1: r, g, b = q, v, p
    elif hi == 2: r, g, b = p, v, t
    elif hi == 3: r, g, b = p, q, v
    elif hi == 4: r, g, b = t, p, v
    elif hi == 5: r, g, b = v, p, q
    return int(r * 255), int(g * 255), int(b * 255)

def get_snake_color(skin, index, length, time_ms):
    if skin == 'neon':
        factor = 1.0 - 0.3 * (index / max(1, length))
        return (int(0 * factor), int(255 * factor), int(255 * factor))
    elif skin == 'rainbow':
        hue = (time_ms/5.0 + index * 15) % 360
        return hsv_to_rgb(hue, 100, 100)
    elif skin == 'mech':
        if index == 0: return (255, 100, 0)
        factor = 1.0 - 0.4 * (index / max(1, length))
        return (int(160 * factor), int(160 * factor), int(170 * factor))
    else:
        factor = 1.0 - 0.45 * (index / max(1, length))
        return (int(74 * factor), int(117 * factor), int(232 * factor))

FONT_CACHE = {}

def draw_text(surface, text, size, x, y, align="center", color=None, shadow=True, scale=1.0, alpha=255):
    if color is None: color = UI_THEMES[current_theme_idx]["text"]
    if size not in FONT_CACHE:
        FONT_CACHE[size] = pygame.font.SysFont("monospace", size, bold=True)
    font = FONT_CACHE[size]
    text_surf = font.render(text, False, color)
    if alpha < 255: text_surf.set_alpha(alpha)
    if scale != 1.0:
        new_w, new_h = max(1, int(text_surf.get_width() * scale)), max(1, int(text_surf.get_height() * scale))
        text_surf = pygame.transform.scale(text_surf, (new_w, new_h))
    rect = text_surf.get_rect()
    if align == "center": rect.center = (x, y)
    elif align == "topleft": rect.topleft = (x, y)
    elif align == "topright": rect.topright = (x, y)
    if shadow:
        shadow_surf = font.render(text, False, (0, 0, 0))
        if alpha < 255: shadow_surf.set_alpha(alpha)
        if scale != 1.0: shadow_surf = pygame.transform.scale(shadow_surf, (text_surf.get_width(), text_surf.get_height()))
        shadow_rect = shadow_surf.get_rect()
        if align == "center": shadow_rect.center = (x + 2, y + 2)
        elif align == "topleft": shadow_rect.topleft = (x + 2, y + 2)
        elif align == "topright": shadow_rect.topright = (x + 2, y + 2)
        surface.blit(shadow_surf, shadow_rect)
    surface.blit(text_surf, rect)

def get_growing_rect(px, py, dx, dy, p, cell_size, bx, by):
    x, y = bx + px * cell_size, by + py * cell_size
    ip = max(0, int(cell_size * p))
    if dx == 1:   return (x, y, ip, cell_size)
    if dx == -1:  return (x + cell_size - ip, y, ip, cell_size)
    if dy == 1:   return (x, y, cell_size, ip)
    if dy == -1:  return (x, y + cell_size - ip, cell_size, ip)
    return (x, y, cell_size, cell_size)

def get_shrinking_rect(px, py, dx, dy, p, cell_size, bx, by):
    x, y = bx + px * cell_size, by + py * cell_size
    ip = max(0, int(cell_size * p))
    if dx == 1:   return (x + ip, y, max(0, cell_size - ip), cell_size)
    if dx == -1:  return (x, y, max(0, cell_size - ip), cell_size)
    if dy == 1:   return (x, y + ip, cell_size, max(0, cell_size - ip))
    if dy == -1:  return (x, y, cell_size, max(0, cell_size - ip))
    return (x, y, cell_size, cell_size)

def get_board_bounds(grid, layout_name):
    if layout_name in ["Top Bar", "Bottom Bar"]:
        max_w = VIRTUAL_W - 20
        max_h = VIRTUAL_H - 55 - 20
    else:
        max_w = VIRTUAL_W - 160 - 20
        max_h = VIRTUAL_H - 20
    cell = max(1, min(max_w // grid, max_h // grid))
    board_w, board_h = grid * cell, grid * cell
    if layout_name == "Top Bar":
        bx = (VIRTUAL_W - board_w) // 2
        by = 55 + (VIRTUAL_H - 55 - board_h) // 2
    elif layout_name == "Bottom Bar":
        bx = (VIRTUAL_W - board_w) // 2
        by = (VIRTUAL_H - 55 - board_h) // 2 - 5
    elif layout_name == "Left Panel":
        bx = 160 + (VIRTUAL_W - 160 - board_w) // 2
        by = (VIRTUAL_H - board_h) // 2
    elif layout_name == "Right Panel":
        bx = 10 + (VIRTUAL_W - 160 - board_w) // 2
        by = (VIRTUAL_H - board_h) // 2
    return cell, bx, by

def draw_head_eyes(surface, vx, vy, direction, cell_size, bx, by, time_ms, offset=(0,0), skin='classic'):
    px, py = bx + int(vx * cell_size) + offset[0], by + int(vy * cell_size) + offset[1]
    blink = (time_ms % 4000 > 3800)
    def draw_r(color, gx, gy, gw, gh):
        x_st, x_end = px + int((gx / 10.0) * cell_size), px + int(((gx + gw) / 10.0) * cell_size)
        y_st, y_end = py + int((gy / 10.0) * cell_size), py + int(((gy + gh) / 10.0) * cell_size)
        pygame.draw.rect(surface, color, (x_st, y_st, x_end - x_st, y_end - y_st))
    w, b = (255, 255, 255), (0, 0, 0)
    if skin == 'mech': w, b = (255, 100, 0), (255, 200, 0)
    elif skin == 'neon': w, b = (0, 255, 255), (255, 255, 255)
    t_c = (220, 50, 50)
    if time_ms % 2000 < 200 and skin != 'mech':
        if direction == (1, 0): draw_r(t_c, 10, 4, 3, 2); draw_r(t_c, 13, 3, 1, 1); draw_r(t_c, 13, 6, 1, 1)
        elif direction == (-1, 0): draw_r(t_c, -3, 4, 3, 2); draw_r(t_c, -4, 3, 1, 1); draw_r(t_c, -4, 6, 1, 1)
        elif direction == (0, -1): draw_r(t_c, 4, -3, 2, 3); draw_r(t_c, 3, -4, 1, 1); draw_r(t_c, 6, -4, 1, 1)
        elif direction == (0, 1): draw_r(t_c, 4, 10, 2, 3); draw_r(t_c, 3, 13, 1, 1); draw_r(t_c, 6, 13, 1, 1)
    if direction == (1, 0):
        if not blink: draw_r(w, 6, 1, 3, 3); draw_r(b, 8, 2, 1, 1); draw_r(w, 6, 6, 3, 3); draw_r(b, 8, 7, 1, 1)
        else: draw_r(b, 6, 2, 3, 1); draw_r(b, 6, 7, 3, 1)
    elif direction == (-1, 0):
        if not blink: draw_r(w, 1, 1, 3, 3); draw_r(b, 1, 2, 1, 1); draw_r(w, 1, 6, 3, 3); draw_r(b, 1, 7, 1, 1)
        else: draw_r(b, 1, 2, 3, 1); draw_r(b, 1, 7, 3, 1)
    elif direction == (0, -1):
        if not blink: draw_r(w, 1, 1, 3, 3); draw_r(b, 2, 1, 1, 1); draw_r(w, 6, 1, 3, 3); draw_r(b, 7, 1, 1, 1)
        else: draw_r(b, 2, 1, 1, 3); draw_r(b, 7, 1, 1, 3)
    elif direction == (0, 1):
        if not blink: draw_r(w, 1, 6, 3, 3); draw_r(b, 2, 8, 1, 1); draw_r(w, 6, 6, 3, 3); draw_r(b, 7, 8, 1, 1)
        else: draw_r(b, 2, 6, 1, 3); draw_r(b, 7, 6, 1, 3)

def main():
    global global_coins, num_players, current_theme_idx, hud_layout_idx, p1_skin, p2_skin
    global P1_KEYS, P2_KEYS
    pygame.init()
    try:
        pygame.mixer.init(frequency=22050, size=-16, channels=1)
    except Exception:
        pass
    
    # Load sound effects
    global sounds
    sounds_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
    for key, filename in {
        "eat": "eat.wav",
        "gold_eat": "gold_eat.wav",
        "powerup": "powerup.wav",
        "game_over": "game_over.wav",
        "menu_move": "menu_move.wav",
        "menu_select": "menu_select.wav",
        "explosion": "explosion.wav",
        "win": "win.wav",
    }.items():
        path = os.path.join(sounds_dir, filename)
        try:
            snd = pygame.mixer.Sound(path)
            snd.set_volume(0.4)
            sounds[key] = snd
        except Exception:
            sounds[key] = None
    
    def play_sound(key):
        if sound_enabled and sounds.get(key):
            try:
                sounds[key].play()
            except Exception:
                pass
    
    # Load background music
    bg_music = None
    bg_menu = None
    current_music = None
    sounds_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
    for key, filename, vol in [("bg_music", "bg_music.wav", 0.3), ("bg_menu", "bg_menu.wav", 0.25)]:
        path = os.path.join(sounds_dir, filename)
        try:
            snd = pygame.mixer.Sound(path)
            snd.set_volume(vol)
            if key == "bg_music": bg_music = snd
            else: bg_menu = snd
        except Exception:
            pass
    
    def play_music(track):
        nonlocal current_music
        try:
            if current_music == track:
                return
            # Stop current music
            if bg_music and (current_music == "game" or bg_music.get_num_channels() > 0):
                bg_music.stop()
            if bg_menu and (current_music == "menu" or bg_menu.get_num_channels() > 0):
                bg_menu.stop()
            current_music = track
            if track == "game" and bg_music:
                bg_music.play(-1)  # loop forever
            elif track == "menu" and bg_menu:
                bg_menu.play(-1)   # loop forever
        except Exception:
            pass
    
    # Start menu music immediately
    play_music("menu")
    
    current_w, current_h = 1280, 720
    screen = pygame.display.set_mode((current_w, current_h), pygame.RESIZABLE)
    pygame.display.set_caption("Snake 2.0 (Ultimate GitHub Edition)")
    clock = pygame.time.Clock()
    v_surf = pygame.Surface((VIRTUAL_W, VIRTUAL_H))
    shadow_surf = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
    is_fullscreen = False
    state = STATE_MENU
    menu_page = "main"
    selected_main_idx, selected_size_idx, selected_speed_idx = 0, 3, 2
    custom_idx = 0
    settings_idx, shop_idx = 0, 0
    highscores = {}
    current_mode, target_mode_dict = None, None
    cell, bx, by = 16, 0, 0
    players, foods, walls = [], [], []
    speed, move_progress, global_ice_timer = 0.0, 0.0, 0.0
    apple_textures = {}
    wall_tex = None
    win_game = False
    score_bump, shake, flash_alpha = 0.0, 0.0, 0.0
    particles, floating_texts = [], []
    transition_alpha = 0
    transitioning_to = None

    def start_game(mode_dict):
        nonlocal current_mode, bx, by, cell, players, foods, walls
        nonlocal speed, move_progress, apple_textures, wall_tex
        nonlocal state, win_game, score_bump, shake, particles, floating_texts, global_ice_timer
        current_mode = mode_dict
        grid, speed = current_mode["grid"], current_mode["speed"]
        layout_name = HUD_LAYOUTS[hud_layout_idx]
        cell, bx, by = get_board_bounds(grid, layout_name)
        apple_textures = {t: get_apple_texture(cell, t) for t in ['red', 'gold', 'ghost', 'ice', 'magnet']}
        wall_tex = get_wall_texture(cell)
        players = [Player(1, grid, p1_skin, P1_KEYS)]
        if num_players == 2: players.append(Player(2, grid, p2_skin, P2_KEYS))
        move_progress, global_ice_timer = 0.0, 0.0
        win_game = False
        score_bump, shake = 0.0, 0.0
        particles.clear(); floating_texts.clear()
        walls = []
        if current_mode.get("maze"):
            margin = grid // 4
            for i in range(margin, grid - margin):
                if i not in (grid//2 - 1, grid//2, grid//2 + 1):
                    walls.extend([(i, margin), (i, grid-margin-1), (margin, i), (grid-margin-1, i)])
        g_chance = current_mode.get("gold_chance", 0.10)
        m_chance = current_mode.get("magic_chance", 0.15)
        foods = spawn_foods(players, current_mode["apples"], grid, walls, g_chance, m_chance)
        state = STATE_PLAYING

    def spawn_explosion(fx, fy, cell_size, color):
        px, py = bx + fx * cell_size + cell_size // 2, by + fy * cell_size + cell_size // 2
        for _ in range(12):
            vx, vy = random.uniform(-cell_size*4, cell_size*4), random.uniform(-cell_size*4, cell_size*4)
            life = random.uniform(0.3, 0.6)
            particles.append({'x': px, 'y': py, 'vx': vx, 'vy': vy, 'life': life, 'max': life, 'color': color})

    def handle_eat(p, f, fx, fy):
        nonlocal speed, move_progress, win_game, score_bump, global_ice_timer
        global global_coins
        foods.remove(f)
        atype = f['type']
        pts = 5 if atype == 'gold' else 1
        p.pending_growth += pts
        p.score += pts
        global_coins += pts
        score_bump = 1.5 if atype == 'gold' else 1.0
        if atype == 'ghost': p.ghost_timer = 8.0
        elif atype == 'ice': global_ice_timer = 5.0
        elif atype == 'magnet': p.magnet_timer = 8.0
        speed += current_mode["inc"]
        c_color = get_apple_color(atype)
        # Play sound based on apple type
        if atype == 'gold':
            play_sound("gold_eat")
        else:
            play_sound("eat")
        if atype in ('ghost', 'ice', 'magnet'):
            play_sound("powerup")
        spawn_explosion(fx, fy, cell, c_color)
        floating_texts.append({
            'x': bx + fx*cell + cell//2, 'y': by + fy*cell, 
            'text': f"+{pts}", 'color': c_color, 'life': 1.0, 'cell': cell
        })
        grid = current_mode["grid"]
        if sum(len(pl.body) for pl in players) + len(walls) >= grid * grid: 
            win_game = True
            play_sound("win")
        else:
            g_chance = current_mode.get("gold_chance", 0.10)
            m_chance = current_mode.get("magic_chance", 0.15)
            new_food = spawn_single_food(players, foods, grid, walls, g_chance, m_chance)
            if new_food: foods.append(new_food)

    waiting_for_key = False
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        if dt > 0.1: dt = 0.1
        time_ms = pygame.time.get_ticks()
        theme_cfg = UI_THEMES[current_theme_idx]
        if score_bump > 0: score_bump = max(0, score_bump - dt * 5)
        if shake > 0: shake = max(0, shake - dt * 35)
        if flash_alpha > 0: flash_alpha = max(0, flash_alpha - dt * 600)
        if transition_alpha > 0 and transitioning_to is None:
            transition_alpha = max(0, transition_alpha - dt * 800)
        elif transitioning_to is not None:
            transition_alpha = min(255, transition_alpha + dt * 800)
            if transition_alpha >= 255:
                if transitioning_to == STATE_PLAYING:
                    start_game(target_mode_dict)
                    play_music("game")
                else:
                    state = transitioning_to
                    if state == STATE_MENU:
                        play_music("menu")
                    elif state in (STATE_SETTINGS, STATE_SHOP, STATE_INDEX):
                        play_music("menu")
                transitioning_to = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                try:
                    if bg_music: bg_music.stop()
                    if bg_menu: bg_menu.stop()
                except Exception:
                    pass
                running = False
            elif event.type == pygame.VIDEORESIZE:
                if not is_fullscreen:
                    current_w, current_h = max(300, event.w), max(300, event.h)
                    screen = pygame.display.set_mode((current_w, current_h), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    is_fullscreen = not is_fullscreen
                    if is_fullscreen: screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else: screen = pygame.display.set_mode((current_w, current_h), pygame.RESIZABLE)
                if transitioning_to is not None: continue
                if waiting_for_key and state == STATE_SETTINGS:
                    if event.key != pygame.K_ESCAPE:
                        if settings_idx == 0: P1_KEYS['up'] = event.key
                        elif settings_idx == 1: P1_KEYS['down'] = event.key
                        elif settings_idx == 2: P1_KEYS['left'] = event.key
                        elif settings_idx == 3: P1_KEYS['right'] = event.key
                        elif settings_idx == 4: P2_KEYS['up'] = event.key
                        elif settings_idx == 5: P2_KEYS['down'] = event.key
                        elif settings_idx == 6: P2_KEYS['left'] = event.key
                        elif settings_idx == 7: P2_KEYS['right'] = event.key
                    waiting_for_key = False
                    continue
                if state == STATE_MENU:
                    if event.key == pygame.K_ESCAPE:
                        if menu_page in ["size", "custom"]: menu_page = "main"
                        elif menu_page == "speed": menu_page = "size"
                        else: running = False
                    elif event.key == pygame.K_p and menu_page == "main":
                        num_players = 2 if num_players == 1 else 1
                    elif event.key == pygame.K_s and menu_page == "main":
                        transitioning_to = STATE_SETTINGS
                    elif event.key == pygame.K_c and menu_page == "main":
                        transitioning_to = STATE_SHOP
                    elif event.key == pygame.K_i and menu_page == "main":
                        transitioning_to = STATE_INDEX
                    elif event.key == pygame.K_UP:
                        play_sound("menu_move")
                        if menu_page == "main": selected_main_idx = (selected_main_idx - 1) % len(MAIN_MODES)
                        elif menu_page == "size": selected_size_idx = (selected_size_idx - 1) % len(SIZE_MODES)
                        elif menu_page == "speed": selected_speed_idx = (selected_speed_idx - 1) % len(SPEED_MODES)
                        elif menu_page == "custom": custom_idx = (custom_idx - 1) % 9
                    elif event.key == pygame.K_DOWN:
                        play_sound("menu_move")
                        if menu_page == "main": selected_main_idx = (selected_main_idx + 1) % len(MAIN_MODES)
                        elif menu_page == "size": selected_size_idx = (selected_size_idx + 1) % len(SIZE_MODES)
                        elif menu_page == "speed": selected_speed_idx = (selected_speed_idx + 1) % len(SPEED_MODES)
                        elif menu_page == "custom": custom_idx = (custom_idx + 1) % 9
                    elif event.key == pygame.K_LEFT and menu_page == "custom":
                        if custom_idx == 0: custom_cfg['grid'] = max(6, custom_cfg['grid'] - 2)
                        elif custom_idx == 1: custom_cfg['speed'] = max(3.0, custom_cfg['speed'] - 1.0)
                        elif custom_idx == 2: custom_cfg['apples'] = max(1, custom_cfg['apples'] - 1)
                        elif custom_idx == 3: custom_cfg['gold_pct'] = max(0, custom_cfg['gold_pct'] - 5)
                        elif custom_idx == 4: custom_cfg['magic_pct'] = max(0, custom_cfg['magic_pct'] - 5)
                        elif custom_idx == 5: custom_cfg['wrap'] = not custom_cfg['wrap']
                        elif custom_idx == 6: custom_cfg['maze'] = not custom_cfg['maze']
                    elif event.key == pygame.K_RIGHT and menu_page == "custom":
                        if custom_idx == 0: custom_cfg['grid'] = min(40, custom_cfg['grid'] + 2)
                        elif custom_idx == 1: custom_cfg['speed'] = min(40.0, custom_cfg['speed'] + 1.0)
                        elif custom_idx == 2: custom_cfg['apples'] = min(50, custom_cfg['apples'] + 1)
                        elif custom_idx == 3: custom_cfg['gold_pct'] = min(100, custom_cfg['gold_pct'] + 5)
                        elif custom_idx == 4: custom_cfg['magic_pct'] = min(100, custom_cfg['magic_pct'] + 5)
                        elif custom_idx == 5: custom_cfg['wrap'] = not custom_cfg['wrap']
                        elif custom_idx == 6: custom_cfg['maze'] = not custom_cfg['maze']
                    elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        if menu_page == "main" or menu_page == "size" or menu_page == "speed" or menu_page == "custom":
                            play_sound("menu_select")
                        if menu_page == "main":
                            if MAIN_MODES[selected_main_idx]["id"] == "custom":
                                menu_page = "custom"; custom_idx = 0
                            else: menu_page = "size"
                        elif menu_page == "size":
                            if SIZE_MODES[selected_size_idx]["id"] == "back": menu_page = "main"
                            else:
                                if MAIN_MODES[selected_main_idx]["id"] in ["turbo", "classic"]: menu_page = "speed"
                                else:
                                    target_mode_dict = get_mode_config(MAIN_MODES[selected_main_idx], SIZE_MODES[selected_size_idx])
                                    transitioning_to = STATE_PLAYING
                        elif menu_page == "speed":
                            if SPEED_MODES[selected_speed_idx]["id"] == "back": menu_page = "size"
                            else:
                                target_mode_dict = get_mode_config(MAIN_MODES[selected_main_idx], SIZE_MODES[selected_size_idx], SPEED_MODES[selected_speed_idx])
                                transitioning_to = STATE_PLAYING
                        elif menu_page == "custom":
                            if custom_idx == 7:
                                target_mode_dict = {
                                    "id": "custom_game", "name": "Custom Game",
                                    "grid": custom_cfg['grid'], "speed": custom_cfg['speed'],
                                    "apples": custom_cfg['apples'], "inc": 0.0,
                                    "wrap": custom_cfg['wrap'], "maze": custom_cfg['maze'],
                                    "gold_chance": custom_cfg['gold_pct'] / 100.0,
                                    "magic_chance": custom_cfg['magic_pct'] / 100.0
                                }
                                transitioning_to = STATE_PLAYING
                            elif custom_idx == 8:
                                menu_page = "main"
                elif state == STATE_SETTINGS:
                    if event.key == pygame.K_ESCAPE: transitioning_to = STATE_MENU
                    elif event.key == pygame.K_UP: play_sound("menu_move"); settings_idx = (settings_idx - 1) % 12
                    elif event.key == pygame.K_DOWN: play_sound("menu_move"); settings_idx = (settings_idx + 1) % 12
                    elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        if settings_idx < 8: waiting_for_key = True
                        elif settings_idx == 8: current_theme_idx = (current_theme_idx + 1) % len(UI_THEMES)
                        elif settings_idx == 9: hud_layout_idx = (hud_layout_idx + 1) % len(HUD_LAYOUTS)
                        elif settings_idx == 10:
                            P1_KEYS.update(DEFAULT_P1_KEYS)
                            P2_KEYS.update(DEFAULT_P2_KEYS)
                            current_theme_idx = 0
                            hud_layout_idx = 0
                        elif settings_idx == 11: transitioning_to = STATE_MENU
                elif state == STATE_SHOP:
                    shop_items = ["neon", "rainbow", "mech", "p1_cycle", "p2_cycle", "back"]
                    prices = {"neon": 100, "rainbow": 250, "mech": 500}
                    if event.key == pygame.K_ESCAPE: transitioning_to = STATE_MENU
                    elif event.key == pygame.K_UP: play_sound("menu_move"); shop_idx = (shop_idx - 1) % len(shop_items)
                    elif event.key == pygame.K_DOWN: play_sound("menu_move"); shop_idx = (shop_idx + 1) % len(shop_items)
                    elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        sel = shop_items[shop_idx]
                        if sel in prices and sel not in unlocked_skins:
                            if global_coins >= prices[sel]:
                                global_coins -= prices[sel]
                                unlocked_skins.append(sel)
                        elif sel == "p1_cycle":
                            idx = unlocked_skins.index(p1_skin)
                            p1_skin = unlocked_skins[(idx + 1) % len(unlocked_skins)]
                        elif sel == "p2_cycle":
                            idx = unlocked_skins.index(p2_skin)
                            p2_skin = unlocked_skins[(idx + 1) % len(unlocked_skins)]
                        elif sel == "back":
                            transitioning_to = STATE_MENU
                elif state == STATE_INDEX:
                    if event.key == pygame.K_ESCAPE: transitioning_to = STATE_MENU
                    elif event.key in (pygame.K_SPACE, pygame.K_RETURN): transitioning_to = STATE_MENU
                elif state == STATE_GAME_OVER:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN): transitioning_to = STATE_PLAYING
                    elif event.key == pygame.K_ESCAPE: transitioning_to = STATE_MENU; menu_page = "main"
                elif state == STATE_PLAYING:
                    if event.key == pygame.K_ESCAPE: transitioning_to = STATE_MENU; menu_page = "main"
                    for p in players:
                        if not p.alive: continue
                        req_dir = None
                        is_p1_up = (event.key == p.keys['up']) or (num_players == 1 and p.pid == 1 and event.key == pygame.K_UP)
                        is_p1_dn = (event.key == p.keys['down']) or (num_players == 1 and p.pid == 1 and event.key == pygame.K_DOWN)
                        is_p1_lt = (event.key == p.keys['left']) or (num_players == 1 and p.pid == 1 and event.key == pygame.K_LEFT)
                        is_p1_rt = (event.key == p.keys['right']) or (num_players == 1 and p.pid == 1 and event.key == pygame.K_RIGHT)
                        if p.pid == 1:
                            if is_p1_up: req_dir = (0, -1)
                            elif is_p1_dn: req_dir = (0, 1)
                            elif is_p1_lt: req_dir = (-1, 0)
                            elif is_p1_rt: req_dir = (1, 0)
                        elif p.pid == 2:
                            if event.key == p.keys['up']: req_dir = (0, -1)
                            elif event.key == p.keys['down']: req_dir = (0, 1)
                            elif event.key == p.keys['left']: req_dir = (-1, 0)
                            elif event.key == p.keys['right']: req_dir = (1, 0)
                        if req_dir:
                            last_dir = p.queue[-1] if p.queue else p.dir
                            if req_dir != (-last_dir[0], -last_dir[1]) and req_dir != last_dir:
                                if len(p.queue) < 3: p.queue.append(req_dir)
        if state == STATE_PLAYING and not win_game and transitioning_to is None:
            if global_ice_timer > 0:
                global_ice_timer -= dt
                move_progress += speed * 0.5 * dt
            else:
                move_progress += speed * dt
            for p in players:
                if p.magnet_timer > 0:
                    p.magnet_timer -= dt
                    if p.alive and time_ms % 200 < 50:
                        hx, hy = p.body[0]
                        for f in foods[:]:
                            dx, dy = hx - f['x'], hy - f['y']
                            if 0 < abs(dx) + abs(dy) <= 4:
                                f['x'] += 1 if dx > 0 else (-1 if dx < 0 else 0)
                                f['y'] += 1 if dy > 0 else (-1 if dy < 0 else 0)
                                if f['x'] == hx and f['y'] == hy:
                                    handle_eat(p, f, hx, hy)
                if p.ghost_timer > 0: p.ghost_timer -= dt
            while move_progress >= 1.0:
                move_progress -= 1.0
                grid = current_mode["grid"]
                for p in players:
                    if not p.alive: continue
                    p.old_body = p.body.copy()
                    if p.queue: p.dir = p.queue.pop(0)
                    p.next_head = (p.body[0][0] + p.dir[0], p.body[0][1] + p.dir[1])
                for p in players:
                    if not p.alive: continue
                    is_ghost = p.ghost_timer > 0
                    is_oob = p.next_head[0] < 0 or p.next_head[0] >= grid or p.next_head[1] < 0 or p.next_head[1] >= grid
                    if is_oob:
                        if current_mode.get("wrap") or is_ghost:
                            p.next_head = (p.next_head[0] % grid, p.next_head[1] % grid)
                        else: p.alive = False; play_sound("explosion"); shake, flash_alpha = 15.0, 255.0
                    if not is_ghost and p.next_head in walls:
                        p.alive = False; play_sound("explosion"); shake, flash_alpha = 15.0, 255.0
                for p in players:
                    if not p.alive: continue
                    eaten_f = None
                    for f in foods:
                        if f['x'] == p.next_head[0] and f['y'] == p.next_head[1]:
                            eaten_f = f; break
                    if eaten_f:
                        handle_eat(p, eaten_f, p.next_head[0], p.next_head[1])
                for p in players:
                    if not p.alive or p.ghost_timer > 0: continue
                    for other in players:
                        if not other.alive and len(other.body) == 0: continue
                        if p.next_head in other.body:
                            if other == p and p.next_head == p.body[-1] and p.pending_growth == 0: pass
                            else: p.alive = False; play_sound("explosion"); shake, flash_alpha = 15.0, 255.0
                for p in players:
                    if not p.alive and len(p.body) > 0:
                        for px, py in p.body:
                            if random.random() < 0.4: foods.append({'x': px, 'y': py, 'type': 'red'})
                        p.body.clear(); p.old_body.clear()
                for p in players:
                    if not p.alive: continue
                    p.body.insert(0, p.next_head)
                    if p.pending_growth > 0: p.pending_growth -= 1
                    else: p.body.pop()
                for p in players:
                    if p.score > highscores.get(current_mode["id"], 0): highscores[current_mode["id"]] = p.score
                if all(not p.alive for p in players):
                    if win_game:
                        play_sound("win")
                    else:
                        play_sound("game_over")
                    # Stop background music
                    try:
                        if bg_music: bg_music.stop()
                        current_music = None
                    except Exception:
                        pass
                    state = STATE_GAME_OVER
        for p in particles[:]:
            p['x'] += p['vx'] * dt; p['y'] += p['vy'] * dt; p['life'] -= dt
            if p['life'] <= 0: particles.remove(p)
        for ft in floating_texts[:]:
            ft['y'] -= ft['cell'] * 1.5 * dt; ft['life'] -= dt
            if ft['life'] <= 0: floating_texts.remove(ft)
        v_surf.fill(theme_cfg["bg"])
        shadow_surf.fill((0, 0, 0, 0))
        if state == STATE_MENU:
            bg_off = (time_ms / 30.0) % 40
            for y in range(-40, VIRTUAL_H + 40, 40):
                for x in range(-40, VIRTUAL_W + 40, 40):
                    if ((x + y) // 40) % 2 == 0: pygame.draw.rect(v_surf, theme_cfg["top"], (x + bg_off, y + bg_off, 40, 40))
            if menu_page == "main":
                draw_text(v_surf, "S N A K E", 60, VIRTUAL_W // 2, 70, "center", BG_LIGHT)
                draw_text(v_surf, "Select Gamemode", 16, VIRTUAL_W // 2, 120, "center", theme_cfg["text"], alpha=150)
                start_y = 160; spacing = 32
                for i, mode in enumerate(MAIN_MODES):
                    my = start_y + i * spacing
                    color = MENU_HIGHLIGHT if i == selected_main_idx else theme_cfg["text"]
                    alpha = 255 if i == selected_main_idx else 120
                    prefix = "> " if i == selected_main_idx else "  "
                    scale = 1.1 + (math.sin(time_ms/150.0)*0.05) if i == selected_main_idx else 1.0
                    draw_text(v_surf, f"{prefix}{mode['name']}", 18, VIRTUAL_W // 2, my, "center", color, scale=scale, alpha=alpha)
            elif menu_page == "size":
                draw_text(v_surf, MAIN_MODES[selected_main_idx]["name"].upper(), 45, VIRTUAL_W // 2, 60, "center", BG_LIGHT)
                draw_text(v_surf, "Select Board Size", 16, VIRTUAL_W // 2, 105, "center", theme_cfg["text"], alpha=150)
                start_y = 140; spacing = 28
                for i, mode in enumerate(SIZE_MODES):
                    my = start_y + i * spacing
                    color = MENU_HIGHLIGHT if i == selected_size_idx else theme_cfg["text"]
                    alpha = 255 if i == selected_size_idx else 120
                    prefix = "> " if i == selected_size_idx else "  "
                    scale = 1.1 + (math.sin(time_ms/150.0)*0.05) if i == selected_size_idx else 1.0
                    draw_text(v_surf, f"{prefix}{mode['name']}", 16, VIRTUAL_W // 2, my, "center", color, scale=scale, alpha=alpha)
            elif menu_page == "speed":
                draw_text(v_surf, "SPEED SETTINGS", 45, VIRTUAL_W // 2, 60, "center", BG_LIGHT)
                draw_text(v_surf, "Select Speed Multiplier", 16, VIRTUAL_W // 2, 105, "center", theme_cfg["text"], alpha=150)
                start_y = 140; spacing = 32
                for i, mode in enumerate(SPEED_MODES):
                    my = start_y + i * spacing
                    color = MENU_HIGHLIGHT if i == selected_speed_idx else theme_cfg["text"]
                    alpha = 255 if i == selected_speed_idx else 120
                    prefix = "> " if i == selected_speed_idx else "  "
                    scale = 1.1 + (math.sin(time_ms/150.0)*0.05) if i == selected_speed_idx else 1.0
                    draw_text(v_surf, f"{prefix}{mode['name']}", 16, VIRTUAL_W // 2, my, "center", color, scale=scale, alpha=alpha)
            elif menu_page == "custom":
                draw_text(v_surf, "CUSTOM GAME", 45, VIRTUAL_W // 2, 40, "center", BG_LIGHT)
                c_sets = [
                    f"Grid Size: < {custom_cfg['grid']}x{custom_cfg['grid']} >",
                    f"Base Speed: < {custom_cfg['speed']} >",
                    f"Apple Count: < {custom_cfg['apples']} >",
                    f"Gold Chance: < {custom_cfg['gold_pct']}% >",
                    f"Magic Chance: < {custom_cfg['magic_pct']}% >",
                    f"Portal / Wrap: < {'ON' if custom_cfg['wrap'] else 'OFF'} >",
                    f"Labyrinth Walls: < {'ON' if custom_cfg['maze'] else 'OFF'} >",
                    "[ START CUSTOM GAME ]",
                    "< Back"
                ]
                for i, s in enumerate(c_sets):
                    y = 100 + i * 32 + (15 if i >= 7 else 0)
                    color = MENU_HIGHLIGHT if i == custom_idx else theme_cfg["text"]
                    draw_text(v_surf, s, 16, VIRTUAL_W // 2, y, "center", color, alpha=255 if i == custom_idx else 150)
            if menu_page == "main":
                draw_text(v_surf, f"[P] P1/P2: {num_players}  |  [S] Settings  |  [C] Shop  |  [I] Index", 12, VIRTUAL_W // 2, VIRTUAL_H - 15, "center", theme_cfg["text"], alpha=180)
            else:
                pulse_alpha = int(155 + math.sin(time_ms/200.0) * 100)
                draw_text(v_surf, "[ SPACE ] / [ ENTER ]", 14, VIRTUAL_W // 2, VIRTUAL_H - 25, "center", MENU_HIGHLIGHT, alpha=pulse_alpha)
        elif state == STATE_INDEX:
            draw_text(v_surf, "APPLE INDEX", 45, VIRTUAL_W // 2, 40, "center", MENU_HIGHLIGHT)
            items = [
                ('red', "RED APPLE", "+1 Score, +1 Length. The classic food."),
                ('gold', "GOLDEN APPLE", "+5 Score, +5 Length. Extremely valuable."),
                ('ghost', "GHOST APPLE", "Grants Ghost Mode (8s). Pass through walls & yourself."),
                ('ice', "ICE APPLE", "Freezes Time (5s). Slows game speed by 50%."),
                ('magnet', "MAGNET APPLE", "Magnetic Aura (8s). Pulls nearby apples into your mouth.")
            ]
            start_y = 100
            for i, (atype, title, desc) in enumerate(items):
                y = start_y + i * 55
                tex = apple_textures.get(atype)
                if not tex:
                    tex = get_apple_texture(32, atype)
                    apple_textures[atype] = tex
                v_surf.blit(tex, (VIRTUAL_W//2 - 240, y - 6))
                color = get_apple_color(atype)
                draw_text(v_surf, title, 18, VIRTUAL_W//2 - 190, y, "topleft", color)
                draw_text(v_surf, desc, 14, VIRTUAL_W//2 - 190, y + 22, "topleft", theme_cfg["text"], alpha=200)
            pulse_alpha = int(155 + math.sin(time_ms/150.0) * 100)
            draw_text(v_surf, "< Back (ESC)", 16, VIRTUAL_W // 2, VIRTUAL_H - 30, "center", theme_cfg["text"], alpha=pulse_alpha)
        elif state == STATE_SETTINGS:
            draw_text(v_surf, "SETTINGS & LAYOUT", 45, VIRTUAL_W // 2, 40, "center", BG_LIGHT)
            layout_name = HUD_LAYOUTS[hud_layout_idx]
            sets = [
                f"P1 UP: {safe_key_name(P1_KEYS['up'])}",   f"P2 UP: {safe_key_name(P2_KEYS['up'])}",
                f"P1 DOWN: {safe_key_name(P1_KEYS['down'])}", f"P2 DOWN: {safe_key_name(P2_KEYS['down'])}",
                f"P1 LEFT: {safe_key_name(P1_KEYS['left'])}", f"P2 LEFT: {safe_key_name(P2_KEYS['left'])}",
                f"P1 RIGHT: {safe_key_name(P1_KEYS['right'])}", f"P2 RIGHT: {safe_key_name(P2_KEYS['right'])}",
                f"Theme: < {theme_cfg['name']} >",          f"Layout: < {layout_name} >",
                "Reset to Defaults",                        "< Back"
            ]
            for i, s in enumerate(sets):
                col = i % 2
                row = i // 2
                x = VIRTUAL_W // 2 - 160 if col == 0 else VIRTUAL_W // 2 + 160
                y = 110 + row * 45
                color = MENU_HIGHLIGHT if i == settings_idx else theme_cfg["text"]
                txt = s if not (waiting_for_key and i == settings_idx) else "Press Key..."
                draw_text(v_surf, txt, 16, x, y, "center", color, alpha=255 if i == settings_idx else 150)
        elif state == STATE_SHOP:
            draw_text(v_surf, "SHOP & SKINS", 45, VIRTUAL_W // 2, 40, "center", MENU_HIGHLIGHT)
            draw_text(v_surf, f"Coins: {global_coins}", 16, VIRTUAL_W // 2, 80, "center", theme_cfg["text"])
            shop_items = ["neon", "rainbow", "mech", "p1_cycle", "p2_cycle", "back"]
            labels = [
                f"Neon Skin (100) {'[UNLOCKED]' if 'neon' in unlocked_skins else ''}",
                f"Rainbow Skin (250) {'[UNLOCKED]' if 'rainbow' in unlocked_skins else ''}",
                f"Mech Skin (500) {'[UNLOCKED]' if 'mech' in unlocked_skins else ''}",
                f"Player 1: < {p1_skin.upper()} >", f"Player 2: < {p2_skin.upper()} >", "< Back"
            ]
            for i, lbl in enumerate(labels):
                y = 140 + i * 35
                color = MENU_HIGHLIGHT if i == shop_idx else theme_cfg["text"]
                draw_text(v_surf, lbl, 16, VIRTUAL_W // 2, y, "center", color, alpha=255 if i == shop_idx else 150)
        elif state in (STATE_PLAYING, STATE_GAME_OVER):
            grid = current_mode["grid"]
            layout_name = HUD_LAYOUTS[hud_layout_idx]
            p_score = players[0].score if len(players)>0 else 0
            highscore = highscores.get(current_mode["id"], 0)
            if layout_name == "Top Bar":
                pygame.draw.rect(v_surf, theme_cfg["top"], (0, 0, VIRTUAL_W, 55))
                pygame.draw.line(v_surf, theme_cfg["border"], (0, 55), (VIRTUAL_W, 55), 2)
                draw_text(v_surf, "SNAKE", 24, 20, 8, "topleft", BG_LIGHT)
                draw_text(v_surf, current_mode["name"], 14, 22, 34, "topleft", theme_cfg["text"], alpha=150)
                if num_players == 1:
                    draw_text(v_surf, "SCORE", 12, VIRTUAL_W // 2, 12, "center", theme_cfg["text"], alpha=150)
                    draw_text(v_surf, str(p_score), 28, VIRTUAL_W // 2, 34, "center", (255, 255, 255), scale=1.0+(score_bump*0.4))
                else:
                    draw_text(v_surf, f"P1: {players[0].score}", 24, VIRTUAL_W // 2 - 80, 27, "center", get_snake_color(p1_skin, 0, 1, 0))
                    draw_text(v_surf, f"P2: {players[1].score}", 24, VIRTUAL_W // 2 + 80, 27, "center", get_snake_color(p2_skin, 0, 1, 0))
                draw_text(v_surf, "HIGH", 12, VIRTUAL_W - 20, 12, "topright", theme_cfg["text"], alpha=150)
                draw_text(v_surf, str(highscore), 24, VIRTUAL_W - 20, 32, "topright", MENU_HIGHLIGHT)
                draw_text(v_surf, "ESC: Menu", 10, 15, VIRTUAL_H - 15, "topleft", theme_cfg["text"], alpha=100)
            elif layout_name == "Bottom Bar":
                pygame.draw.rect(v_surf, theme_cfg["top"], (0, VIRTUAL_H - 55, VIRTUAL_W, 55))
                pygame.draw.line(v_surf, theme_cfg["border"], (0, VIRTUAL_H - 55), (VIRTUAL_W, VIRTUAL_H - 55), 2)
                draw_text(v_surf, "SNAKE", 24, 20, VIRTUAL_H - 45, "topleft", BG_LIGHT)
                if num_players == 1:
                    draw_text(v_surf, f"SCORE: {p_score}", 24, VIRTUAL_W // 2, VIRTUAL_H - 28, "center", (255, 255, 255), scale=1.0+(score_bump*0.4))
                else:
                    draw_text(v_surf, f"P1: {players[0].score}", 24, VIRTUAL_W // 2 - 80, VIRTUAL_H - 28, "center", get_snake_color(p1_skin, 0, 1, 0))
                    draw_text(v_surf, f"P2: {players[1].score}", 24, VIRTUAL_W // 2 + 80, VIRTUAL_H - 28, "center", get_snake_color(p2_skin, 0, 1, 0))
                draw_text(v_surf, f"HIGH: {highscore}", 24, VIRTUAL_W - 20, VIRTUAL_H - 28, "topright", MENU_HIGHLIGHT)
                draw_text(v_surf, "ESC: Menu", 10, 15, 10, "topleft", theme_cfg["text"], alpha=100)
            elif layout_name == "Left Panel":
                pygame.draw.rect(v_surf, theme_cfg["top"], (0, 0, 160, VIRTUAL_H))
                pygame.draw.line(v_surf, theme_cfg["border"], (160, 0), (160, VIRTUAL_H), 2)
                draw_text(v_surf, "SNAKE", 24, 80, 20, "center", BG_LIGHT)
                draw_text(v_surf, current_mode["name"], 12, 80, 45, "center", theme_cfg["text"], alpha=150)
                if num_players == 1:
                    draw_text(v_surf, "SCORE", 12, 80, 100, "center", theme_cfg["text"], alpha=150)
                    draw_text(v_surf, str(p_score), 28, 80, 125, "center", (255, 255, 255), scale=1.0+(score_bump*0.4))
                else:
                    draw_text(v_surf, "P1", 12, 80, 100, "center", theme_cfg["text"], alpha=150)
                    draw_text(v_surf, str(players[0].score), 24, 80, 120, "center", get_snake_color(p1_skin, 0, 1, 0))
                    draw_text(v_surf, "P2", 12, 80, 160, "center", theme_cfg["text"], alpha=150)
                    draw_text(v_surf, str(players[1].score), 24, 80, 180, "center", get_snake_color(p2_skin, 0, 1, 0))
                draw_text(v_surf, "HIGH", 12, 80, VIRTUAL_H - 60, "center", theme_cfg["text"], alpha=150)
                draw_text(v_surf, str(highscore), 24, 80, VIRTUAL_H - 35, "center", MENU_HIGHLIGHT)
            elif layout_name == "Right Panel":
                pygame.draw.rect(v_surf, theme_cfg["top"], (VIRTUAL_W - 160, 0, 160, VIRTUAL_H))
                pygame.draw.line(v_surf, theme_cfg["border"], (VIRTUAL_W - 160, 0), (VIRTUAL_W - 160, VIRTUAL_H), 2)
                draw_text(v_surf, "SNAKE", 24, VIRTUAL_W - 80, 20, "center", BG_LIGHT)
                draw_text(v_surf, current_mode["name"], 12, VIRTUAL_W - 80, 45, "center", theme_cfg["text"], alpha=150)
                if num_players == 1:
                    draw_text(v_surf, "SCORE", 12, VIRTUAL_W - 80, 100, "center", theme_cfg["text"], alpha=150)
                    draw_text(v_surf, str(p_score), 28, VIRTUAL_W - 80, 125, "center", (255, 255, 255), scale=1.0+(score_bump*0.4))
                else:
                    draw_text(v_surf, "P1", 12, VIRTUAL_W - 80, 100, "center", theme_cfg["text"], alpha=150)
                    draw_text(v_surf, str(players[0].score), 24, VIRTUAL_W - 80, 120, "center", get_snake_color(p1_skin, 0, 1, 0))
                    draw_text(v_surf, "P2", 12, VIRTUAL_W - 80, 160, "center", theme_cfg["text"], alpha=150)
                    draw_text(v_surf, str(players[1].score), 24, VIRTUAL_W - 80, 180, "center", get_snake_color(p2_skin, 0, 1, 0))
                draw_text(v_surf, "HIGH", 12, VIRTUAL_W - 80, VIRTUAL_H - 60, "center", theme_cfg["text"], alpha=150)
                draw_text(v_surf, str(highscore), 24, VIRTUAL_W - 80, VIRTUAL_H - 35, "center", MENU_HIGHLIGHT)
            if global_ice_timer > 0:
                pygame.draw.rect(v_surf, (50, 255, 255, 50), (0, 0, VIRTUAL_W, VIRTUAL_H))
            pygame.draw.rect(v_surf, theme_cfg["border"], (bx - 6, by - 6, grid * cell + 12, grid * cell + 12), border_radius=8)
            for y in range(grid):
                for x in range(grid):
                    pygame.draw.rect(v_surf, BG_LIGHT if (x + y) % 2 == 0 else BG_DARK, (bx + x * cell, by + y * cell, cell, cell))
            shadow_off = 2
            for f in foods: pygame.draw.circle(shadow_surf, SNAKE_SHADOW, (bx + f['x']*cell + cell//2 + shadow_off, by + f['y']*cell + cell//2 + shadow_off), cell//2)
            for wx, wy in walls: pygame.draw.rect(shadow_surf, SNAKE_SHADOW, (bx + wx*cell + shadow_off, by + wy*cell + shadow_off, cell, cell))
            for p in players:
                is_ghost = p.ghost_timer > 0
                if is_ghost: continue
                static_start = 1 if (p.alive and len(p.old_body) > 0) else 0
                for i in range(static_start, len(p.body)):
                    seg = p.body[i]
                    pygame.draw.rect(shadow_surf, SNAKE_SHADOW, (bx + seg[0]*cell + shadow_off, by + seg[1]*cell + shadow_off, cell, cell))
                if p.alive and len(p.old_body) > 0:
                    hx, hy = p.body[0]
                    hdx, hdy = hx - p.old_body[0][0], hy - p.old_body[0][1]
                    if abs(hdx) <= 1 and abs(hdy) <= 1: 
                        hr = get_growing_rect(hx, hy, hdx, hdy, move_progress, cell, bx, by)
                        pygame.draw.rect(shadow_surf, SNAKE_SHADOW, (hr[0]+shadow_off, hr[1]+shadow_off, hr[2], hr[3]))
                    for i in range(len(p.old_body) - 1):
                        px, py = p.old_body[i]
                        pygame.draw.rect(shadow_surf, SNAKE_SHADOW, (bx+px*cell+shadow_off, by+py*cell+shadow_off, cell, cell))
                    if len(p.old_body) == len(p.body) and len(p.old_body) > 1:
                        tx, ty = p.old_body[-1]
                        tdx, tdy = p.old_body[-2][0] - tx, p.old_body[-2][1] - ty
                        if abs(tdx) <= 1 and abs(tdy) <= 1:
                            tr = get_shrinking_rect(tx, ty, tdx, tdy, move_progress, cell, bx, by)
                            pygame.draw.rect(shadow_surf, SNAKE_SHADOW, (tr[0]+shadow_off, tr[1]+shadow_off, tr[2], tr[3]))
                    elif len(p.old_body) < len(p.body):
                        tx, ty = p.old_body[-1]
                        pygame.draw.rect(shadow_surf, SNAKE_SHADOW, (bx+tx*cell+shadow_off, by+ty*cell+shadow_off, cell, cell))
                else:
                    for px, py in p.body: pygame.draw.rect(shadow_surf, SNAKE_SHADOW, (bx+px*cell+shadow_off, by+py*cell+shadow_off, cell, cell))
            v_surf.blit(shadow_surf, (0, 0))
            for wx, wy in walls: v_surf.blit(wall_tex, (bx + wx*cell, by + wy*cell))
            for f in foods: v_surf.blit(apple_textures[f['type']], (bx + f['x']*cell, by + f['y']*cell))
            for p in players:
                is_ghost = p.ghost_timer > 0
                if p.alive and len(p.old_body) > 0:
                    hx, hy = p.body[0]
                    hdx, hdy = hx - p.old_body[0][0], hy - p.old_body[0][1]
                    if abs(hdx) <= 1 and abs(hdy) <= 1:
                        hr = get_growing_rect(hx, hy, hdx, hdy, move_progress, cell, bx, by)
                        pygame.draw.rect(v_surf, get_snake_color(p.skin, 0, len(p.body), time_ms), hr)
                    else:
                        pygame.draw.rect(v_surf, get_snake_color(p.skin, 0, len(p.body), time_ms), (bx+hx*cell, by+hy*cell, cell, cell))
                    for i in range(len(p.old_body) - 1):
                        px, py = p.old_body[i]
                        pygame.draw.rect(v_surf, get_snake_color(p.skin, i + 1, len(p.body), time_ms), (bx+px*cell, by+py*cell, cell, cell))
                    if len(p.old_body) == len(p.body) and len(p.old_body) > 1:
                        tx, ty = p.old_body[-1]
                        tdx, tdy = p.old_body[-2][0] - tx, p.old_body[-2][1] - ty
                        if abs(tdx) <= 1 and abs(tdy) <= 1:
                            tr = get_shrinking_rect(tx, ty, tdx, tdy, move_progress, cell, bx, by)
                            pygame.draw.rect(v_surf, get_snake_color(p.skin, len(p.old_body)-1, len(p.body), time_ms), tr)
                    elif len(p.old_body) < len(p.body):
                        tx, ty = p.old_body[-1]
                        pygame.draw.rect(v_surf, get_snake_color(p.skin, len(p.old_body)-1, len(p.body), time_ms), (bx+tx*cell, by+ty*cell, cell, cell))
                else:
                    for i, (px, py) in enumerate(p.body):
                        pygame.draw.rect(v_surf, get_snake_color(p.skin, i, len(p.body), time_ms), (bx+px*cell, by+py*cell, cell, cell))
                if p.alive and len(p.old_body) > 0 and move_progress > 0:
                    hdx, hdy = p.body[0][0] - p.old_body[0][0], p.body[0][1] - p.old_body[0][1]
                    if abs(hdx) <= 1 and abs(hdy) <= 1:
                        head_vx, head_vy = p.old_body[0][0] + hdx * move_progress, p.old_body[0][1] + hdy * move_progress
                    else:
                        head_vx, head_vy = p.body[0][0], p.body[0][1]
                elif p.body:
                    head_vx, head_vy = p.body[0][0], p.body[0][1]
                else:
                    continue
                if is_ghost:
                    px, py = bx + int(head_vx * cell), by + int(head_vy * cell)
                    pygame.draw.rect(v_surf, (180, 50, 255), (px-2, py-2, cell+4, cell+4), 2)
                draw_head_eyes(v_surf, head_vx, head_vy, p.dir, cell, bx, by, time_ms, skin=p.skin)
            for p in particles:
                alpha = int(max(0, min(255, (p['life'] / p['max']) * 255)))
                psurf = pygame.Surface((4, 4), pygame.SRCALPHA)
                r, g, b = p['color'][0], p['color'][1], p['color'][2]
                pygame.draw.rect(psurf, (r, g, b, alpha), (0, 0, 4, 4))
                v_surf.blit(psurf, (int(p['x']), int(p['y'])))
            for ft in floating_texts:
                alpha = int(max(0, min(1, ft['life'])) * 255)
                draw_text(v_surf, ft['text'], 16, int(ft['x']), int(ft['y']), "center", ft['color'], alpha=alpha)
            if state == STATE_GAME_OVER:
                overlay = pygame.Surface((grid * cell + 12, grid * cell + 12), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 190))
                v_surf.blit(overlay, (bx - 6, by - 6))
                title = "YOU WIN!" if win_game else "GAME OVER"
                color = MENU_HIGHLIGHT if win_game else (255, 80, 80)
                cy = by + (grid * cell) // 2
                draw_text(v_surf, title, 40, bx + (grid * cell)//2, cy - 20, "center", color)
                pulse_alpha = int(155 + math.sin(time_ms/150.0) * 100)
                draw_text(v_surf, "[ SPACE ] to Restart", 14, bx + (grid * cell)//2, cy + 25, "center", MENU_HIGHLIGHT, alpha=pulse_alpha)
                draw_text(v_surf, "ESC for Menu", 12, bx + (grid * cell)//2, cy + 50, "center", (150, 150, 150))
        if flash_alpha > 0:
            fs = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
            fs.fill((255, 255, 255, int(max(0, min(255, flash_alpha)))))
            v_surf.blit(fs, (0, 0))
        if transition_alpha > 0:
            fade_surf = pygame.Surface((VIRTUAL_W, VIRTUAL_H), pygame.SRCALPHA)
            r, g, b = theme_cfg["bg"]
            fade_surf.fill((r, g, b, int(max(0, min(255, transition_alpha)))))
            v_surf.blit(fade_surf, (0, 0))
        win_w, win_h = screen.get_size()
        ratio = min(win_w / VIRTUAL_W, win_h / VIRTUAL_H)
        new_w, new_h = max(1, int(VIRTUAL_W * ratio)), max(1, int(VIRTUAL_H * ratio))
        scaled_surf = pygame.transform.scale(v_surf, (new_w, new_h))
        screen.fill((15, 15, 15))
        shake_x = random.uniform(-shake, shake) if shake > 0 else 0
        shake_y = random.uniform(-shake, shake) if shake > 0 else 0
        screen.blit(scaled_surf, ((win_w - new_w) // 2 + shake_x, (win_h - new_h) // 2 + shake_y))
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
