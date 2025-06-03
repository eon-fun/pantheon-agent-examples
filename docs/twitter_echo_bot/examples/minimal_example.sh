#!/bin/bash
# FollowUnfollowBot - Usage Examples

# 1. Add new user
curl -X POST "http://localhost:8000/12345.add_user.johndoe"

# 2. Update user persona
curl -X POST "http://localhost:8000/12345.update_user.johndoe.professional.tech_enthusiast"

# 3. Add tracked accounts
curl -X POST "http://localhost:8000/12345.add_handles.johndoe.twitteruser1,twitteruser2"

# 4. Get user data
curl -X POST "http://localhost:8000/12345.get_user.johndoe"

# Example responses:
# {"status":"success","user":{"id":12345,"username":"johndoe"...}}
