# Random Agents (기본)
from agents.random_mario import RandomMarioAgent
from agents.random_pokemon import RandomPokemonAgent
from agents.random_twenty_fourty_eight import RandomTwentyFourtyEightAgent
from agents.random_starcraft import RandomStarCraftAgent
from agents.random_street_fighter import RandomStreetFighterAgent

# Upstage Solar Pro Agents (Track 2 - Open)
from agents.upstage_twenty_fourty_eight import UpstageTwentyFourtyEightAgent
from agents.upstage_mario import UpstageMarioAgent
from agents.upstage_pokemon import UpstagePokemonAgent
from agents.upstage_starcraft import UpstageStarCraftAgent
from agents.upstage_street_fighter import UpstageStreetFighterAgent

# ============================================
# 🎮 Active Agent Configuration
# ============================================
# 모든 게임에 Upstage Solar Pro 사용!

TwentyFourtyEightAgent = UpstageTwentyFourtyEightAgent  # ✅ Upstage (604점!)
SuperMarioAgent = UpstageMarioAgent                      # ✅ Upstage  
PokemonAgent = UpstagePokemonAgent                       # ✅ Upstage
StarCraftAgent = UpstageStarCraftAgent                   # ✅ Upstage
StreetFighterAgent = UpstageStreetFighterAgent           # ✅ Upstage

# ============================================
# 💡 Random 에이전트로 바꾸려면 아래 주석 해제
# ============================================
# TwentyFourtyEightAgent = RandomTwentyFourtyEightAgent
# SuperMarioAgent = RandomMarioAgent
# PokemonAgent = RandomPokemonAgent
# StarCraftAgent = RandomStarCraftAgent
# StreetFighterAgent = RandomStreetFighterAgent
