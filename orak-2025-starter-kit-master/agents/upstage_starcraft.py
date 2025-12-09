import openai
import re
import os

SYSTEM_PROMPT = """
You are an expert StarCraft II Protoss player. Your goal is to defeat the Zerg AI opponent.

### Core Mechanics ###
- **Resources**: Minerals, Vespene Gas
- **Supply**: Cap (max population), Used (current), Left (available)
- **Workers**: Probes gather resources
- **Army**: Military units for combat

### IMPORTANT: You must output exactly 5 actions per turn! ###

### Build Order Priority ###
1. Early Game: Probes, Pylons (supply), Gateway
2. Mid Game: More Gateways, Cybernetics Core, Stalkers/Zealots
3. Late Game: Expand (Nexus), Tech buildings, Army

### Key Actions ###
- TRAIN PROBE: Make workers (need 50 minerals, 1 supply)
- BUILD PYLON: Increase supply cap (100 minerals)
- BUILD GATEWAY: Train ground units (150 minerals)
- BUILD NEXUS: Expand economy (400 minerals)
- BUILD ASSIMILATOR: Gather gas (75 minerals)
- TRAIN ZEALOT: Basic melee unit (100 minerals, 2 supply)
- TRAIN STALKER: Ranged unit (125 minerals, 50 gas, 2 supply)
- MULTI-ATTACK: Send army to attack enemy
- CHRONOBOOST NEXUS: Speed up probe production
- EMPTY ACTION: Do nothing (use when waiting for resources)

### Strategy Tips ###
1. Always make Probes until ~20 workers
2. Keep building Pylons to avoid supply block
3. Build Gateway before making army units
4. Build Assimilator for gas (needed for Stalkers)
5. Attack when you have a decent army (6+ units)

### Output Format ###
### Reasoning
<brief strategy explanation>
### Actions
1: <ACTION_NAME>
2: <ACTION_NAME>
3: <ACTION_NAME>
4: <ACTION_NAME>
5: <ACTION_NAME>
"""

USER_PROMPT = """
### Current Game State
{cur_state_str}

Based on the current resources, buildings, and units, choose 5 actions.
Remember: Always output exactly 5 actions!

### Reasoning
<your strategy>
### Actions
1: <action>
2: <action>
3: <action>
4: <action>
5: <action>
"""

class UpstageStarCraftAgent:
    TRACK = "TRACK2"
    
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.environ.get("UPSTAGE_API_KEY", "up_UKdOB8JQt7dAF1XUGi5GmZ02mimkX"),
            base_url="https://api.upstage.ai/v1/solar"
        )

    def act(self, obs):
        cur_state_str = obs.get("obs_str", "")
        game_info = obs.get("game_info", {})

        # If obs_str is empty, use default actions (early game strategy)
        if not cur_state_str or cur_state_str.strip() == "":
            print("Warning: obs_str is empty, using default early game actions")
            return self._default_actions()

        try:
            response = self.client.chat.completions.create(
                model="solar-pro",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": USER_PROMPT.format(
                        cur_state_str=cur_state_str
                    )}
                ],
                temperature=0.3,
                max_tokens=600
            )
            
            output = response.choices[0].message.content.strip()
            actions = self._parse_actions(output)
            
        except Exception as e:
            print(f"API Error: {e}")
            actions = self._default_actions()

        return actions

    def _parse_actions(self, output):
        """Extract 5 actions from output"""
        actions = []
        
        # Find all action lines
        lines = output.split('\n')
        for line in lines:
            match = re.match(r'^\s*\d+:\s*(.+)$', line.strip())
            if match:
                action = match.group(1).strip().upper()
                # Validate action
                if self._is_valid_action(action):
                    actions.append(action)
        
        # Pad with EMPTY ACTION if needed
        while len(actions) < 5:
            actions.append("EMPTY ACTION")
        
        # Format output
        result = "Actions\n"
        for i, action in enumerate(actions[:5], 1):
            result += f"{i}: {action}\n"
        
        return result.strip()

    def _is_valid_action(self, action):
        """Check if action is valid"""
        valid_prefixes = [
            "TRAIN", "BUILD", "RESEARCH", "SCOUTING", 
            "MULTI-ATTACK", "MULTI-RETREAT", "CHRONOBOOST", "EMPTY ACTION"
        ]
        return any(action.startswith(prefix) for prefix in valid_prefixes)

    def _default_actions(self):
        """Default safe actions"""
        return """Actions
1: TRAIN PROBE
2: BUILD PYLON
3: TRAIN PROBE
4: EMPTY ACTION
5: EMPTY ACTION"""

