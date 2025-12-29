# Gather Calendar Add-On - Apps Script

This directory contains the Google Apps Script code for the Gather Calendar add-on.

## Setup Instructions

### 1. Create Apps Script Project

1. Go to [script.google.com](https://script.google.com)
2. Click "New Project"
3. Name it "Gather Calendar Add-On"

### 2. Copy Files to Apps Script

**Option A: Manual Copy (Easiest)**
1. Copy contents of `Code.gs` into the Apps Script editor
2. Copy contents of `utils.gs` into a new file in Apps Script (File → New → Script)
3. Click "Project Settings" (gear icon)
4. Enable "Show 'appsscript.json' manifest file"
5. Copy contents of `appsscript.json` into the manifest file

**Option B: Using clasp (CLI)**
```bash
# Install clasp
npm install -g @google/clasp

# Login to Google
clasp login

# Create new Apps Script project
clasp create --type standalone --title "Gather Calendar Add-On"

# Push files
clasp push
```

### 3. Configure API URL

1. Open `Code.gs` in Apps Script editor
2. Update `API_BASE_URL` constant:
   ```javascript
   const API_BASE_URL = 'https://your-api.example.com';  // Your deployed API URL
   ```
3. For local testing, use ngrok:
   ```bash
   ngrok http 8000
   # Then use the ngrok URL
   ```

### 4. Test Deployment

1. In Apps Script, click "Deploy" → "Test deployments"
2. Click "Install" next to your test deployment
3. Open Google Calendar
4. You should see "Gather Assistant" in the sidebar
5. Test sending a message

### 5. Deploy

1. In Apps Script, click "Deploy" → "New deployment"
2. Choose type: "Add-on"
3. Set description
4. Click "Deploy"
5. Install in Calendar

## File Structure

- `Code.gs` - Main Apps Script code with chat interface
- `utils.gs` - Utility functions (user ID, conversation history)
- `appsscript.json` - Add-on manifest and configuration
- `README.md` - This file

## Key Functions

**Code.gs:**
- `onHomepage()` - Creates the main chat interface when add-on opens
- `handleSendMessage()` - Processes user input and calls API
- `callBackendAPI()` - Makes HTTP request to your FastAPI backend
- `createResponseCard()` - Displays conversation (user + agent messages)
- `handleClearHistory()` - Clears conversation history

**utils.gs:**
- `getUserId()` - Gets user identifier from email
- `saveConversationHistory()` - Saves messages to PropertiesService
- `getConversationHistory()` - Retrieves conversation history
- `clearConversationHistory()` - Clears conversation history

## API Integration

The add-on calls your FastAPI backend at:
- `POST /api/chat` - Sends user message, gets agent response

Request format:
```json
{
  "message": "What's the weather?",
  "user_id": "user@example.com"
}
```

Response format:
```json
{
  "response": "Agent response text",
  "tool_calls": [],
  "user_id": "user@example.com"
}
```

## Development Tips

1. **Local Testing**: Use ngrok to expose your local API (`ngrok http 8000`)
2. **Debugging**: Use `Logger.log()` in Apps Script, view in Executions
3. **Error Handling**: Check API response codes and handle errors gracefully
4. **User ID**: Currently uses email prefix, can be customized

## Features Implemented

- ✅ Chat interface with card-based UI
- ✅ Conversation history (stored in PropertiesService)
- ✅ Clear history button
- ✅ Error handling
- ✅ API integration with FastAPI backend

## Next Steps

- [ ] Update `API_BASE_URL` with production API URL
- [ ] Test chat functionality end-to-end
- [ ] Add buttons for quick actions (create event, etc.)
- [ ] Handle restaurant/event suggestions with interactive buttons
- [ ] Add loading states (currently shows "Processing..." but doesn't persist)

