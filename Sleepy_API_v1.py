from fastapi import FastAPI
import uvicorn
from typing import Dict
import os

RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
BLUE    = "\033[94m"
MAGENTA = "\033[95m"  # purple-ish
CYAN    = "\033[96m"
WHITE   = "\033[97m"

# Extras that are often useful
ORANGE  = "\033[38;5;208m"  # 256-color mode
PINK    = "\033[38;5;213m"
PURPLE  = "\033[38;5;129m"
GRAY    = "\033[90m"

# Styles (optional but handy)
BOLD    = "\033[1m"
DIM     = "\033[2m"
UNDERLINE = "\033[4m"

RESET   = "\033[0m"

def print_c(text, color):
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"  # purple-ish
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"

    # Extras that are often useful
    ORANGE  = "\033[38;5;208m"  # 256-color mode
    PINK    = "\033[38;5;213m"
    PURPLE  = "\033[38;5;129m"
    GRAY    = "\033[90m"

    # Styles (optional but handy)
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    UNDERLINE = "\033[4m"

    RESET   = "\033[0m"
    if color.lower() == "red":
        print(f"{RED}{text}{RESET}")
    elif color.lower() == "green":
        print(f"{GREEN}{text}{RESET}")
    elif color.lower() == "yellow":
        print(f"{YELLOW}{text}{RESET}")
    elif color.lower() == "blue":
        print(f"{BLUE}{text}{RESET}")
    elif color.lower() == "magenta":
        print(f"{MAGENTA}{text}{RESET}")
    elif color.lower() == "cyan":
        print(f"{CYAN}{text}{RESET}")
    elif color.lower() == "white":
        print(f"{WHITE}{text}{RESET}")
    elif color.lower() == "orange":
        print(f"{ORANGE}{text}{RESET}")
    elif color.lower() == "pink":
        print(f"{PINK}{text}{RESET}")
    elif color.lower() == "purple":
        print(f"{PURPLE}{text}{RESET}")
    elif color.lower() == "gray":
        print(f"{GRAY}{text}{RESET}")
    else:
        print(text)


app = FastAPI()

total_profit = 0.0
E_stop_v = False    # V = value
pause_trading_v = False
adding_agent = False

agents = {}     # Format {"name" : $$$}
agent_to_add = {}
logs = []

pause_status = ""
total_agents = 0
def update_paused():
    global agents, pause_status
    pause_status = f"{len(paused_agents)}/{total_agents}"
    return pause_status

paused_agents = []

def get_r():
    global pause_trading_v, E_stop_v
    recieved = {"status": "recieved", "Pause traiding" : pause_trading_v, "E-stop" : E_stop_v}  # For agents only
    return recieved


def get_stats():
    global total_profit, E_stop_v, pause_trading_v, pause_status, paused_agents, adding_agent, agent_to_add
    update_paused()
    stats = {
        "total profit" : round(total_profit, 2),
        "E-stop" : E_stop_v,
        "Pause traiding" : pause_trading_v,
        "Pause status" : pause_status,
        "Paused agents": paused_agents,
        "Adding agents" : adding_agent,
        "Agent to add" : agent_to_add
    }
    return stats



@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/-------------END-POINTS---------------") # Litterly just a seprator for printing endpoints
def stfu():
    return "stfu"

@app.get("/status")
def status():
    global E_stop_v, pause_trading_v, total_profit, adding_agent, agent_to_add
    if adding_agent:
        clone = {}
        stats = get_stats()
        clone.update(stats)
        adding_agent = False
        agent_to_add = {}
        return {"status" : clone}
    stats = get_stats()
    return {"status" : stats}

@app.get("/E-stop")
def E_stop():
    global E_stop_v
    E_stop_v = True
    stats = get_stats()
    return {"status" : stats}


@app.get("/Pause-traiding")
def pause_traiding():
    global pause_trading_v
    pause_trading_v = True
    stats = get_stats()
    return {"status" : stats}



# update list
@app.get("/update-profit")
def update_profit(value: float, Aname: str):
    global total_profit, pause_trading_v
    update_paused()
    total_profit += value
    if pause_trading_v:
        if Aname not in paused_agents:
            paused_agents.append(Aname)
        else:
            print_c(F"ERROR: FAILED TO PAUSE AGENT {Aname}{RESET}", "red")
    r = get_r()
    return r


@app.post("/load-agents")
def load_agents(payload: Dict):
    global agents, total_agents
    agents.update(payload)
    total_agents = len(agents["agents"])
    return {"status": "updated", "agents": agents}



@app.get("/add-agent")
def add_agent(agent_name = str, id = str):
    global adding_agent, agent_to_add
    if agent_name not in agents["agents"]:
        agent_to_add[agent_name] = id
        adding_agent = True
        stats = get_stats()
        return stats
    else:
        return {"status": "Agent already exists"}
    

@app.get("/resume-all")
def resume_all():
    global E_stop_v, pause_trading_v, pause_status, paused_agents
    E_stop_v = False
    pause_trading_v = False
    pause_status = "0/0"
    paused_agents = []
    stats = get_stats()
    return stats

@app.get("/get-agents")
def get_agents():
    global agents
    return agents   # no stats cuz idgaf


@app.get("/update-logs")
def update_logs(agent_name: str, action: str):
    global logs, E_stop_v, paused_agents
    if len(logs) > 100:    # to keep things fresh ;]
        logs = []
    logs.append(f"{agent_name}: {action}")
    recieved = get_r()
    return recieved

@app.get("/get-logs")
def get_logs():
    global logs
    return logs

for route in app.routes:
    hi = ["/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"]
    if route.path not in hi:
        print("http://127.0.0.1:8000"+route.path)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

"""
if __name__ == "__main__":
    uvicorn.run("Sleepy_API_v1:app", host="0.0.0.0", port=8000, reload=True)
"""

# Querei: http://127.0.0.1:8000/update-profit?value=1036.39871243?Aname=hiiii
# Get: http://127.0.0.1:8000/total-profit