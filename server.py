import os
import sys
import time
from typing import Any, Dict, Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# Ensure model directory is in sys.path
MODEL_PATH = os.environ.get("LAYA_MODEL_PATH", r"C:\AI\Models\laya")
if MODEL_PATH not in sys.path:
    sys.path.insert(0, MODEL_PATH)

from rl_agent_api import RLAgent

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

import torch

# Automatic GPU detection or CPU fallback
device = os.environ.get("DEVICE")
if not device:
    device = "cuda" if torch.cuda.is_available() else "cpu"

if device == "cpu":
    # Maximize multi-threaded CPU inference speed
    torch.set_num_threads(os.cpu_count() or 8)

print(f"[*] Loading Laya model from: {MODEL_PATH}")
agent = RLAgent(MODEL_PATH, device=device)
print(f"[OK] Laya model successfully loaded on {device} (threads: {torch.get_num_threads()})!")

app = FastAPI(title="Laya Local System 1 Server")

# Allow all CORS origins for local web client interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DIR_PATH = os.path.dirname(os.path.abspath(__file__))
SNAKE_HTML_PATH = os.path.join(DIR_PATH, "snake.html")

class SystemOneRequest(BaseModel):
    model: Optional[str] = "laya"
    state: Dict[str, Any]
    questions: Dict[str, Any]
    samples: Optional[int] = 1
    steps: Optional[int] = 1
    seed: Optional[int] = 42

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model": "laya",
        "device": device,
        "cuda_available": torch.cuda.is_available(),
        "model_path": MODEL_PATH
    }

@app.get("/")
def get_root():
    if os.path.exists(SNAKE_HTML_PATH):
        return FileResponse(SNAKE_HTML_PATH)
    return {"message": "Laya System 1 Server is running. Open /snake to play."}

@app.get("/snake")
def get_snake():
    if os.path.exists(SNAKE_HTML_PATH):
        return FileResponse(SNAKE_HTML_PATH)
    return JSONResponse(status_code=404, content={"error": "snake.html not found"})

@app.post("/v1/systemone")
async def system_one(payload: SystemOneRequest):
    try:
        t0 = time.perf_counter()
        
        state = dict(payload.state)
        questions = dict(payload.questions)
        
        # When evaluating Snake moves, adapt to Laya's optimal semantic representation
        if "move" in questions:
            head = state.get("head") or state.get("current_head_position") or state.get("snake_head")
            food = state.get("food") or state.get("target_food_position") or state.get("target_food")
            safe_moves = state.get("safe_moves") or state.get("available_safe_moves", [])
            recommended = state.get("recommended_safe_move")
            body = state.get("body") or state.get("snake_body") or state.get("snake_body_cells", [])
            snake_len = state.get("snake_length") or (len(body) if body else 1)
            move_analysis = state.get("move_analysis", {})
            strategy = state.get("strategy", "hunt")
            
            if head and food and isinstance(head, (list, tuple)) and isinstance(food, (list, tuple)):
                dx = food[0] - head[0]
                dy = food[1] - head[1]
                dirs = []
                if dx > 0: dirs.append("east (right)")
                elif dx < 0: dirs.append("west (left)")
                if dy > 0: dirs.append("south (down)")
                elif dy < 0: dirs.append("north (up)")
                food_dir_str = " and ".join(dirs) if dirs else "aligned with food"

                # Build rich, descriptive semantic criteria for each direction
                criteria = {}
                for d in ["up", "down", "left", "right"]:
                    info = move_analysis.get(d, {})
                    nx = info.get("nx", head[0] + {"up": 0, "down": 0, "left": -1, "right": 1}[d])
                    ny = info.get("ny", head[1] + {"up": -1, "down": 1, "left": 0, "right": 0}[d])
                    reason = info.get("reason", "unknown")
                    space = info.get("open_space", 0)
                    tail_ok = info.get("tail_reachable", False)
                    dist = info.get("manhattan_to_food", abs(food[0] - nx) + abs(food[1] - ny))
                    is_safe = info.get("safe", False)
                    is_phys = info.get("isPhysicallyFree", False)

                    if reason == "wall" or nx < 0 or nx >= 12 or ny < 0 or ny >= 12:
                        criteria[d] = f"crash into outer boundary wall at [{nx}, {ny}], fatal collision"
                    elif reason == "neck":
                        criteria[d] = f"reverse 180 degrees into snake neck at [{nx}, {ny}], fatal crash"
                    elif reason == "body":
                        criteria[d] = f"collide into snake body at [{nx}, {ny}], fatal crash"
                    elif reason == "trap" or (is_phys and not is_safe):
                        criteria[d] = f"crash into dead-end trap at [{nx}, {ny}], only {space} spaces for length {snake_len}, tail unreachable"
                    elif is_safe:
                        is_rec = (d == recommended)
                        rec_txt = " (optimal recommended path)" if is_rec else ""
                        tail_txt = "tail reachable" if tail_ok else "open space"
                        criteria[d] = f"safely move {d} towards food with {space} open cells ({tail_txt}, distance={dist}){rec_txt}"
                    else:
                        criteria[d] = f"move {d} towards [{nx}, {ny}]"

                adapted_state = {
                    "game": "Snake 12x12 grid (boundaries x: 0..11, y: 0..11 are lethal walls)",
                    "snake_head": head,
                    "target_food": food,
                    "food_direction": food_dir_str,
                    "snake_length": snake_len,
                    "safe_open_directions": safe_moves,
                    "recommended_safe_move": recommended,
                    "snake_body_cells": body[:30] if len(body) > 30 else body
                }

                if strategy == "hunt":
                    instructions = (
                        f"Which action should the snake head at {head} execute now to safely reach the food at {food} (towards {food_dir_str})? "
                        f"Strictly avoid any move that causes a crash into a wall, neck, body, or dead-end trap."
                    )
                else:
                    instructions = (
                        f"Direct food path is blocked. Which action should the snake head at {head} execute now to safely survive and maximize open space? "
                        f"Strictly avoid any move that causes a crash into a wall, neck, body, or dead-end trap."
                    )

                adapted_questions = {
                    "move": {
                        "type": "choice",
                        "instructions": instructions,
                        "criteria": criteria
                    }
                }
                with torch.inference_mode():
                    result = agent.system_one(adapted_state, adapted_questions)
            else:
                with torch.inference_mode():
                    result = agent.system_one(state, questions)
        else:
            with torch.inference_mode():
                result = agent.system_one(state, questions)
            
        duration_ms = round((time.perf_counter() - t0) * 1000, 2)
        result["latency_ms"] = duration_ms
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "trace": traceback.format_exc()}
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"[*] Starting server at http://localhost:{port}")
    print(f"[*] Open http://localhost:{port}/snake in your browser to play!")
    uvicorn.run(app, host="0.0.0.0", port=port)
