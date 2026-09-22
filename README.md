# 🐍 Laya Cyber-Snake AI · Tactical Battle Arena

<p align="center">
  <b><a href="README.md">🇬🇧 English</a></b> | <b><a href="README_FA.md">🇮🇷 فارسی</a></b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/PyTorch-CUDA%20Accelerated-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch" />
  <img src="https://img.shields.io/badge/FastAPI-High%20Performance-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Model-convaiinnovations%2Flaya-8A2BE2?style=for-the-badge&logo=huggingface&logoColor=white" alt="Laya Model" />
  <img src="https://img.shields.io/badge/V--Sync-60%20FPS%20Canvas-00F0FF?style=for-the-badge" alt="60 FPS" />
  <img src="https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge" alt="License" />
</p>

An ultra-fast, intelligent, and mathematically calibrated **Cyber-Snake Tactical Battle Arena** powered by the **Laya System 1 Decision Model** ([`convaiinnovations/laya`](https://huggingface.co/convaiinnovations/laya)) running locally on **NVIDIA GPU (CUDA)** via FastAPI.

This project showcases a modern hybrid AI architecture: a **Client-Side Analytical Lookahead Engine (Virtual Forward Steps + Flood Fill)** guarantees physical and geometric survival, while the **Laya System-1 Neural Commander** evaluates real-time strategic trade-offs—choosing between plasma beam strikes, defensive quantum warps, tactical retreats, ammo reloads, and health preservation in under 60 milliseconds.

---

## 🎮 Live Gameplay Demo

![Laya AI Snake Gameplay](assets/laya_snake_gameplay.gif)

> **GPU Inference Performance:** ~**35-65 ms** per dual-decision pass (`tactical_action` + `move`) on NVIDIA GeForce RTX 4060 GPU with CUDA acceleration.

---

## ⚔️ Tactical Arena Mechanics & Features

### 1. 🌀 Quantum Dimension Warp (Strict 5-Warp Quota)
* **Elimination of Infinite Expansion:** The snake is granted a strictly metered budget of **5 dimension warps** per sector (+1 row/col in any 4 cardinal directions).
* **Live HUD Quota Gauge:** The top status bar tracks capacity in real time: `WARP: 100% (5/5 Left)`.
* **Laya Server Guidance via `[EXHAUSTED/PROHIBITED]`:** When all 5 warps are spent, the warp trigger is disabled and the server explicitly labels the warp criterion with this prohibitive tag. This prevents Laya from wasting decision probability on unviable expansions, directing its focus toward combat maneuvers.

### 2. 🏆 Sector Mission Objective (Target: 2,000 Pts)
* **No More Infinite Loops:** The game provides a clear victory condition with concrete stakes. Reach **2,000 points** to successfully liberate the sector.
* **Victory Celebration Modal:** Upon achieving the target score, a dedicated mission completion overlay displays breakdown metrics (Final Score, Warps Utilized, Hull Vitality Remaining) accompanied by a synthesized victory fanfare.
* **Sector Progression (`▶ Next Sector`):** Advancing to subsequent sectors increases hostile drone speed, spawn density, and combat intensity.

### 3. 🛡️ 5-Heart Hull Vitality & Invincibility Forcefield (i-Frames)
* **Extended Survival:** Instead of unforgiving one-hit eliminations, the snake possesses **5 Vitality Nodes (HP=5)**.
* **Invulnerability Shield:** Taking damage triggers **25 ticks of translucent cyan forcefield invincibility**, completely preventing sudden multi-hit death spirals from close-quarter enemy encounters.
* **Perimeter Deflector Bounce:** Hitting outer perimeter walls redirects the snake along an open corridor rather than instantly terminating the run.

### 4. 🎥 Built-in 60 FPS Canvas Video Recorder (Zero-Flicker)
* **Root Cause of External Recording Flicker:** In Windows environments with NVIDIA GPUs, Chromium's DirectComposition Multi-Plane Overlays (MPO) can conflict with CSS `backdrop-filter: blur` effects and root DOM transforms during screen capture (OBS, Xbox Game Bar), causing flickering black or transparent frames.
* **The Solution:** Heavy GPU backdrop filters were replaced with solid high-contrast `#050811` surfaces, and rendering was locked to display V-Sync (`requestAnimationFrame`). Additionally, a native in-browser recorder was integrated via the `🎥 Rec (60fps)` button, recording directly from the canvas buffer via HTML5 `canvas.captureStream(60)` and `MediaRecorder` to produce pristine, artifact-free `.webm` video files with one click.

### 5. 💥 High-Voltage Plasma Laser Beam Cannon
* **Line-of-Sight Targeting:** When an enemy drone aligns horizontally or vertically with the snake's head, the laser discharges a blazing beam down the corridor.
* **Drone Vaporization & Particle FX:** Direct hits instantly detonate drones (+250 points), scattering glowing neon particle shrapnel and dropping salvageable items.

### 6. 🛸 Autonomous Hostile AI Drones
* Predator drones spawn at safe distances from the snake's head and maneuver tactically to intercept.
* Approaching drones trigger auditory and visual alerts, creating high-intensity tactical urgency.

### 7. 📦 4-Tier Battlefield Collectibles
| Icon | Item | In-Game Effect |
| :---: | :---: | :--- |
| 🍎 | **Biomass Energy (Food)** | Increases snake length, grants points, and recharges warp capacitor mana |
| ⚡ | **Plasma Ammo Pods** | Reloads +3 laser cannon shots |
| ❤️ | **Nanite Repair Kits (Heart)** | Restores +1 HP (up to maximum of 5 HP) |
| 🎁 | **EMP Hypercube (Gift)** | Freezes all active drones for several seconds and recharges 100% warp energy |

### 8. 🔊 Procedural Web Audio SFX Engine
* **100% Self-Contained:** Zero external audio assets or downloads required. Every sound—laser blasts, drone explosions, item pickups, damage sirens, warp whooshes, and victory fanfares—is synthesized in real time via the browser's native Web Audio API oscillators and gain envelopes.
* Includes one-click audio mute/unmute (`🔊 SFX: ON`) and hotkey `M`.

### 9. 🧠 High-Contrast Semantic Directives with PRIORITY Tags
* Decision criteria are categorized into structured tiers (`PRIORITY-1` through `PRIORITY-3`). This eliminates hesitation in Laya's statistical head, producing prompt and decisive actions under high-stress combat conditions.

---

## ⌨️ Controls & Keyboard Shortcuts

| Key / Control | Action |
| :--- | :--- |
| **Spacebar** | Fire Plasma Laser Cannon manually |
| **E Key** | Trigger Quantum Dimension Warp (+1 Col Left, max 5) |
| **P Key** | Pause / Resume Game |
| **R Key** | Reset / Start New Game |
| **M Key** | Toggle Web Audio SFX (Mute / Unmute) |
| **Arrow Keys / WASD** | Manual steering override |
| **`🤖 AI: ON` Button** | Toggle between autonomous Laya AI and manual human control |
| **`🎥 Rec (60fps)` Button** | Start / Stop native 60 FPS flicker-free video recording and download `.webm` |

---

## 🏗️ System Architecture & Dataflow

```mermaid
graph TD
    A[Browser Client: snake.html] -->|Live Combat State + Questions| B[FastAPI Server: server.py]
    B -->|Generate Structured PRIORITY Criteria| C[Laya ModernBERT Head on CUDA GPU]
    C -->|Multi-Task Probability Distribution| B
    B -->|Tactical Action + Direction Output| A
    A -->|60 FPS V-Sync Canvas Render + Particle Engine| D[Dynamic Battle Arena]

    subgraph Analytical Safety Engine
      E[Line-of-Sight Laser Interception]
      F[Virtual Lookahead & Escape Corridor Proof]
      G[Flood Fill Free-Space Invariance]
      H[Dynamic Dimension Grid Bounds Max 5 Warps]
    end

    A <--> Analytical Safety Engine
```

---

## 🚀 Quickstart Guide

### Prerequisites
* Windows, Linux, or macOS with **Python 3.10+**.
* NVIDIA GPU with CUDA support (or modern multi-core CPU).
* Downloaded Laya model weights:
  ```bash
  git clone https://huggingface.co/convaiinnovations/laya C:\AI\Models\laya
  ```

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start the Tactical Server
```bash
# Optional: customize path if cloned elsewhere
set LAYA_MODEL_PATH=C:\AI\Models\laya

# Run the server
python -u server.py
```
> **Windows Quickstart:** You can simply double-click **`start-game.bat`** to initialize and start the server automatically.

### Step 3: Open in Browser
Launch Chrome, Edge, Firefox, or Brave and navigate to:
```
http://localhost:8080/snake
```

---

## 📡 API Specification (`/v1/systemone`)

### Combat State Request:
`POST /v1/systemone`
```json
{
  "model": "laya",
  "state": {
    "grid": { "cols": 12, "rows": 12, "min_x": 0, "max_x": 11, "min_y": 0, "max_y": 11 },
    "hp": 4,
    "max_hp": 5,
    "ammo": 3,
    "mana": 100,
    "warp_count": 2,
    "max_warps": 5,
    "head": [6, 7],
    "body": [[6, 7], [5, 7], [4, 7], [3, 7]],
    "enemies": [{ "id": 1, "pos": [6, 2], "dist": 5 }],
    "closest_enemy": { "pos": [6, 2], "dist": 5 },
    "enemy_in_line_of_sight": true,
    "los_direction": "up",
    "can_expand_grid": true,
    "items": { "has_food": true, "has_ammo": false, "has_heart": true, "has_gift": false },
    "safe_moves": ["up", "right", "left"],
    "recommended_safe_move": "up"
  },
  "questions": {
    "tactical_action": { "type": "choice" },
    "move": { "type": "choice" }
  }
}
```

### Laya Multi-Decision Response:
```json
{
  "model": "rl-agent",
  "answers": {
    "tactical_action": {
      "type": "choice",
      "choice": "shoot",
      "probabilities": {
        "shoot": 0.7412,
        "evade_and_heal": 0.1105,
        "cast_grid_expansion": 0.0821,
        "gather_ammo": 0.0412,
        "hunt_food": 0.0250
      }
    },
    "move": {
      "type": "choice",
      "choice": "up",
      "probabilities": {
        "up": 0.8845,
        "right": 0.0712,
        "left": 0.0381,
        "down": 0.0062
      }
    }
  },
  "latency_ms": 41.8
}
```

---

## 📊 Performance & Hardware Benchmarks

| Metric | Measured Value | Operational State |
| :--- | :--- | :--- |
| **CUDA GPU Inference Latency** | 35 – 65 ms | Ultra-low latency real-time responsiveness |
| **Graphics Engine Frame Rate** | Locked 60 FPS | Synchronized with monitor V-Sync; zero stutters |
| **In-Browser Video Recorder** | 1080p @ 60 FPS WebM | Zero flicker, zero black frames, direct memory export |
| **GPU VRAM Utilization** | ~1.2 GB | Highly efficient footprint for simultaneous multitasking |

---

## 📄 License & Credits
* Model: [`convaiinnovations/laya`](https://huggingface.co/convaiinnovations/laya).
* Author: Mohammad Javad ([@IrMaho](https://github.com/IrMaho)).
* License: Apache License 2.0.
