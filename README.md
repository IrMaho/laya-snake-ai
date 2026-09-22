# 🐍 Laya AI Snake - System 1 Autonomous Decision Engine

<p align="center">
  <b><a href="README.md">🇬🇧 English</a></b> | <b><a href="README_FA.md">🇮🇷 فارسی</a></b>
</p>

An ultra-fast, intelligent, and mathematically calibrated **Snake AI** powered by the **Laya System 1 Decision Model** ([`convaiinnovations/laya`](https://huggingface.co/convaiinnovations/laya)) running locally on **NVIDIA GPU (CUDA)** via FastAPI.

Featuring a **Dual-Engine Forward Virtual Lookahead System (1000+ Steps)** combined with the Laya System 1 Neural Decision Head to eliminate suicidal traps, wall collisions, and robotic circling while hunting apples at maximum throughput.

---

## 🎮 Gameplay Demo

![Laya AI Snake Gameplay](assets/laya_snake_gameplay.gif)

> **Live Inference**: ~35-45 ms per move on NVIDIA GeForce RTX 4060 GPU with CUDA acceleration. Zero hallucination, non-autoregressive single forward-pass decision head.

---

## 🌟 Key Features

* **⚡ Ultra-Low Latency Inference**: Runs locally on your GPU using ModernBERT-large (421M parameters) with PyTorch `inference_mode` and automatic mixed precision (AMP).
* **🧠 True Forward Lookahead (Dual-Engine System)**:
  * **🎯 Safe Direct Hunt**: Computes the shortest BFS trajectory to the apple and performs a **Virtual Simulation** to ensure that after eating, the snake can still safely reach its own tail and has sufficient escape space.
  * **🛡 Intelligent Tail-Chase Survival**: If eating the food would trap the snake, it seamlessly switches to survival mode, following its tail and maximizing open flood-fill space until an escape path clears.
* **🚫 100% Trap & Wall Prevention**:
  * Evaluates dead-end pockets in real time (`space < snake.length + 1 && !tailReachable`).
  * Emits semantic hazard tags (`FATAL WALL`, `FATAL BODY`, `DEAD-END TRAP`) directly to Laya's decision head.
  * Employs an absolute physical safety guard ensuring zero wall or neck collisions under any circumstances.
* **📊 Real-Time Interactive Dashboard**:
  * Live move probability bars with exact percentage scoring.
  * Dynamic Strategy Badge (`🎯 Hunt (Direct)` vs `🛡 Survive (Tail-Chase)`).
  * Real-time inspection of the `/v1/systemone` JSON payload, current head/food coordinates, snake length, and fill percentage.

---

## 🏗️ Architecture Overview

```mermaid
graph TD
    A[Browser Client: snake.html] -->|JSON State + Questions| B[FastAPI Server: server.py]
    B -->|State Serialization + Semantic Criteria| C[Laya ModernBERT Head]
    C -->|Calibrated Probabilities| B
    B -->|Choice & Metrics| A
    A -->|Apply Move| D[Canvas Board 12x12]

    subgraph Decision Engine
      E[BFS Direct Path]
      F[Virtual Snake Simulation]
      G[Flood Fill Open Space]
      H[Tail Reachability Invariant]
    end

    A <--> Decision Engine
```

### Decision Flow:
1. **Perception**: The client scans the 12×12 board, head coordinates, food position, and the full list of body segments.
2. **Virtual Lookahead**:
   - Shortest path to food is found using Breadth-First Search (BFS).
   - A virtual clone of the snake steps through the trajectory to the apple.
   - If after eating, the virtual head can reach the virtual tail with sufficient space, the hunt is certified **100% Safe**.
3. **Hazard Tagging**: Directions leading outside the grid, into the neck, into body segments, or into inescapable pockets are marked with lethal crash criteria.
4. **Laya System 1 Inference**: The ModernBERT model evaluates the state and criteria in a single 35ms pass, scoring the optimal move with high probability (~75-85%).
5. **Action Execution**: The board updates smoothly at 15ms-45ms intervals or Turbo Mode.

---

## 🚀 Quickstart Guide

### Prerequisites
* Windows, Linux, or macOS with **Python 3.10+**.
* An NVIDIA GPU with CUDA support (or CPU with multi-threading).
* The Laya model downloaded locally:
  ```bash
  # Example target directory: C:\AI\Models\laya
  git clone https://huggingface.co/convaiinnovations/laya C:\AI\Models\laya
  ```

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Start the Laya Server
Set the model path (if different from default `C:\AI\Models\laya`) and start `server.py`:
```bash
# Optional: specify custom path
set LAYA_MODEL_PATH=C:\AI\Models\laya

# Run server
python -u server.py
```
Or simply double-click **`start-game.bat`**.

You should see:
```text
[*] Loading Laya model from: C:\AI\Models\laya
[OK] Laya model successfully loaded on cuda (threads: 14)!
[*] Starting server at http://localhost:8080
[*] Open http://localhost:8080/snake in your browser to play!
```

### Step 3: Launch the Game
Open your web browser and navigate to:
```
http://localhost:8080/snake
```
Click **Start** and watch Laya play autonomously!

---

## ⚙️ Speed Modes

You can dynamically adjust the execution rate from the UI dropdown:
* **⚡ Turbo (Max GPU)**: Zero delay event loop tick (`0ms`). Moves execute as fast as the GPU can process inferences (~25 moves/sec).
* **🚀 Fast (15ms)**: Ideal for visual inspection with high responsiveness.
* **⏱ Normal (45ms)**: Relaxed pacing for observing decision probabilities.

---

## 📡 API Specification (`/v1/systemone`)

### Request
`POST /v1/systemone`
```json
{
  "model": "laya",
  "state": {
    "head": [5, 6],
    "food": [7, 0],
    "snake_length": 4,
    "body": [[5, 6], [4, 6], [3, 6], [2, 6]],
    "strategy": "hunt",
    "safe_moves": ["up", "down", "right"],
    "recommended_safe_move": "up",
    "move_analysis": {
      "up": { "safe": true, "isPhysicallyFree": true, "reason": "safe", "open_space": 140 },
      "down": { "safe": true, "isPhysicallyFree": true, "reason": "safe", "open_space": 140 },
      "left": { "safe": false, "isPhysicallyFree": false, "reason": "neck", "open_space": 0 },
      "right": { "safe": true, "isPhysicallyFree": true, "reason": "safe", "open_space": 140 }
    }
  },
  "questions": {
    "move": { "type": "choice" }
  }
}
```

### Response
```json
{
  "model": "rl-agent",
  "answers": {
    "move": {
      "type": "choice",
      "choice": "up",
      "probabilities": {
        "up": 0.8058,
        "down": 0.0506,
        "left": 0.0268,
        "right": 0.1169
      },
      "confidence": 0.6889
    }
  },
  "latency_ms": 38.4
}
```

---

## 📄 License & Credits
* Model: [`convaiinnovations/laya`](https://huggingface.co/convaiinnovations/laya).
* Author: Mohammad Javad ([@IrMaho](https://github.com/IrMaho))
* License: Apache 2.0.
