#!/bin/bash
# PersonaAgent - Basic Interaction Examples

# 1. Generate tweet in Elon Musk's persona style
curl -X POST "http://localhost:8000/elon_musk" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a tweet about the future of AI and Mars colonization"}'

# Expected successful response:
# {
#   "success": true,
#   "result": "The future of AI is inevitable, just like our destiny on Mars. Neuralinks will connect human consciousness across planets while Starships carry our physical forms. The age of multiplanetary civilization is coming faster than most think. #AI #Mars"
# }

# 2. Generate tweet in professional CEO persona style
curl -X POST "http://localhost:8000/ceo_tech" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Announce our new quantum computing initiative"}'

# Expected successful response:
# {
#   "success": true,
#   "result": "Thrilled to announce our $50M quantum computing initiative. This breakthrough technology will redefine encryption, drug discovery, and climate modeling. Proud of our team pushing boundaries. The future is quantum. #Innovation #TechLeadership"
# }

# 3. Attempt with non-existent persona
curl -X POST "http://localhost:8000/unknown_persona" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Any prompt"}'

# Expected error response:
# {
#   "success": false,
#   "result": "No persona collection found"
# }

# 4. Generate with additional generation plan
curl -X POST "http://localhost:8000/news_anchor" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Report on the latest blockchain regulation news",
    "plan": {
      "tone": "professional",
      "length": "medium",
      "key_points": ["EU MiCA", "US proposals", "market impact"]
    }
  }'

# Example successful response:
# {
#   "success": true,
#   "result": "Breaking: EU's MiCA regulations set new global standard for crypto oversight while US lawmakers debate their approach. Markets show cautious optimism as clarity emerges. Experts suggest this balanced regulation could attract institutional investment. More details at 9. #CryptoNews #Regulation"
# }