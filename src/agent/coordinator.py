from typing import List, Optional, Tuple
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from src.agent.tools.weather import create_weather_tool, create_forecast_tool
from src.agent.tools.calendar import (
    create_calendar_tool,
    create_get_events_tool,
    create_find_free_times_tool,
    create_create_event_tool,
    create_update_event_location_tool,
    create_parse_date_tool
)
from src.agent.tools.n8n_client import create_n8n_tool
from src.agent.tools.maps import create_search_places_tool, create_get_place_details_tool
from src.agent.types import ToolContext

def build_agent(ctx: ToolContext, memory: Optional[ConversationBufferWindowMemory] = None):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    # Create tools with context bound via closures
    tools = [
        create_parse_date_tool(ctx),  # Add date parsing tool first
        create_weather_tool(ctx),
        create_forecast_tool(ctx),
        create_calendar_tool(ctx),
        create_get_events_tool(ctx),
        create_find_free_times_tool(ctx),
        create_create_event_tool(ctx),
        create_update_event_location_tool(ctx),
        create_search_places_tool(ctx),
        create_get_place_details_tool(ctx),
        create_n8n_tool(ctx),
    ]
    
    # Get user_id from calendar client
    user_id = ctx.calendar_client.user_id if ctx.calendar_client else "me"
    
    # Build chat history string from memory if available
    chat_history_str = ""
    if memory:
        # Get chat history from memory
        messages = memory.chat_memory.messages
        if messages:
            chat_history_str = "\n\nPrevious conversation:\n"
            for msg in messages[-10:]:  # Show last 10 messages for context
                if hasattr(msg, 'content'):
                    role = "User" if msg.__class__.__name__ == "HumanMessage" else "Assistant"
                    chat_history_str += f"{role}: {msg.content}\n"
    
    # Create a ReAct prompt template with improved instructions
    prompt = PromptTemplate.from_template("""
You are a helpful assistant that can coordinate schedules and activities.

IMPORTANT: The current user ID is "{user_id}". Always use this user_id when calling calendar tools.
{chat_history}

You have access to the following tools:
{tools}

IMPORTANT INSTRUCTIONS:
- DISTINGUISH between two types of requests:
  1. WEATHER-ONLY: User asks about weather but does NOT ask to schedule (e.g., "what's the weather", "warmest day", "best weather")
     * Call get_weather_forecast ONCE
     * Analyze the data and provide Final Answer immediately
     * DO NOT take scheduling actions
  
  2. WEATHER + SCHEDULING: User asks about weather AND wants to schedule (e.g., "find best time and schedule", "put it in my calendar", "schedule a hike")
     * First, call get_weather_forecast ONCE to get weather data
     * Use that data to determine the best day/time
     * Then take ALL scheduling actions needed (check_availability, find_available_times, create_calendar_event)
     * ONLY AFTER completing all scheduling actions, provide Final Answer
     * DO NOT provide Final Answer until you have actually scheduled the event
- For "this weekend" weather-only questions: 
  * Call get_weather_forecast ONCE (with location and days=5 or days=7)
  * The forecast will include Saturday and Sunday - compare them in your Final Answer
  * Provide Final Answer immediately after getting the forecast
- Break down complex requests into steps. For example, "warmest day this week" requires: 1) Get forecast for the week ONCE, 2) Compare temperatures in the data you received, 3) Identify the warmest day, 4) Provide Final Answer
- Always use the appropriate tool - use get_weather_forecast for multi-day comparisons, use check_weather for current conditions.
- For Maps/Places API usage:
  * Use search_places when the user asks for suggestions or wants to find places (e.g., "find restaurants", "suggest places to go")
  * Do NOT use search_places if the user provides a specific location/address - they already know where they want to go
  * When suggesting places, always provide address, phone number, and website if available
  * Remember the location context from previous messages (e.g., if user mentioned "Wilmington, DE" earlier, use that in searches)
  * If user asks for a specific type after initial suggestions (e.g., "I'm looking for Mexican food"), search for that type in the remembered location
  * When a user picks a restaurant/place from your suggestions, use update_event_location to add that location to the relevant calendar event
- CRITICAL: After calling ANY tool and receiving data, you MUST analyze that data and provide a Final Answer. DO NOT call the same tool again with the same parameters.
- For scheduling/calendar requests:
  - If user explicitly asks to "put it on my calendar", "schedule it", "add it to my calendar", "create an event", etc.:
    * This IS user confirmation - proceed to create the event
    * If no specific time is given, use find_available_times to find a good slot, then create_calendar_event
    * Pick a reasonable time if multiple options are available (e.g., first available slot, or a time like 2pm if available)
    * Create the event directly - don't ask for confirmation again
  - If user specifies EXACT times (e.g., "dinner at 6 PM", "meeting from 2-3 PM"):
    * Parse the date/time
    * If they asked to "put it on my calendar" or similar, create the event immediately
    * Otherwise, suggest the event and ask for confirmation
  - If user just asks "when am I free?" or "what times are available?" WITHOUT asking to schedule:
    * Use find_available_times to show options
    * DO NOT create an event - just show the available times
- CRITICAL ANTI-LOOPING RULES:
  * NEVER call the same tool twice with the same parameters - if you already have the data, use it
  * If you see the same Observation result twice, you are looping - STOP and provide Final Answer immediately
  * After providing a Final Answer, DO NOT take additional Actions - the Final Answer ends the conversation
  * If you write "Final Answer:" in your output, that MUST be the absolute last thing - no more Thoughts or Actions after that
  * If the user asked you to schedule something, complete ALL scheduling steps BEFORE providing Final Answer
- CRITICAL: Provide Final Answer ONLY after:
  * For weather-only questions: After getting weather data
  * For scheduling questions: After completing ALL scheduling actions (checking availability, creating event, etc.)
- CRITICAL FORMAT: When providing Final Answer, your output MUST be:
  Thought: I now know the final answer
  Final Answer: [your answer here]
  DO NOT write ANYTHING after the Final Answer line - no Thoughts, no Actions, nothing

OUTPUT FORMAT RULES (STRICTLY FOLLOW):
1. After each tool use, you MUST include "Thought:" before your next action
2. When ready to answer, you MUST format exactly as:
   Thought: I now know the final answer
   Final Answer: [your answer here]
3. Do not write explanations or answers without the "Final Answer:" prefix
4. If you write any response to the user, it MUST come after "Final Answer:"

Use the following format (follow this EXACTLY):

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}
""")
    
    # Format prompt with user_id and chat history
    formatted_prompt = prompt.partial(user_id=user_id, chat_history=chat_history_str)
    agent = create_react_agent(llm, tools, formatted_prompt)

    # Custom error handler to provide better guidance
    def handle_parsing_error(error) -> str:
        """Custom error handler that reminds the agent of the correct format."""
        return (
            "PARSING ERROR. You must follow this EXACT format:\n"
            "Thought: I now know the final answer\n"
            "Final Answer: [your complete answer to the user]\n\n"
            "Do NOT write any text without the proper prefix (Thought:, Action:, Action Input:, or Final Answer:).\n"
            "If you provided a Final Answer, DO NOT write any Actions after it - the Final Answer ends the conversation.\n"
            "If you need to take actions, do them BEFORE providing the Final Answer."
        )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,  # Enable verbose to debug - check terminal/console for output
        handle_parsing_errors=handle_parsing_error,
        max_iterations=8,  # Allow enough iterations for multi-step requests (weather + scheduling)
        max_execution_time=60  # 60 second timeout for complex requests
    )
    return agent_executor

