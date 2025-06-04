#!/bin/bash
# Minimal Example for TwitterAmbassadorCommentsAnswerer

# Input: TikTok video URL and comment text
VIDEO_URL="https://www.tiktok.com/@example_user/video/123456789"
COMMENT_TEXT="This is an automated comment"

# Make API request to the agent
curl -X POST "http://localhost:8000/comment" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "'"$VIDEO_URL"'",
    "comment_text": "'"$COMMENT_TEXT"'"
  }'

# Expected Output:
# {"success": true} on successful comment
# {"success": false, "error": "..."} on failure