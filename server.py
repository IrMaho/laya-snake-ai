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

app = FastAPI(title="Laya Tactical Battle Arena Server")

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
    return {"message": "Laya Tactical Battle Arena is running. Open /snake to play."}

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
        
        # Check if tactical battle mode is active
        is_battle = "tactical_action" in questions or "enemies" in state or "hp" in state
        
        if "move" in questions or is_battle:
            head = state.get("head") or state.get("current_head_position") or state.get("snake_head")
            food = state.get("food") or state.get("target_food_position") or state.get("target_food")
            safe_moves = state.get("safe_moves") or state.get("available_safe_moves", [])
            recommended = state.get("recommended_safe_move")
            body = state.get("body") or state.get("snake_body") or state.get("snake_body_cells", [])
            snake_len = state.get("snake_length") or (len(body) if body else 1)
            move_analysis = state.get("move_analysis", {})
            strategy = state.get("strategy", "hunt")
            
            # Dynamic grid dimensions
            grid_info = state.get("grid", {})
            cols = grid_info.get("cols", 12)
            rows = grid_info.get("rows", 12)
            min_x = grid_info.get("min_x", 0)
            max_x = grid_info.get("max_x", cols - 1)
            min_y = grid_info.get("min_y", 0)
            max_y = grid_info.get("max_y", rows - 1)
            
            # Tactical battle variables
            hp = state.get("hp", 3)
            max_hp = state.get("max_hp", 3)
            ammo = state.get("ammo", 0)
            mana = state.get("mana", 100)
            enemies = state.get("enemies", [])
            items = state.get("items", {})
            closest_enemy = state.get("closest_enemy")
            can_expand = state.get("can_expand_grid", False)
            expand_side = state.get("recommended_expand_side", "none")
            enemy_in_los = state.get("enemy_in_line_of_sight", False)
            los_dir = state.get("los_direction", "none")

            if head and isinstance(head, (list, tuple)):
                # Calculate direction string to current target (food or nearest item)
                target_pos = food if food else (head[0], head[1])
                dx = target_pos[0] - head[0]
                dy = target_pos[1] - head[1]
                dirs = []
                if dx > 0: dirs.append("east (right)")
                elif dx < 0: dirs.append("west (left)")
                if dy > 0: dirs.append("south (down)")
                elif dy < 0: dirs.append("north (up)")
                food_dir_str = " and ".join(dirs) if dirs else "aligned with objective"

                # Build rich, descriptive semantic criteria for each direction
                move_criteria = {}
                for d in ["up", "down", "left", "right"]:
                    info = move_analysis.get(d, {})
                    nx = info.get("nx", head[0] + {"up": 0, "down": 0, "left": -1, "right": 1}[d])
                    ny = info.get("ny", head[1] + {"up": -1, "down": 1, "left": 0, "right": 0}[d])
                    reason = info.get("reason", "unknown")
                    space = info.get("open_space", 0)
                    tail_ok = info.get("tail_reachable", False)
                    dist = info.get("manhattan_to_food", abs(target_pos[0] - nx) + abs(target_pos[1] - ny))
                    is_safe = info.get("safe", False)
                    is_phys = info.get("isPhysicallyFree", False)
                    is_enemy = info.get("has_enemy", False)

                    if reason == "wall" or nx < min_x or nx > max_x or ny < min_y or ny > max_y:
                        move_criteria[d] = f"crash into perimeter wall at [{nx}, {ny}], fatal collision"
                    elif reason == "neck":
                        move_criteria[d] = f"reverse 180 degrees into snake neck at [{nx}, {ny}], fatal crash"
                    elif reason == "body":
                        move_criteria[d] = f"collide into snake body at [{nx}, {ny}], fatal crash"
                    elif is_enemy or reason == "enemy":
                        move_criteria[d] = f"step directly into hostile Drone at [{nx}, {ny}], lethal contact damage!"
                    elif reason == "trap" or (is_phys and not is_safe):
                        move_criteria[d] = f"enter dead-end trap at [{nx}, {ny}], only {space} spaces for length {snake_len}, tail unreachable"
                    elif is_safe:
                        is_rec = (d == recommended)
                        rec_txt = " (optimal recommended path)" if is_rec else ""
                        tail_txt = "tail reachable" if tail_ok else "open space"
                        move_criteria[d] = f"safely maneuver {d} towards objective with {space} open cells ({tail_txt}, distance={dist}){rec_txt}"
                    else:
                        move_criteria[d] = f"move {d} towards [{nx}, {ny}]"

                adapted_state = {
                    "arena": f"Tactical Grid {cols}x{rows} (boundaries: x {min_x}..{max_x}, y {min_y}..{max_y})",
                    "snake_head": head,
                    "snake_status": f"HP: {hp}/{max_hp}, Ammo: {ammo} plasma rounds, Mana: {mana}%",
                    "snake_length": snake_len,
                    "enemies_detected": len(enemies),
                    "enemy_proximity": f"Closest enemy at {closest_enemy['pos']} (distance {closest_enemy['dist']})" if closest_enemy else "No immediate enemies",
                    "line_of_sight": f"Enemy aligned in {los_dir} line of sight!" if enemy_in_los else "No enemy in direct line of fire",
                    "target_objective": food if food else "Patrol",
                    "safe_directions": safe_moves,
                    "recommended_move": recommended,
                    "snake_body_cells": body[:20] if len(body) > 20 else body
                }

                adapted_questions = {}

                # Tactical combat action question
                if "tactical_action" in questions or is_battle:
                    action_criteria = {}
                    if enemy_in_los and ammo > 0:
                        action_criteria["shoot"] = f"DISCHARGE plasma cannon {los_dir} to destroy hostile drone in line of sight (Ammo: {ammo} remaining)"
                    elif ammo > 0 and closest_enemy and closest_enemy.get("dist", 99) <= 4:
                        action_criteria["shoot"] = f"Prepare weapon and shoot towards approaching drone at distance {closest_enemy['dist']}"
                    else:
                        action_criteria["shoot"] = "Fire weapon into open space (low efficiency, no target lined up)"

                    if hp < max_hp and items.get("has_heart"):
                        action_criteria["evade_and_heal"] = f"URGENT: HP is low ({hp}/{max_hp}), break combat and navigate towards ❤️ Heart Pack to restore vitality"
                    elif closest_enemy and closest_enemy.get("dist", 99) <= 2:
                        action_criteria["evade_and_heal"] = f"Evasive maneuver: hostile drone is critically close ({closest_enemy['dist']} steps), dodge attack radius"
                    else:
                        action_criteria["evade_and_heal"] = "Maintain standard defensive spacing"

                    if can_expand:
                        action_criteria["cast_grid_expansion"] = f"WARP SPELL: Snake is pinned near boundary wall; cast dimension shift to expand grid {expand_side} by 1 column/row and create an escape corridor!"
                    else:
                        action_criteria["cast_grid_expansion"] = "Warp mana recharging (requires 100% mana)"

                    if ammo == 0 and items.get("has_ammo"):
                        action_criteria["gather_ammo"] = "Ammo is depleted! Navigate to ⚡ Ammo Crate to reload 3 plasma rounds"
                    else:
                        action_criteria["gather_ammo"] = "Stockpile additional ammo cells"

                    action_criteria["hunt_food"] = "Tactical field is secure: pursue 🍎 Energy Food to increase combat length and score"

                    adapted_questions["tactical_action"] = {
                        "type": "choice",
                        "instructions": (
                            f"You are the Tactical AI Commander for the Cyber-Snake. "
                            f"Current Status: HP={hp}/{max_hp}, Ammo={ammo}, Mana={mana}%. "
                            f"What is the single highest-priority tactical combat decision right now?"
                        ),
                        "criteria": action_criteria
                    }

                # Movement question
                if "move" in questions:
                    adapted_questions["move"] = {
                        "type": "choice",
                        "instructions": (
                            f"Which movement direction should the snake head at {head} execute now? "
                            f"Strictly avoid outer perimeter walls, neck reversal, body collisions, or stepping onto enemies."
                        ),
                        "criteria": move_criteria
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
    print(f"[*] Starting Tactical Battle Arena Server at http://localhost:{port}")
    print(f"[*] Open http://localhost:{port}/snake in your browser to play!")
    uvicorn.run(app, host="0.0.0.0", port=port)
