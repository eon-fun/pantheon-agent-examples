# Architecture & Flow

## Overview
The TwitterAmbassadorCommentsAnswerer is a FastAPI service built on Ray Serve that automates TikTok interactions through browser automation. It follows a single-operation flow focused on commenting functionality.

## Component Diagram
See [`architecture.puml`](./architecture.puml) for visual representation.

## Core Components
1. **FastAPI Layer**:
   - Provides HTTP interface
   - Handles request routing
   - Manages lifespan

2. **Ray Serve Deployment**:
   - Wraps the agent logic
   - Handles scaling
   - Manages requests queue

3. **TikTokBot Worker**:
   - Browser automation (Selenium)
   - Credential management
   - Comment posting logic
   - Captcha solving integration

4. **System Dependencies**:
   - Chrome browser
   - 2captcha service
   - TikTok platform

## Execution Flow
1. **Initialization**:
   - Chrome installation check
   - WebDriver setup
   - Service dependencies verification

2. **Operation Phase**:
   ```plaintext
   API Request → Authentication → Video Navigation → Comment Posting → Cleanup
   ```

3. **Shutdown**:
   - Browser session termination
   - Resource cleanup
   - Error state handling

## Failure Modes
1. **Browser-Level**:
   - Chrome installation failures
   - Driver compatibility issues

2. **Platform-Level**:
   - TikTok authentication failures
   - Captcha solving timeouts

3. **Operation-Level**:
   - Element not found errors
   - Rate limiting detection
   - Network interruptions
