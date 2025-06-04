#!/bin/bash
# FollowUnfollowBot - Usage Examples

# 1. Add new user to tracking system
curl -X POST "http://localhost:8000/123456789.add"

# Expected response:
# {
#   "status": "success",
#   "action": "added",
#   "user_id": 123456789
# }

# 2. Remove user from system
curl -X POST "http://localhost:8000/987654321.delete"

# 3. Check system status (custom endpoint example)
curl "http://localhost:8000/status"

# 4. Force daily reset (admin endpoint example)
curl -X POST "http://localhost:8000/admin/reset_all"
