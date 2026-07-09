A classic Snake game with tons of extras – modern, extensible, and for 1–2 players!

---

## 🚀 Installation & Launch

**Requirements:** Python 3.11+ installed.

### Quick Start (Recommended)

Just double-click **`setup.py`** or run in terminal:

```bash
python setup.py
```

**This does everything automatically:**
1. ✅ Checks Python installation
2. ✅ Installs Pygame (if missing)
3. ✅ Launches the game

### Manual Installation

```bash
# 1. Clone the repository
git clone https://github.com/jonasheiss-eichiner-spec/Snake.git
cd Snake

# 2. Install Pygame
pip install -r requirements.txt

# 3. Start the game
python Snake.py
```

---

## 🎮 Controls

### Player 1 (Default)
| Action  | Key |
|---------|-----|
| Up      | **W** (or Arrow Up) |
| Down    | **S** (or Arrow Down) |
| Left    | **A** (or Arrow Left) |
| Right   | **D** (or Arrow Right) |

*(In 1-player mode, the arrow keys work in addition to WASD.)*

### Player 2 (Default)
| Action  | Key |
|---------|-----|
| Up      | **Arrow Up** |
| Down    | **Arrow Down** |
| Left    | **Arrow Left** |
| Right   | **Arrow Right** |

### General
| Key           | Function |
|---------------|----------|
| **ESC**       | Menu / Back |
| **P**         | Toggle 1-player / 2-player (on main menu) |
| **S**         | Open Settings |
| **C**         | Open Shop |
| **I**         | Apple Index (info on all apple types) |
| **F11**       | Toggle fullscreen (in-game) |
| **SPACE / ENTER** | Confirm selection |

---

## 🕹️ Game Modes

| Mode | Description |
|------|-------------|
| **Classic Mode** | Standard Snake – grow longer, collect points. |
| **Portal Mode** | Snakes wrap around to the opposite side when hitting the edge. |
| **Labyrinth** | A board with walls you have to navigate around. |
| **Swarm Mode** | Lots of apples on the field at once – pure chaos! |
| **Turbo Speed** | Extremely high base speed – for pros only. |
| **Custom Game** | Build your own game (size, speed, apples, portals/walls, and more). |

### Board Sizes
From **Tiny (6×6)** to **Giant (32×32)** – everything is selectable.

### Speeds (Classic & Turbo)
From **Slow (0.5×)** to **God Mode (2.0×)**.

---

## 🔊 Sound Effects & Music

The game comes with over **15 custom sound effects** and **background music**, all generated with pure Python (no extra libraries needed!).

| Sound | When? |
|-------|-------|
| 🍎 **Crunch** | Eating a normal apple |
| 🟡 **Shiny chime** | Eating a golden apple |
| 🐍 **Slither** | Changing direction |
| 📏 **Growth** | Snake gets longer |
| ⚡ **Power-up** | Activating ghost/ice/magnet |
| 💥 **Explosion** | Hitting a wall or yourself |
| 😵 **Sad melody** | Game over |
| 🏆 **Fanfare** | Winning the game |
| 🎵 **Lo-fi loop** | Background music during gameplay |
| 🎵 **Ambient pad** | Background music in menus |

You can regenerate all sounds anytime by running:

```bash
python generate_sounds.py
```

---

## 🍎 Apple Types

| Apple | Effect |
|-------|--------|
| 🔴 **Red Apple** | +1 point, +1 length. The standard apple. |
| 🟡 **Golden Apple** | +5 points, +5 length. Very valuable! |
| 👻 **Ghost Apple** | Ghost Mode (8s) – pass through walls and yourself. |
| ❄️ **Ice Apple** | Slow Motion (5s) – game speed is reduced by 50%. |
| 🧲 **Magnet Apple** | Magnetic Aura (8s) – pulls nearby apples toward you. |

---

## 🎨 Skins (Shop)

Collect coins in-game and buy new skins in the shop (**C** in the menu):

| Skin | Price | Effect |
|------|-------|--------|
| **Classic** | Free | Standard blue snake |
| **Neon** | 100 Coins | Glowing cyan |
| **Rainbow** | 250 Coins | Rainbow colors |
| **Mech** | 500 Coins | Metallic orange |

---

## ⚙️ Settings (S in Menu)

- **Rebind keys** – Fully customizable for both players.
- **UI Theme** – Dark Mode, Light Mode, or Hacker (green on black).
- **HUD Layout** – Position of the display: top, bottom, left, or right.
- **Reset to Defaults** – Reset all settings.

---

## 👥 2-Player Mode

Press **P** on the main menu to toggle between 1 and 2 players.  
Player 1 uses **WASD**, Player 2 uses the **Arrow Keys** (both are freely configurable in the settings).

---

## 📁 Files

| File / Folder | Description |
|------|-------------|
| `Snake.py` | The complete game (single file, no modules) |
| `setup.py` | Universal launcher – double-click or run `python setup.py` |
| `requirements.txt` | Dependencies (only `pygame`) |
| `generate_sounds.py` | Script to regenerate all sound effects & music |
| `sounds/` | Folder with all sound effects and background music |
| `README.md` | This guide |

---

## 💡 Tips

- **No subscription, no login, no internet** – runs completely locally.
- **Resolution**: The game automatically scales to any window size (resizable + fullscreen via F11).
- **Virtual resolution**: 768×432 – runs smoothly even on weaker machines.
- **Highscores** are saved per game mode (while the game is running).

---

Have fun playing! 🐍🔥