def run_task(ctx: ToolContext, user_prompt: str, memory: Optional[ConversationBufferWindowMemory] = None) -> tuple[str, list]:
    """
    Run agent task with memory.
    
    Returns:
        tuple: (output_string, tool_calls_list)
    """
    # Add user message to memory before building agent (so it's in context)
    if memory:
        memory.chat_memory.add_user_message(user_prompt)
    
    agent = build_agent(ctx, memory=memory)
    tool_calls = []
    
    try:
        result = agent.invoke({"input": user_prompt})
        output = result.get("output", str(result))
        
        # Extract tool calls from intermediate steps if available
        if isinstance(result, dict):
            # Try to get intermediate_steps
            intermediate_steps = result.get("intermediate_steps", [])
            for step in intermediate_steps:
                try:
                    if len(step) >= 2:
                        # step[0] is usually an AgentAction, step[1] is the observation
                        action = step[0]
                        observation = step[1]
                        
                        tool_name = getattr(action, 'tool', str(action))
                        tool_input = getattr(action, 'tool_input', {})
                        tool_output = str(observation)[:500] if len(str(observation)) > 500 else str(observation)  # Truncate long outputs
                        
                        tool_calls.append({
                            "tool": str(tool_name),
                            "input": str(tool_input),
                            "output": tool_output,
                            "timestamp": datetime.now().isoformat()
                        })
                except Exception as e:
                    # If extraction fails, skip this tool call
                    continue
        
        # Add assistant response to memory
        if memory:
            memory.chat_memory.add_ai_message(output)
        
        return output, tool_calls
    except Exception as e:
        # Handle timeout or other errors gracefully
        error_msg = str(e)
        if "timeout" in error_msg.lower() or "max_execution_time" in error_msg.lower():
            return ("I apologize, but the request took too long to process. This might be due to calendar API delays or complex scheduling. Please try again with a simpler request, or check your calendar connection.", [])
        elif "max_iterations" in error_msg.lower() or "iteration limit" in error_msg.lower():
            return ("I apologize, but I reached the maximum number of steps while processing your request. Please try rephrasing your request more simply, or break it into smaller parts.", [])
        else:
            return (f"I encountered an error while processing your request: {error_msg}. Please try again or rephrase your request.", [])