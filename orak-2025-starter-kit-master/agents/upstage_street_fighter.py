import openai
import re
import os

SYSTEM_PROMPT = """
You are an expert Street Fighter III player controlling Ken. Your goal is to defeat opponents.

### Game Rules ###
- Best-of-three rounds per stage
- Win by reducing opponent HP to 0 or having more HP when time runs out
- 10 stages total, score = stages cleared × 10

### Combat Mechanics ###
- Check distance: very close, close, or far
- Check health: yours vs opponent's (max 161)
- Super Bar: 0-100, use super when full
- Stun Bar: If opponent is stunned (=1), use powerful moves!

### Available Moves ###
- **Movement**: Move Closer, Move Away, Jump Closer, Jump Away
- **Punches**: Low Punch, Medium Punch, High Punch
- **Kicks**: Low Kick, Medium Kick, High Kick  
- **Combos**: Low Punch+Low Kick, Medium Punch+Medium Kick, High Punch+High Kick
- **Special Moves**:
  - Fireball (Hadouken): Ranged attack, good for far distance
  - Dragon Punch (Shoryuken): Anti-air, high damage
  - Hurricane: Spinning kick
  - Megapunch: Powerful punch
- **Super Moves** (need Super Count > 0):
  - Super Attack
  - Super Dragon Punch
  - Shippuu-Jinrai-Kyaku

### Strategy by Distance ###
**Very Close:**
- Use: High Kick, High Punch, Low Punch+Low Kick
- If opponent stunned: Dragon Punch or Super Attack

**Close:**
- Use: Medium Kick, Medium Punch, Fireball
- Mix attacks to keep pressure

**Far:**
- Use: Fireball to chip damage
- Move Closer to engage

### Output Format (Max 2 actions!) ###
### Reasoning
<analyze distance, health, super bar>
### Actions
- <action1>
- <action2>
"""

USER_PROMPT = """
### Current Game State
{cur_state_str}

### Available Skills
{skill_library}

### Previous State
{prev_state_str}

### Last Action
{last_action}

Choose up to 2 actions based on distance and game state.
### Reasoning
<your analysis>
### Actions
- <action1>
- <action2>
"""

class UpstageStreetFighterAgent:
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
        game_info = obs.get("game_info", {})
        skill_library = game_info.get("skill_library", "No skills available")

        try:
            response = self.client.chat.completions.create(
                model="solar-pro",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": USER_PROMPT.format(
                        cur_state_str=cur_state_str,
                        skill_library=skill_library,
                        prev_state_str=self.prev_state_str,
                        last_action=self.last_action
                    )}
                ],
                temperature=0.4,
                max_tokens=500
            )
            
            output = response.choices[0].message.content.strip()
            actions = self._parse_actions(output)
            
        except Exception as e:
            print(f"API Error: {e}")
            actions = "- Medium Kick"

        self.prev_state_str = cur_state_str
        self.last_action = actions

        return actions

    def _parse_actions(self, output):
        """Extract actions from ### Actions section"""
        actions_match = re.search(r"### Actions\s*\n(.+)", output, re.IGNORECASE | re.DOTALL)
        if actions_match:
            actions_section = actions_match.group(1).strip()
            # Clean up and return
            lines = []
            for line in actions_section.split('\n'):
                line = line.strip()
                if line.startswith('-'):
                    lines.append(line)
                elif line and not line.startswith('#'):
                    lines.append(f"- {line}")
                if len(lines) >= 2:
                    break
            
            if lines:
                return '\n'.join(lines)
        
        return "- Medium Kick"


