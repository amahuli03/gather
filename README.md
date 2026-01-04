# Gather

An agentic AI assistant that helps you better schedule, coordinate, and connect with your friends. Gather integrates with Google Calendar to intelligently manage your schedule, check weather forecasts, find restaurants and places, and create calendar events—all through natural conversation.

## Quick Links

- [Installation for End Users](#installation-for-end-users) - Install Gather in your Google Calendar
- [Development Guide](DEVELOPMENT.md) - Setup and development instructions
- [Contributing](DEVELOPMENT.md#contributing) - How to contribute to Gather
- [Project Structure](#project-structure) - Codebase overview
- [Key Features](#key-features) - What Gather can do

## How It Works

Gather is a **Google Calendar add-on** powered by an AI agent that understands natural language and can coordinate multiple aspects of your schedule:

- **Calendar Management**: Check availability, find free times, create and update events
- **Weather Intelligence**: Check current weather and forecasts to suggest optimal times for activities
- **Location Services**: Find restaurants, places, and get location details using Google Places API
- **Smart Coordination**: Combines weather, calendar availability, and location data to make intelligent suggestions

### Architecture

Gather consists of three main components:

1. **Google Apps Script Add-On** (`addon/`)
   - Frontend interface embedded in Google Calendar
   - Card-based UI for chat interaction
   - Handles OAuth authentication and user session management
   - Communicates with the backend API

2. **FastAPI Backend** (`src/api/`)
   - REST API service that processes user requests
   - Hosts the LangChain ReAct agent with access to multiple tools
   - Manages conversation memory and context
   - Integrates with external APIs (OpenWeather, Google Places, Google Calendar)

3. **AI Agent** (`src/agent/`)
   - LangChain-based ReAct agent using GPT-4
   - Tool system for calendar, weather, maps, and custom integrations
   - Conversational memory for context-aware responses
   - Intelligent reasoning to coordinate multiple data sources

### Data Flow

```
User (Google Calendar) 
  → Apps Script Add-On 
  → FastAPI Backend (Cloud Run)
  → AI Agent (LangChain)
  → Tools (Calendar API, Weather API, Maps API)
  → Response back through the chain
```

## Installation for End Users

You can install Gather directly in your Google Calendar without any developer setup:

1. **Visit the installation link:**
   ```
   https://script.google.com/home/projects/1p4A95gLWtTW55-gPTK47f26NP1x7v58vfNlmPDRsnTbe1L4veHyHvuL_/edit
   ```

2. **Install the add-on:**
   - Click **"Deploy"** in the top menu
   - Click **"Test deployments"**
   - Find **"Version 3"** in the list
   - Click **"Install"** next to Version 3

3. **Authorize access:**
   - Grant the requested permissions when prompted
   - This allows Gather to access your Google Calendar

4. **Start using Gather:**
   - Open [Google Calendar](https://calendar.google.com)
   - Look for **"Gather Assistant"** in the right sidebar
   - Click on it to start chatting with your AI assistant!

That's it! No coding or developer setup required. Gather is now ready to help you coordinate your schedule, check weather, find places, and more.

## Development & Contributing

For setup instructions, development guide, and contribution guidelines, see the [Development Guide](DEVELOPMENT.md).

## Project Structure

```
gather-1/
├── addon/                 # Google Apps Script add-on code
│   ├── Code.gs           # Main add-on logic
│   ├── utils.gs          # Utility functions
│   └── appsscript.json   # Add-on manifest
├── src/
│   ├── agent/            # AI agent implementation
│   │   ├── coordinator.py    # Agent orchestration
│   │   ├── memory.py         # Conversation memory
│   │   └── tools/            # Agent tools (calendar, weather, maps)
│   ├── api/              # FastAPI backend
│   │   ├── main.py       # FastAPI app entry point
│   │   ├── routes/       # API endpoints
│   │   └── dependencies.py  # Dependency injection
│   ├── integrations/     # External API clients
│   │   ├── calendar_api.py
│   │   ├── weather_api.py
│   │   ├── maps_api.py
│   │   └── google_auth.py
│   └── ui.py             # Streamlit UI (for local testing)
├── Dockerfile            # Container configuration
├── cloudbuild.yaml       # Cloud Build configuration
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Key Features

- **Natural Language Interface**: Chat with the assistant using plain English
- **Calendar Integration**: Full Google Calendar read/write access
- **Weather-Aware Scheduling**: Suggests optimal times based on weather forecasts
- **Location Intelligence**: Finds restaurants and places near you
- **Conversation Memory**: Remembers context across messages
- **Multi-Tool Coordination**: Combines multiple data sources for intelligent suggestions

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions, please contact anisha.mahuli@gmail.com or open an issue on GitHub.