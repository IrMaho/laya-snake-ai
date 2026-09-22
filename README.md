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

* **🛸 Hostile AI Drones (Dynamic Enemies)**:
  * Autonomous drones spawn and patrol the arena, actively chasing the snake.
  * Contact with an enemy deals 1 Hull Damage (reducing HP).
* **💥 Plasma Projectile Weapon (Shooting System)**:
  * When Ammo > 0, the snake can discharge high-velocity plasma laser bolts along its line of sight.
  * Direct hits vaporize hostile drones in explosive particle bursts (+200 pts) and drop tactical supplies.
* **🌀 Quantum Dimension Warp (Grid Expansion on Demand)**:
  * When cornered against perimeter walls, the snake can cast a Warp Spell to dynamically **expand the grid by 1 column/row**, creating instant escape corridors and altering board geometry in real time.
* **📦 4-Tier Collectibles Ecosystem**:
  * 🍎 **Biomass Energy (Food)**: Lengthens the snake and adds base points.
  * ⚡ **Ammo Cells**: Replenishes plasma munition (+3 rounds).
  * ❤️ **Vitality Heart**: Restores +1 HP (max 3 HP) to survive combat damage.
  * 🎁 **Mystery Tactical Crate**: Triggers perks like **EMP Drone Freeze** or instant 100% Warp charge.
* **🧠 Multi-Faceted Laya System 1 Decision Head**:
  * In every tick, Laya evaluates multiple decisions simultaneously in a single forward pass:
    * `tactical_action`: `["shoot", "evade_and_heal", "cast_grid_expansion", "gather_ammo", "hunt_food"]`
    * `move`: `["up", "down", "left", "right"]`
    * `threat_level`: `["SECURE RECON", "HOSTILE COMBAT", "CRITICAL THREAT"]`
* **🛡 Dual-Engine Spatial Safety**:
  * Mathematical lookahead and flood-fill invariants guarantee zero suicidal wall or neck collisions under any circumstances.

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
