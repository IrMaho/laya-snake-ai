import os
import sys
import time
from typing import Any, Dict, Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

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

device = os.environ.get("DEVICE")
if not device:
    device = "cuda" if torch.cuda.is_available() else "cpu"
if device == "cpu":
    torch.set_num_threads(os.cpu_count() or 8)

print(f"[*] Loading Laya model from: {MODEL_PATH}")
agent = RLAgent(MODEL_PATH, device=device)
print(f"[OK] Laya loaded on {device} (threads: {torch.get_num_threads()})!")

app = FastAPI(title="Laya Tactical Arena")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

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
    return {"status": "healthy", "model": "laya", "device": device, "cuda_available": torch.cuda.is_available()}

@app.get("/")
def get_root():
    if os.path.exists(SNAKE_HTML_PATH):
        return FileResponse(SNAKE_HTML_PATH)
    return {"message": "Laya Arena running. Open /snake"}

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

        is_battle = "tactical_action" in questions or "enemies" in state or "hp" in state

        if "move" in questions or is_battle:
            head = state.get("head") or state.get("snake_head")
            food = state.get("food") or state.get("target_food")
            safe_moves = state.get("safe_moves", [])
            recommended = state.get("recommended_safe_move")
            body = state.get("body", [])
            snake_len = state.get("snake_length") or len(body)
            move_analysis = state.get("move_analysis", {})

            grid_info = state.get("grid", {})
            min_x = grid_info.get("min_x", 0)
            max_x = grid_info.get("max_x", 11)
            min_y = grid_info.get("min_y", 0)
            max_y = grid_info.get("max_y", 11)

            hp = state.get("hp", 5)
            max_hp = state.get("max_hp", 5)
            ammo = state.get("ammo", 0)
            mana = state.get("mana", 100)
            enemies = state.get("enemies", [])
            items = state.get("items", {})
            closest_enemy = state.get("closest_enemy")
            can_expand = state.get("can_expand_grid", False)
            enemy_in_los = state.get("enemy_in_line_of_sight", False)
            los_dir = state.get("los_direction", "none")
            priority_target = state.get("priority_target", "food")

            if head and isinstance(head, (list, tuple)):
                target = food if food else head
                # Build move criteria
                move_criteria = {}
                for d in ["up", "down", "left", "right"]:
                    info = move_analysis.get(d, {})
                    nx = info.get("nx", head[0] + {"up": 0, "down": 0, "left": -1, "right": 1}[d])
                    ny = info.get("ny", head[1] + {"up": -1, "down": 1, "left": 0, "right": 0}[d])
                    reason = info.get("reason", "unknown")
                    space = info.get("open_space", 0)
                    is_safe = info.get("safe", False)
                    is_enemy = info.get("has_enemy", False)

                    if reason == "wall" or nx < min_x or nx > max_x or ny < min_y or ny > max_y:
                        move_criteria[d] = f"FATAL: crash into wall at [{nx},{ny}], instant death"
                    elif reason == "neck":
                        move_criteria[d] = f"FATAL: reverse into own neck at [{nx},{ny}], instant death"
                    elif reason == "body":
                        move_criteria[d] = f"FATAL: collide into own body at [{nx},{ny}], instant death"
                    elif is_enemy or reason == "enemy":
                        move_criteria[d] = f"DANGER: step into hostile drone at [{nx},{ny}], takes 1 HP damage"
                    elif reason == "trap":
                        move_criteria[d] = f"TRAP: dead-end corridor at [{nx},{ny}], only {space} cells for body length {snake_len}"
                    elif is_safe and d == recommended:
                        move_criteria[d] = f"BEST: safely move {d} with {space} open cells, closest to target (RECOMMENDED)"
                    elif is_safe:
                        move_criteria[d] = f"SAFE: move {d} with {space} open cells available"
                    else:
                        move_criteria[d] = f"RISKY: move {d} to [{nx},{ny}], limited space"

                adapted_state = {
                    "game": f"Snake Battle Arena ({max_x-min_x+1}x{max_y-min_y+1})",
                    "head": head,
                    "hp": f"{hp}/{max_hp}",
                    "ammo": ammo,
                    "enemies_count": len(enemies),
                    "nearest_enemy": f"at {closest_enemy['pos']} dist {closest_enemy['dist']}" if closest_enemy else "none",
                    "line_of_sight": f"enemy in {los_dir}" if enemy_in_los else "clear",
                    "safe_dirs": safe_moves,
                    "best_move": recommended,
                    "priority": priority_target
                }

                adapted_questions = {}

                # Tactical action - use PRIORITY-ranked decisive criteria
                if "tactical_action" in questions or is_battle:
                    tc = {}

                    # SHOOT - only offer as high-priority when useful
                    if enemy_in_los and ammo > 0:
                        tc["shoot"] = f"[PRIORITY-1] FIRE plasma {los_dir} NOW! Enemy is directly in line of sight and ammo={ammo}. Guaranteed hit and kill!"
                    elif ammo > 0 and closest_enemy and closest_enemy.get("dist", 99) <= 3:
                        tc["shoot"] = f"[PRIORITY-2] Shoot towards approaching enemy at distance {closest_enemy['dist']}"
                    else:
                        tc["shoot"] = "[LOW] No clear target. Wasting ammo."

                    # EVADE_AND_HEAL
                    if hp <= 2 and items.get("has_heart"):
                        tc["evade_and_heal"] = f"[PRIORITY-1] CRITICAL: HP={hp}/{max_hp}! Heart pack on map. Must heal immediately or risk death!"
                    elif hp <= 2:
                        tc["evade_and_heal"] = f"[PRIORITY-2] HP is dangerously low ({hp}/{max_hp}), evade all enemies"
                    elif closest_enemy and closest_enemy.get("dist", 99) <= 2:
                        tc["evade_and_heal"] = f"[PRIORITY-2] Enemy at distance {closest_enemy['dist']}! Take evasive action"
                    else:
                        tc["evade_and_heal"] = "[LOW] Not in immediate danger, no urgent need to evade"

                    # GRID EXPANSION
                    if can_expand:
                        tc["cast_grid_expansion"] = "[PRIORITY-1] QUANTUM WARP READY! Boundary wall is directly adjacent. Expand grid boundary immediately to escape corner trap and open new terrain!"
                    else:
                        tc["cast_grid_expansion"] = "[LOW/LOCKED] Quantum warp drive charging or not touching perimeter wall."

                    # GATHER AMMO
                    if ammo == 0 and items.get("has_ammo"):
                        tc["gather_ammo"] = "[PRIORITY-1] WEAPONS DRY: Ammo is 0! Supply crate on field. Collect ammo to restore laser capabilities!"
                    elif ammo == 0:
                        tc["gather_ammo"] = "[PRIORITY-3] Weapons dry, but no ammo crate currently available on map."
                    else:
                        tc["gather_ammo"] = f"[LOW] Plasma laser has {ammo} charges ready. No ammo resupply needed."

                    # HUNT FOOD
                    if not enemy_in_los and (not closest_enemy or closest_enemy.get("dist", 99) > 3):
                        tc["hunt_food"] = "[PRIORITY-1] SECTOR SECURE! Move directly towards biomass food to grow length, boost score, and recharge warp mana!"
                    else:
                        tc["hunt_food"] = "[PRIORITY-3] Combat situation active. Food gathering secondary to tactical defense."

                    adapted_questions["tactical_action"] = {
                        "type": "choice",
                        "instructions": (
                            f"Cyber-Snake Combat System: HP={hp}/{max_hp}, Ammo={ammo}, Enemies={len(enemies)}, LineOfSight={los_dir if enemy_in_los else 'none'}. "
                            f"Select the SINGLE highest-priority tactical action. "
                            f"Execute PRIORITY-1 directives immediately to survive and dominate."
                        ),
                        "criteria": tc
                    }

                if "move" in questions:
                    adapted_questions["move"] = {
                        "type": "choice",
                        "instructions": (
                            f"Snake head at {head}. Recommended safe path is '{recommended}'. "
                            f"Select the safest navigation direction. "
                            f"BEST=optimal tactical path towards objective. "
                            f"SAFE=valid clear corridor. "
                            f"NEVER select FATAL, TRAP, or DANGER directions."
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

        result["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e), "trace": traceback.format_exc()})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"[*] Starting at http://localhost:{port}")
    print(f"[*] Open http://localhost:{port}/snake to play!")
    uvicorn.run(app, host="0.0.0.0", port=port)
