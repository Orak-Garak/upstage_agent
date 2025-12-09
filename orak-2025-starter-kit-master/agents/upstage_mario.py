import openai
import re
import os

SYSTEM_PROMPT = """
You are an expert AI agent playing Super Mario. Your goal is to reach the flag without dying.

### Game Rules ###
- Mario automatically moves RIGHT at a fixed speed
- You control ONLY the jump level (0-6)
- Each jump level determines horizontal distance (x) and height (y):
  - Level 0: No jump, just walk
  - Level 1: +42 in x, +35 in y
  - Level 2: +56 in x, +46 in y
  - Level 3: +63 in x, +53 in y
  - Level 4: +70 in x, +60 in y
  - Level 5: +77 in x, +65 in y
  - Level 6: +84 in x, +68 in y (highest/farthest)

### Objects (Size info) ###
- Mario: 15x13
- Bricks/Question Blocks: 16x16
- Monster Goomba: 16x16 (enemy - jump on to defeat)
- Monster Koopa: 20x24 (turtle enemy)
- Warp Pipe: 30xHeight (must jump over)
- Pit: Fall = death! Must jump over
- Ground level: y=32

### Strategy ###
1. Jump BEFORE reaching obstacles (Mario moves continuously)
2. For Goombas/Koopas ahead: small jump (Level 1-2) to stomp or pass
3. For Pipes: check height, use appropriate level
4. For Pits: calculate width, use sufficient jump level
5. For high blocks in the way: use Level 5-6
6. If no obstacles nearby: Level 0 (save jumps)

### Output Format ###
### Reasoning
<brief analysis of current obstacles>
### Actions
Explain: <why this jump level>
Jump Level: <0-6>
"""

USER_PROMPT = """
### Current Game State
{cur_state_str}

### Previous State
{prev_state_str}

### Last Action
{last_action}

Analyze Mario's position and nearby obstacles. Choose the best jump level.
Respond ONLY in this format:
### Reasoning
<analysis>
### Actions
Explain: <reasoning>
Jump Level: <0-6>
"""

class UpstageMarioAgent:
    TRACK = "TRACK2"
    
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.environ.get("UPSTAGE_API_KEY", "up_UKdOB8JQt7dAF1XUGi5GmZ02mimkX"),
            base_url="https://api.upstage.ai/v1/solar"
        )
        self.prev_state_str = "N/A"
        self.last_action = "No action yet"

    def act(self, obs):
        cur_state_str = obs.get("obs_str", "")

        try:
            response = self.client.chat.completions.create(
                model="solar-pro",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": USER_PROMPT.format(
                        cur_state_str=cur_state_str,
                        prev_state_str=self.prev_state_str,
                        last_action=self.last_action
                    )}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            output = response.choices[0].message.content.strip()
            action = self._parse_action(output)
            
        except Exception as e:
            print(f"API Error: {e}")
            action = "Jump Level: 0"

        self.prev_state_str = cur_state_str
        self.last_action = action

        return action

    def _parse_action(self, output):
        """Extract Jump Level from output"""
        match = re.search(r"Jump Level:\s*(\d+)", output, re.IGNORECASE)
        if match:
            level = int(match.group(1))
            if 0 <= level <= 6:
                return f"Jump Level: {level}"
        return "Jump Level: 0"


