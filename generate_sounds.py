#!/usr/bin/env python3
"""
Snake 2.0 – High Quality Sound & Music Generator
Creates rich, fitting sound effects and background music.
Uses only Python standard library – no extra dependencies!
"""

import wave
import math
import struct
import os
import random

SAMPLE_RATE = 44100  # CD quality
AMPLITUDE = 0.4
MAX_16BIT = 32767

def write_wav(filename, samples):
    """Write a list of float samples (-1 to 1) to a WAV file."""
    n_samples = len(samples)
    with wave.open(filename, 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        for value in samples:
            value = max(-1.0, min(1.0, value))
            sample = int(MAX_16BIT * AMPLITUDE * value)
            wav.writeframes(struct.pack('<h', sample))

def envelope_adsr(t, attack, decay, sustain, release, dur, sustain_level=0.7):
    """ADSR envelope generator."""
    if t < attack:
        return t / attack
    elif t < attack + decay:
        return 1.0 - (1.0 - sustain_level) * ((t - attack) / decay)
    elif t < dur - release:
        return sustain_level
    else:
        rt = t - (dur - release)
        return sustain_level * (1.0 - rt / release)

def sine(freq, t):
    return math.sin(2 * math.pi * freq * t)

def square(freq, t, pulse=0.5):
    return 1.0 if (t * freq) % 1.0 < pulse else -1.0

def saw(freq, t):
    return 2.0 * ((t * freq) % 1.0) - 1.0

def noise():
    return random.uniform(-1.0, 1.0)

def clamp(v):
    return max(-1.0, min(1.0, v))

# ============================================================
# SOUND EFFECTS
# ============================================================

def generate_eat():
    """Crisp, satisfying 'bite' sound for eating a normal apple."""
    dur = 0.12
    n = int(SAMPLE_RATE * dur)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = envelope_adsr(t, 0.001, 0.02, 0.05, 0.05, dur)
        # Bright crunchy tone with harmonics
        v = (
            0.6 * sine(1200 + t * 3000, t) +
            0.3 * sine(2400 + t * 2000, t) +
            0.15 * sine(3600, t) +
            0.1 * noise()
        )
        samples.append(v * env)
    return samples

def generate_gold_eat():
    """Shiny, rewarding 'ding' for golden apple."""
    dur = 0.35
    n = int(SAMPLE_RATE * dur)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = envelope_adsr(t, 0.005, 0.1, 0.2, 0.1, dur, 0.8)
        # Ascending chime with sparkle
        freq = 600 + t * 2000
        v = (
            0.5 * sine(freq, t) +
            0.3 * sine(freq * 2, t) +
            0.15 * sine(freq * 3, t) +
            0.05 * noise()
        )
        samples.append(v * env)
    return samples

def generate_powerup():
    """Magical ascending tone for power-up activation."""
    dur = 0.5
    n = int(SAMPLE_RATE * dur)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = envelope_adsr(t, 0.01, 0.1, 0.3, 0.15, dur, 0.9)
        # Arpeggio feel: C E G C
        notes = [523, 659, 784, 1047]
        note_idx = min(3, int(t / dur * 4))
        freq = notes[note_idx]
        v = (
            0.4 * sine(freq, t) +
            0.3 * sine(freq * 2, t) +
            0.15 * sine(freq * 3, t) +
            0.05 * sine(freq * 0.5, t)
        )
        # Vibrato
        v *= (1.0 + 0.05 * math.sin(2 * math.pi * 20 * t))
        samples.append(v * env)
    return samples

def generate_explosion():
    """Heavy crash/explosion sound for death."""
    dur = 0.4
    n = int(SAMPLE_RATE * dur)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = envelope_adsr(t, 0.001, 0.05, 0.1, 0.3, dur, 0.4)
        # Noise burst with low-end rumble
        v = (
            0.6 * noise() +
            0.3 * sine(80 - t * 150, t) +
            0.15 * sine(160 - t * 200, t)
        )
        samples.append(v * env)
    return samples

def generate_game_over():
    """Sad descending melody for game over."""
    dur = 1.2
    n = int(SAMPLE_RATE * dur)
    samples = []
    # Slow descending scale: C B A G F E D C
    notes = [523, 494, 440, 392, 349, 330, 294, 262]
    note_len = dur / len(notes)
    for i in range(n):
        t = i / SAMPLE_RATE
        env = envelope_adsr(t, 0.02, 0.1, 0.6, 0.4, dur, 0.7)
        note_idx = min(len(notes) - 1, int(t / note_len))
        freq = notes[note_idx]
        v = (
            0.5 * sine(freq, t) +
            0.25 * sine(freq * 2, t) +
            0.1 * sine(freq * 0.5, t)
        )
        samples.append(v * env)
    return samples

def generate_win():
    """Triumphant ascending fanfare for winning."""
    dur = 1.5
    n = int(SAMPLE_RATE * dur)
    samples = []
    # Ascending arpeggio: C E G C E G C
    notes = [523, 659, 784, 1047, 1319, 1568, 2093]
    note_len = dur / len(notes)
    for i in range(n):
        t = i / SAMPLE_RATE
        env = envelope_adsr(t, 0.02, 0.05, 0.5, 0.5, dur, 0.8)
        note_idx = min(len(notes) - 1, int(t / note_len))
        freq = notes[note_idx]
        v = (
            0.4 * sine(freq, t) +
            0.3 * sine(freq * 2, t) +
            0.2 * sine(freq * 3, t) +
            0.1 * sine(freq * 4, t)
        )
        samples.append(v * env)
    return samples

def generate_menu_move():
    """Short, subtle click for menu navigation."""
    dur = 0.04
    n = int(SAMPLE_RATE * dur)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = envelope_adsr(t, 0.001, 0.005, 0.01, 0.03, dur, 0.3)
        v = 0.5 * sine(800, t) + 0.2 * noise()
        samples.append(v * env)
    return samples

def generate_menu_select():
    """Satisfying confirmation 'blip' for selection."""
    dur = 0.15
    n = int(SAMPLE_RATE * dur)
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = envelope_adsr(t, 0.002, 0.02, 0.05, 0.08, dur)
        v = (
            0.5 * sine(660, t) +
            0.3 * sine(880, t) +
            0.15 * sine(1320, t)
        )
        samples.append(v * env)
    return samples

# ============================================================
# BACKGROUND MUSIC
# ============================================================

def generate_bg_music():
    """Lo-fi chill background music for Snake gameplay.
    ≈30 seconds, designed to loop seamlessly.
    """
    bpm = 100
    beat_dur = 60.0 / bpm
    total_beats = 48  # 12 bars of 4/4
    total_dur = total_beats * beat_dur
    n = int(SAMPLE_RATE * total_dur)
    
    samples = [0.0] * n
    
    # === Bass line: simple arpeggiated pattern in Am ===
    bass_notes = [
        [220, 220, 262, 220],  # A2, A2, C3, A2
        [196, 196, 220, 196],  # G2, G2, A2, G2
        [165, 165, 196, 165],  # E2, E2, G2, E2
        [175, 175, 196, 220],  # F2, F2, G2, A2
    ]
    
    bass_volume = 0.25
    for beat_idx in range(total_beats):
        bar = (beat_idx // 4) % 4
        sub = beat_idx % 4
        freq = bass_notes[bar][sub]
        
        for s in range(int(SAMPLE_RATE * beat_dur)):
            t_global = (beat_idx * beat_dur) + s / SAMPLE_RATE
            t_local = s / SAMPLE_RATE
            idx = int(t_global * SAMPLE_RATE)
            if idx >= n: break
            
            env = 1.0 - (t_local / beat_dur) * 0.3
            v = 0.0
            v += 0.6 * sine(freq, t_local)
            v += 0.3 * sine(freq * 2, t_local)
            v = clamp(v) * env * bass_volume
            samples[idx] += v
    
    # === Chords: warm pad chords ===
    chord_prog = [
        [220, 262, 330, 392],  # Am
        [196, 247, 294, 370],  # G
        [165, 196, 247, 294],  # Em
        [175, 220, 262, 349],  # F
    ]
    
    chord_volume = 0.12
    chord_dur = 4 * beat_dur  # One chord per bar
    for bar in range(12):
        notes = chord_prog[bar % 4]
        for s in range(int(SAMPLE_RATE * chord_dur)):
            t_global = (bar * chord_dur) + s / SAMPLE_RATE
            t_local = s / SAMPLE_RATE
            idx = int(t_global * SAMPLE_RATE)
            if idx >= n: break
            
            # Slow attack, slow decay
            env = 1.0 - (t_local / chord_dur) * 0.5
            env *= min(1.0, t_local * 2)  # fade in
            
            v = 0.0
            for freq in notes:
                v += 0.4 * sine(freq, t_local)
                v += 0.2 * sine(freq * 0.5, t_local)
            v = clamp(v) * env * chord_volume
            samples[idx] += v
    
    # === Hi-hat / percussion: subtle rhythm ===
    hat_volume = 0.08
    for step in range(total_beats * 4):
        step_dur = beat_dur / 4
        t_start = step * step_dur
        
        # Skip some for variation
        if step % 8 in (1, 3, 5, 7) and random.random() < 0.3:
            continue
            
        for s in range(int(SAMPLE_RATE * 0.03)):
            t_global = t_start + s / SAMPLE_RATE
            idx = int(t_global * SAMPLE_RATE)
            if idx >= n: break
            
            env = 1.0 - (s / (SAMPLE_RATE * 0.03))
            v = noise() * env * hat_volume
            samples[idx] += v
    
    # === Melody: simple pentatonic hook ===
    melody = [
        (0, 523),   (1.5, 587),  (3, 659),   (4, 784),
        (5.5, 659),  (7, 587),   (8, 523),   (9.5, 440),
        (11, 523),  (12, 659),  (13.5, 784), (15, 880),
        (16.5, 784), (18, 659),  (19.5, 587), (21, 523),
        (22, 440),  (23, 523),
    ]
    
    melody_dur = total_dur
    melody_volume = 0.15
    for i in range(n):
        t = i / SAMPLE_RATE
        env = 1.0 - (t / melody_dur) * 0.3
        
        v = 0.0
        for j in range(len(melody)-1):
            t1, f1 = melody[j]
            t2, f2 = melody[j+1]
            if t1 <= t < t2:
                progress = (t - t1) / (t2 - t1)
                freq = f1 + (f2 - f1) * progress
                local_t = t - t1
                note_env = 1.0 - (local_t / (t2 - t1)) * 0.5
                note_env *= min(1.0, local_t * 10)
                v += 0.5 * sine(freq, t) * note_env
                break
        
        v += 0.2 * sine(523 * 0.5, t) * 0.3
        v = clamp(v) * env * melody_volume
        samples[i] += v
    
    # Final mix: normalize a bit
    max_val = max(abs(s) for s in samples) or 1.0
    if max_val > 0.8:
        scale = 0.8 / max_val
        samples = [s * scale for s in samples]
    
    return samples

def generate_pause_music():
    """A short ambient loop for the menu (15 seconds)."""
    dur = 15.0
    n = int(SAMPLE_RATE * dur)
    samples = [0.0] * n
    
    # Ambient pads
    pad_notes = [262, 330, 392, 523]
    volume = 0.15
    for i in range(n):
        t = i / SAMPLE_RATE
        env = 0.5 + 0.5 * math.sin(2 * math.pi * 0.1 * t)
        v = 0.0
        for freq in pad_notes:
            v += 0.3 * sine(freq, t)
        v += 0.15 * sine(130, t)
        samples[i] = clamp(v) * env * volume
    
    return samples

# ============================================================
# GENERATE ALL FILES
# ============================================================

if __name__ == "__main__":
    os.makedirs("sounds", exist_ok=True)
    random.seed(42)
    
    print("🎵 Generating high-quality sound effects...\n")
    
    print("  🍎 eat.wav ...", end=" ")
    write_wav("sounds/eat.wav", generate_eat())
    print("✅ Crisp bite sound")
    
    print("  🟡 gold_eat.wav ...", end=" ")
    write_wav("sounds/gold_eat.wav", generate_gold_eat())
    print("✅ Shiny reward chime")
    
    print("  ⚡ powerup.wav ...", end=" ")
    write_wav("sounds/powerup.wav", generate_powerup())
    print("✅ Magical ascending arpeggio")
    
    print("  💥 explosion.wav ...", end=" ")
    write_wav("sounds/explosion.wav", generate_explosion())
    print("✅ Heavy crash")
    
    print("  😵 game_over.wav ...", end=" ")
    write_wav("sounds/game_over.wav", generate_game_over())
    print("✅ Sad descending scale")
    
    print("  🏆 win.wav ...", end=" ")
    write_wav("sounds/win.wav", generate_win())
    print("✅ Triumphant fanfare")
    
    print("  🔼 menu_move.wav ...", end=" ")
    write_wav("sounds/menu_move.wav", generate_menu_move())
    print("✅ Subtle click")
    
    print("  ✅ menu_select.wav ...", end=" ")
    write_wav("sounds/menu_select.wav", generate_menu_select())
    print("✅ Satisfying blip")
    
    print("\n🎵 Generating background music...")
    
    print("  🎵 bg_music.wav ...", end=" ")
    samples = generate_bg_music()
    write_wav("sounds/bg_music.wav", samples)
    dur = len(samples) / SAMPLE_RATE
    print(f"✅ Lo-fi chill loop ({dur:.1f}s)")
    
    print("  🎵 bg_menu.wav ...", end=" ")
    write_wav("sounds/bg_menu.wav", generate_pause_music())
    print("✅ Ambient menu pad (15s)")
    
    print("\n✨ All sounds regenerated!")
    print(f"📁 Location: {os.path.abspath('sounds')}/")
