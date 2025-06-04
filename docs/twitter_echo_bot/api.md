# API & Configuration Reference

## REST Endpoints

#### `POST /{user_id}.{action}.{username}[.additional_params]`
Manages user profiles and tracking

#### Action Types:
| Action | Parameters | Description |
|--------|------------|-------------|
| `add_user` | username | Creates new user |
| `update_user` | username, persona, prompt | Updates preferences |
| `get_user` | - | Retrieves user data |
| `add_handles` | handle1,handle2,... | Adds tracked accounts |

#### Responses
Returns JSON with operation status and user data

## Configuration

### Environment Variables
| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection URL |
| `TWITTER_API_*` | Twitter API credentials |
| `CONTENT_INTERVAL` | Generation frequency (default: 5s) |

### Database Schema
Key tables:
- `users`: User profiles
- `tracked_accounts`: Twitter handles to monitor
- `generated_content`: Created tweets
