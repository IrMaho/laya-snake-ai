# 🐍 Laya Cyber-Snake AI · Tactical Battle Arena

<p align="center">
  <b><a href="README.md">🇬🇧 English</a></b> | <b><a href="README_FA.md">🇮🇷 فارسی</a></b>
</p>

An ultra-fast, intelligent, and mathematically calibrated **Cyber-Snake Tactical Battle Arena** powered by the **Laya System 1 Decision Model** ([`convaiinnovations/laya`](https://huggingface.co/convaiinnovations/laya)) running locally on **NVIDIA GPU (CUDA)** via FastAPI.

Featuring a **Multi-Criteria Tactical Decision Engine** combined with **Forward Virtual Lookahead**, dynamic AI hostile drones, plasma projectile weapons, dimension-expansion abilities, and a rich multi-item combat ecosystem.

---

## 🎮 Gameplay Demo

![Laya AI Snake Gameplay](assets/laya_snake_gameplay.gif)

> **Live Inference**: ~35-65 ms per dual-decision pass (`tactical_action` + `move`) on NVIDIA GeForce RTX 4060 GPU with CUDA acceleration.

---

## ⚔️ Tactical Battle Arena Features

* **🛡️ 5-Heart Hull Vitality & Invincibility Shield (i-Frames)**:
  * Snake is equipped with 5 HP vitality nodes and 25 ticks of translucent forcefield invulnerability after each hit, preventing rapid multi-hit deaths.
  * Perimeter Deflector Bounce and Auto-Warp Save prevent instant deaths against boundary walls.
* **🌀 Quantum Dimension Warp (Strict 5-Warp Limit)**:
  * Dynamically expands arena bounds (+1 row/col in 4 directions) on demand or when pinned near a wall.
  * Strictly capped at **5 warps per sector** (`5/5 Left`); once exhausted, Laya receives `[EXHAUSTED/PROHIBITED]` to prevent infinite endless expansion.
* **🏆 Sector Victory Progression (Target: 2,000 Pts)**:
  * Eliminates endless infinite loops by providing a concrete sector completion target (Score 2,000).
  * Upon victory, a celebratory Sector Clear modal appears with breakdown statistics and unlocks the next sector with enhanced enemy intensity.
* **🎥 Built-in 60 FPS Canvas Screen Recorder**:
  * Dedicated `🎥 Rec (60fps)` button records crystal-clear gameplay directly from browser memory via HTML5 MediaRecorder.
  * Direct 1-click `.webm` download with zero capture flicker, zero black frames, and zero external screen recorder conflicts.
* **🛸 Hostile AI Drones (Dynamic Balanced Enemies)**:
  * Autonomous drones spawn at safe distances and patrol with calibrated tactical speed.
  * Direct laser shots vaporize drones in dazzling particle bursts (+250 pts) with ammo/heart loot drops.
* **💥 Plasma High-Voltage Laser Beam System**:
  * Fires glowing cyan laser beams in line of sight with particle trails, lens flares, and screen impact.
* **🔊 Synthesized Web Audio SFX Engine**:
  * 100% self-contained procedural synthesizer generates laser blasts, explosions, warp whooshes, bleeps, damage sirens, and victory fanfare directly in the browser with zero external audio files.
* **📦 4-Tier Collectibles Ecosystem**:
  * 🍎 **Biomass Energy (Food)**: Grows snake body, scores points, and charges warp mana capacitor.
  * ⚡ **Plasma Ammo Pods**: Reloads laser weapon (+3 rounds).
  * ❤️ **Nanite Repair Kits (Heart)**: Restores +1 HP (up to 5 HP max).
  * 🎁 **EMP Quantum Hypercube (Gift)**: Freezes all hostile drones and charges 100% warp energy.
* **🧠 Razor-Sharp Laya Decision Quality via PRIORITY Directives**:
  * High-contrast semantic criteria eliminate hesitation between shooting, evading, and harvesting.
* **🛡️ Dual-Engine Spatial Safety & Flicker-Free V-Sync**:
  * Flood fill space invariance, zero empty-buffer `clearRect` states, and continuous `requestAnimationFrame` 60 FPS rendering.

---

## 🏗️ Architecture Overview

```mermaid
graph TD
    A[Browser Client: snake.html] -->|Combat State + Questions| B[FastAPI Server: server.py]
    B -->|State Serialization + Semantic Tactical Criteria| C[Laya ModernBERT GPU Head]
    C -->|Multi-Decision Distribution| B
    B -->|Tactical Action + Direction| A
    A -->|Apply Move & Weapon| D[Dynamic Battle Canvas]

    subgraph Dual-Engine Decision System
      E[Line-of-Sight Laser Targeting]
      F[Virtual Lookahead & Escape Proof]
      G[Flood Fill Open Space Invariant]
      H[Dynamic Dimension Grid Scaler]
    end

    A <--> Dual-Engine Decision System
```

---

## 🚀 Quickstart Guide

### Prerequisites
* Windows, Linux, or macOS with **Python 3.10+**.
* An NVIDIA GPU with CUDA support (or multi-threaded CPU).
* Downloaded Laya model:
  ```bash
  git clone https://huggingface.co/convaiinnovations/laya C:\AI\Models\laya
  ```

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start the Tactical Server
```bash
# Optional custom path
set LAYA_MODEL_PATH=C:\AI\Models\laya

# Run server
python -u server.py
```
Or simply double-click **`start-game.bat`**.

### Step 3: Launch & Play
Open your browser at:
```
http://localhost:8080/snake
```
* **Spacebar**: Discharge Plasma Laser
* **E Key**: Cast Dimension Warp (+1 Col)
* **P Key**: Pause / Resume
* **Arrow Keys / WASD**: Manual control override

---

## 📡 API Specification (`/v1/systemone`)

### Multi-Question Combat Request
`POST /v1/systemone`
```json
{
  "model": "laya",
  "state": {
    "grid": { "cols": 12, "rows": 12, "min_x": 0, "max_x": 11, "min_y": 0, "max_y": 11 },
    "hp": 2,
    "max_hp": 3,
    "ammo": 3,
    "mana": 100,
    "head": [5, 6],
    "body": [[5, 6], [4, 6], [3, 6], [2, 6]],
    "enemies": [{ "id": 1, "pos": [5, 3], "dist": 3 }],
    "closest_enemy": { "pos": [5, 3], "dist": 3 },
    "enemy_in_line_of_sight": true,
    "los_direction": "up",
    "can_expand_grid": true,
    "safe_moves": ["up", "down", "right"],
    "recommended_safe_move": "up"
  },
  "questions": {
    "tactical_action": { "type": "choice" },
    "move": { "type": "choice" }
  }
}
```

### Multi-Decision Response
```json
{
  "model": "rl-agent",
  "answers": {
    "tactical_action": {
      "type": "choice",
      "choice": "shoot",
      "probabilities": {
        "shoot": 0.5841,
        "evade_and_heal": 0.142,
        "cast_grid_expansion": 0.113,
        "gather_ammo": 0.098,
        "hunt_food": 0.0629
      }
    },
    "move": {
      "type": "choice",
      "choice": "up",
      "probabilities": {
        "up": 0.8124,
        "down": 0.0642,
        "left": 0.0211,
        "right": 0.1023
      }
    }
  },
  "latency_ms": 42.5
}
```

---

## 📄 License & Credits
* Model: [`convaiinnovations/laya`](https://huggingface.co/convaiinnovations/laya).
* Author: Mohammad Javad ([@IrMaho](https://github.com/IrMaho)).
* License: Apache 2.0.
