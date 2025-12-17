/**
 * Utility functions for the Gather add-on
 */

/**
 * Gets user ID from current user's email
 * @return {string} User identifier
 */
function getUserId() {
  var email = Session.getActiveUser().getEmail();
  // Use email prefix as user_id, or return full email
  return email.split('@')[0];
}

/**
 * Stores conversation history in PropertiesService
 * Note: PropertiesService has size limits, so keep history concise
 * @param {string} userId - User identifier
 * @param {string} message - User message
 * @param {string} response - Agent response
 */
function saveConversationHistory(userId, message, response) {
  var properties = PropertiesService.getUserProperties();
  var key = 'conversation_' + userId;
  var history = properties.getProperty(key) || '[]';
  var messages = JSON.parse(history);
  
  // Add new messages
  messages.push({
    'role': 'user',
    'content': message,
    'timestamp': new Date().toISOString()
  });
  messages.push({
    'role': 'assistant',
    'content': response,
    'timestamp': new Date().toISOString()
  });
  
  // Keep only last 10 messages (to stay within size limits)
  if (messages.length > 10) {
    messages = messages.slice(-10);
  }
  
  properties.setProperty(key, JSON.stringify(messages));
}

/**
 * Gets conversation history for a user
 * @param {string} userId - User identifier
 * @return {Array} Array of message objects
 */
function getConversationHistory(userId) {
  var properties = PropertiesService.getUserProperties();
  var key = 'conversation_' + userId;
  var history = properties.getProperty(key) || '[]';
  return JSON.parse(history);
}

/**
 * Clears conversation history for a user
 * @param {string} userId - User identifier
 */
function clearConversationHistory(userId) {
  var properties = PropertiesService.getUserProperties();
  var key = 'conversation_' + userId;
  properties.deleteProperty(key);
}

