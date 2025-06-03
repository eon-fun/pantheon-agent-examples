# TikTokTestAgent

## Purpose & Scope
Automates TikTok comment posting through browser automation. Handles:
- Chrome browser installation (Linux)
- TikTok authentication
- Video commenting via Selenium
- Captcha solving using 2captcha service

## Prerequisites
- Linux OS (for automatic Chrome install)
- Python 3.10+
- `google-chrome-stable` package
- Active 2captcha API key
- Valid TikTok account credentials

### Required Permissions
- sudo access for package installation
- Internet access for TikTok and 2captcha

## Quickstart
1. **Install dependencies:**
```bash
pip install fastapi ray[serve] selenium
```

2. **Run the service:**
```bash
python twitter_ambassador_comment_answerer.py
```

3. **Trigger commenting:**
```bash
curl -X POST http://localhost:8000/comment
```

## Configuration
### Hardcoded Parameters (Update before deployment!)
```python
# TikTok credentials
username = "your_tiktok@email.com"
password = "your_password" 

# 2captcha API key 
api_key = "your_2captcha_key"

# Default test video
video_url = "https://www.tiktok.com/@test/video/123"
comment = "Test comment"
```

## Security Notice
- Credentials are currently hardcoded (unsafe for production)
- No input validation on video URLs
- Browser automation may trigger anti-bot systems