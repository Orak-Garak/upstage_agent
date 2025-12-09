import openai
import re
import os

SYSTEM_PROMPT = """
You are an expert AI agent specialized in playing the 2048 game with advanced strategic reasoning. 
Your primary goal is to achieve the highest possible tile value while maintaining long-term playability.

### 2048 Game Rules ### 
1. The game is played on a 4×4 grid. Tiles slide in one of four directions: 'up', 'down', 'left', or 'right'. 
2. Only two consecutive tiles with the SAME value can merge.
3. Merging is directional: Row-based merges occur on 'left' or 'right', Column-based on 'up' or 'down'.
4. All tiles first slide in the chosen direction, then merges are applied.
5. A tile can merge only once per move.
6. After every valid action, a new tile (90% chance of 2, 10% chance of 4) appears.
7. The game ends when the board is full and no valid merges are possible.

### Strategy Tips ###
1. Keep the highest tile in a corner (preferably bottom-left or bottom-right)
2. Build a "snake" pattern to organize tiles
3. Avoid moving up unless absolutely necessary
4. Try to keep tiles organized in descending order

### Decision Output Format ### 
Return your decision in this exact format:
### Reasoning
<brief explanation>
### Actions
<up, right, left, or down>
"""

USER_PROMPT = """
### Current Board State
{cur_state_str}

### Previous State
{prev_state_str}

### Last Action
{action}

Analyze the board and choose the best move. Respond ONLY in this format:
### Reasoning
<your reasoning>
### Actions
<direction>
"""

class UpstageTwentyFourtyEightAgent:
    TRACK = "TRACK2"
    
    def __init__(self):
        # Upstage API - OpenAI 호환!
        self.client = openai.OpenAI(
            api_key=os.environ.get("UPSTAGE_API_KEY", "up_UKdOB8JQt7dAF1XUGi5GmZ02mimkX"),
            base_url="https://api.upstage.ai/v1/solar"
        )
        self.prev_state_str = "N/A"
        self.last_action = "No action yet"

    def act(self, obs):
        game_info = obs.get("game_info", {})
        cur_state_str = obs.get("obs_str", "")

        try:
            response = self.client.chat.completions.create(
                model="solar-pro",  # Upstage Solar Pro 모델
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": USER_PROMPT.format(
                        cur_state_str=cur_state_str,
                        prev_state_str=self.prev_state_str,
                        action=self.last_action
                    )}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            output = response.choices[0].message.content.strip()
            action = self._parse_actions(output)
            
        except Exception as e:
            print(f"API Error: {e}")
            action = "left"  # Fallback
        
        # Validate action
        if action not in ["left", "right", "up", "down"]:
            action = "left"

        self.prev_state_str = cur_state_str
        self.last_action = action

        return action

    def _parse_actions(self, output):
        """Extract action from ### Actions section"""
        actions_match = re.search(r"### Actions\s*\n(.+)", output, re.IGNORECASE | re.DOTALL)
        if actions_match:
            action = actions_match.group(1).strip().lower()
            # Clean up the action
            for valid in ["left", "right", "up", "down"]:
                if valid in action:
                    return valid
        return "left"

