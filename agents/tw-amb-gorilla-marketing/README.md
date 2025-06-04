# Twitter Gorilla Marketing Agent

## Overview
The Twitter Gorilla Marketing Agent is an automated system designed to find and engage with relevant conversations on Twitter based on specified keywords and themes. This agent searches for popular tweets matching your criteria and engages with them through comments, implementing a guerrilla marketing strategy to increase visibility for your brand or project.

## Features
- Searches Twitter for popular tweets based on keywords and hashtags
- Filters tweets based on relevance and engagement metrics
- Generates contextual comments that subtly promote your brand/product
- Tracks interaction history to avoid duplicate engagements
- Implements rate limiting to comply with Twitter API restrictions

## Architecture
The agent is built using:
- **FastAPI**: For API endpoints and request handling
- **Ray Serve**: For deployment and scaling
- **Redis**: For persistent storage and rate limit management
- **Twitter API**: For tweet searching and comment posting

## Usage
To use the agent, send a POST request to the `/{goal}` endpoint where `goal` is formatted as:

```
{your_username}.{[keywords]}.{[themes]}
```

- `your_username`: Your Twitter account that will be posting comments
- `keywords`: Keywords related to your product/brand (comma-separated)
- `themes`: Broader themes or hashtags to target (comma-separated)

For example: `mybrand.[productname,newrelease].[tech,innovation,startup]`

## Workflow
1. Searches Twitter for popular tweets (min 5 likes) containing your keywords or hashtags
2. Filters out tweets that have already been engaged with
3. Checks tweets for relevance to your specified keywords and themes
4. Sorts remaining tweets by popularity (like count)
5. Generates contextually relevant comments for the top 2 tweets
6. Posts comments to Twitter after ensuring appropriate delay
7. Records the interactions in Redis for future reference


## Best Practices
- Use specific, targeted keywords related to your product
- Include broad themes to widen your reach while maintaining relevance
- Monitor engagement to refine your approach
- Ensure your comments add value to conversations rather than appearing as spam
