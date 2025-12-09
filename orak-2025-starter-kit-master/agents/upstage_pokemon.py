import openai
import re
import os

SYSTEM_PROMPT = """
You are an expert AI agent playing Pokemon Red. Your goal is to progress through the story.

### Game States ###
1. **Title State**: Press 'a' to continue, select 'CONTINUE' not 'NEW GAME'
2. **Field State**: Move around, interact with objects, open menu
3. **Dialog State**: Press 'a' or 'b' to advance dialog
4. **Battle State**: Select moves, switch Pokemon, use items, or run

### Controls ###
- Movement: up, down, left, right
- Confirm: a
- Cancel: b
- Menu: start

### Map System ###
- (0,0) is top-left
- X increases rightward, Y increases downward
- 'O' = walkable, 'X' = wall, 'G' = grass
- 'WarpPoint' = teleport location
- 'SPRITE' = NPC to talk to
- 'SIGN' = readable sign

### Available Tools ###
- move_to(x, y): Move to coordinates
- interact_with_object(name): Talk to NPC or read sign
- warp_with_warp_point(x, y): Use warp point
- continue_dialog(): Advance dialog
- select_move_in_battle(move_name): Use a move in battle
- switch_pkmn_in_battle(pokemon_name): Switch Pokemon
- run_away(): Flee from wild battle
- use_item_in_battle(item_name): Use item

### Story Milestones ###
1. Exit Red's House
2. Encounter Professor Oak
3. Choose a starter Pokemon
4. Finish first battle with Rival
5. Arrive in Viridian City
6. Receive Oak's parcel
7. Deliver Oak's parcel

### Strategy ###
- In Field: Explore, find WarpPoints, talk to NPCs
- In Dialog: Keep pressing continue_dialog()
- In Battle: Use strongest moves, or run from wild Pokemon
- Check map for '?' unexplored areas

### Output Format ###
### Reasoning
<analysis of current state>
### Actions
use_tool(<tool_name>, (<parameters>))
"""

USER_PROMPT = """
### Current Game State
{cur_state_str}

Analyze the state and choose the best action.
Output format:
### Reasoning
<your analysis>
### Actions
use_tool(<tool_name>, (<parameters>))
"""

class UpstagePokemonAgent:
    TRACK = "TRACK2"
    
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.environ.get("UPSTAGE_API_KEY", "up_UKdOB8JQt7dAF1XUGi5GmZ02mimkX"),
            base_url="https://api.upstage.ai/v1/solar"
        )
        self.last_state = None

    def act(self, obs):
        cur_state_str = obs.get("obs_str", "")

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
                max_tokens=500
            )
            
            output = response.choices[0].message.content.strip()
            action = self._parse_action(output, cur_state_str)
            
        except Exception as e:
            print(f"API Error: {e}")
            action = self._default_action(cur_state_str)

        self.last_state = cur_state_str
        return action

    def _parse_action(self, output, state_str):
        """Extract action from output"""
        # Look for use_tool pattern
        match = re.search(r"use_tool\(([^,]+),\s*\(([^)]*)\)\)", output, re.IGNORECASE)
        if match:
            tool_name = match.group(1).strip()
            params = match.group(2).strip()
            return f"use_tool({tool_name}, ({params}))"
        
        # Fallback: check state and provide default action
        return self._default_action(state_str)

    def _default_action(self, state_str):
        """Provide default action based on state"""
        state_lower = state_str.lower()
        
        if "state: dialog" in state_lower or "dialog" in state_lower:
            return "use_tool(continue_dialog, ())"
        elif "state: battle" in state_lower or "battle" in state_lower:
            # Try to find a move name
            move_match = re.search(r"moves?:.*?(\w+)", state_lower)
            if move_match:
                return f'use_tool(select_move_in_battle, (move_name="{move_match.group(1)}"))'
            return "use_tool(run_away, ())"
        elif "warppoint" in state_lower:
            # Find warp point coordinates
            warp_match = re.search(r"\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*warppoint", state_lower)
            if warp_match:
                return f"use_tool(warp_with_warp_point, (x={warp_match.group(1)}, y={warp_match.group(2)}))"
        
        # Default: press a to interact/continue
        return "a"


