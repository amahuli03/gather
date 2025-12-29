/**
 * Gather Calendar Add-On
 * Main entry point and chat interface
 */

// TODO: Update this with your deployed API URL
// For local testing, use ngrok or similar to expose localhost
// Example: const API_BASE_URL = 'https://your-api.herokuapp.com';
const API_BASE_URL = 'http://localhost:8000';  // Change to your production API URL

/**
 * Called when the add-on is opened in Calendar homepage
 * Creates the main chat interface card
 */
function onHomepage(e) {
  return createChatCard();
}

/**
 * Creates the main chat interface card
 * Shows conversation history and input field
 */
function createChatCard() {
  var userId = getUserId();
  var history = getConversationHistory(userId);
  
  var card = CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader()
      .setTitle('🤝 Gather Assistant')
      .setSubtitle('Your coordination assistant'));
  
  // Add conversation history if exists
  if (history.length > 0) {
    card.addSection(createHistorySection(history));
  } else {
    card.addSection(createWelcomeSection());
  }
  
  card.addSection(createInputSection());
  
  return card.build();
}

/**
 * Creates welcome section with instructions
 */
function createWelcomeSection() {
  return CardService.newCardSection()
    .addWidget(CardService.newTextParagraph()
      .setText('Ask me to coordinate schedules, check weather, find places, and more!'))
    .addWidget(CardService.newDivider());
}

/**
 * Creates input section for user messages
 */
function createInputSection() {
  var section = CardService.newCardSection()
    .setHeader('Send a message')
    .addWidget(CardService.newTextInput()
      .setFieldName('user_message')
      .setTitle('Your message')
      .setHint('e.g., "What\'s the weather in Wilmington, DE?"'))
    .addWidget(CardService.newTextButton()
      .setText('Send')
      .setOnClickAction(CardService.newAction()
        .setFunctionName('handleSendMessage')));
  
  // Add clear history button if there's history
  var userId = getUserId();
  var history = getConversationHistory(userId);
  if (history.length > 0) {
    section.addWidget(CardService.newTextButton()
      .setText('Clear History')
      .setOnClickAction(CardService.newAction()
        .setFunctionName('handleClearHistory'))
      .setTextButtonStyle(CardService.TextButtonStyle.TEXT));
  }
  
  return section;
}

/**
 * Handles when user clicks "Send" button
 * Calls the backend API and displays response
 */
function handleSendMessage(e) {
  var userMessage = e.formInput.user_message;
  
  if (!userMessage || userMessage.trim() === '') {
    return createErrorCard('Please enter a message');
  }
  
  var userId = getUserId();
  
  // Show loading state
  var loadingCard = CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader()
      .setTitle('🤝 Gather Assistant'))
    .addSection(createMessageSection('👤 You', userMessage))
    .addSection(CardService.newCardSection()
      .addWidget(CardService.newTextParagraph()
        .setText('🤖 Gather: <i>Processing...</i>')))
    .build();
  
  // Call backend API
  try {
    var response = callBackendAPI(userMessage, userId);
    
    // Save to conversation history
    saveConversationHistory(userId, userMessage, response.response);
    
    // Create response card with full history
    return createResponseCard(userMessage, response);
  } catch (error) {
    Logger.log('Error: ' + error.toString());
    return createErrorCard('Error connecting to API. Make sure your API is running and API_BASE_URL is correct.');
  }
}

/**
 * Calls the backend FastAPI service
 * @param {string} message - User's message
 * @param {string} userId - User identifier
 * @return {object} API response
 */
function callBackendAPI(message, userId) {
  var url = API_BASE_URL + '/api/chat';
  
  // Get OAuth token from Apps Script (this gives us access to Calendar API)
  var oauthToken = ScriptApp.getOAuthToken();
  
  var payload = {
    'message': message,
    'user_id': userId,
    'oauth_token': oauthToken  // Pass the OAuth token to the API
  };
  
  var options = {
    'method': 'post',
    'contentType': 'application/json',
    'payload': JSON.stringify(payload),
    'muteHttpExceptions': true
  };
  
  var response = UrlFetchApp.fetch(url, options);
  var responseCode = response.getResponseCode();
  var responseText = response.getContentText();
  
  if (responseCode !== 200) {
    throw new Error('API returned status ' + responseCode + ': ' + responseText);
  }
  
  return JSON.parse(responseText);
}

/**
 * Creates a card showing the conversation (user message + agent response)
 */
function createResponseCard(userMessage, apiResponse) {
  var userId = getUserId();
  var history = getConversationHistory(userId);
  
  var card = CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader()
      .setTitle('🤝 Gather Assistant'));
  
  // Show conversation history
  if (history.length > 0) {
    card.addSection(createHistorySection(history));
  } else {
    // If no history yet, show current exchange
    card.addSection(createMessageSection('👤 You', userMessage))
        .addSection(createMessageSection('🤖 Gather', apiResponse.response));
  }
  
  card.addSection(createInputSection());
  
  return card.build();
}

/**
 * Creates a section showing conversation history
 */
function createHistorySection(history) {
  var section = CardService.newCardSection()
    .setHeader('Conversation');
  
  // Add last few messages from history
  var recentMessages = history.slice(-6); // Show last 3 exchanges (6 messages)
  
  for (var i = 0; i < recentMessages.length; i++) {
    var msg = recentMessages[i];
    var role = msg.role === 'user' ? '👤 You' : '🤖 Gather';
    section.addWidget(CardService.newTextParagraph()
      .setText('<b>' + role + ':</b><br/>' + msg.content));
  }
  
  return section;
}

/**
 * Creates a section for a single message
 */
function createMessageSection(role, content) {
  return CardService.newCardSection()
    .addWidget(CardService.newTextParagraph()
      .setText('<b>' + role + ':</b><br/>' + content));
}

/**
 * Creates an error card
 */
function createErrorCard(errorMessage) {
  var userId = getUserId();
  var history = getConversationHistory(userId);
  
  var card = CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader()
      .setTitle('⚠️ Error'));
  
  // Show history if exists
  if (history.length > 0) {
    card.addSection(createHistorySection(history));
  }
  
  card.addSection(CardService.newCardSection()
      .addWidget(CardService.newTextParagraph()
        .setText('<font color="#d32f2f">' + errorMessage + '</font>')))
    .addSection(createInputSection());
  
  return card.build();
}

/**
 * Clears conversation history (can be called from a button)
 */
function handleClearHistory() {
  var userId = getUserId();
  clearConversationHistory(userId);
  return createChatCard();
}

/**
 * Optional: Called when a calendar event is opened
 * Can provide event-specific actions
 */
function onEventOpen(e) {
  // Future: Add event-specific actions here
  // For now, just show the chat interface
  return createChatCard();
}

