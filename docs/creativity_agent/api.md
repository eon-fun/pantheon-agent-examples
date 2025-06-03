# API & Configuration Reference

## Core Endpoints

### Lipsync v1
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/lipsyncs/` | POST | Create lipsync task |
| `/lipsyncs/preview/` | POST | Generate preview |
| `/lipsyncs/{id}/render/` | POST | Start rendering |
| `/lipsyncs/{id}/` | GET | Get task status |

### Lipsync v2
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/lipsyncs_v2/` | POST | Create task |
| `/lipsyncs_v2/preview/` | POST | Generate preview |
| `/lipsyncs_v2/{id}/render/` | POST | Start rendering |
| `/lipsyncs_v2/{id}/` | GET | Get task status |

### AI Shorts
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ai_shorts/` | POST | Create short |
| `/ai_shorts/preview/` | POST | Generate preview |
| `/ai_shorts/{id}/render/` | POST | Start rendering |
| `/ai_shorts/{id}/` | GET | Get task status |

## Configuration

### Environment Variables
| Variable | Description |
|----------|-------------|
| `CREATIVITY_BASE_URL` | API base URL |
| `CREATIVITY_API_ID` | Authentication ID |
| `CREATIVITY_API_KEY` | Authentication key |
| `LOG_LEVEL` | Log verbosity |

### Request Models
All endpoints use strongly-typed Pydantic models for:
- Input validation
- Documentation
- Auto-completion
