document.addEventListener('DOMContentLoaded', function() {
  const chatbotToggle = document.getElementById('chatbot-toggle');
  const chatbotWindow = document.getElementById('chatbot-window');
  const messageContainer = document.getElementById('chatbot-messages');
  const messageInput = document.getElementById('chatbot-input');
  const sendButton = document.getElementById('chatbot-send');
  
  // Add welcome message
  addBotMessage("Hello! I'm your WE Hub assistant. How can I help you today?");
  addBotMessage("You can ask me about setting up your business profile, managing products, using our community features, or any other questions about the platform.");
  
  // Toggle chatbot window
  if (chatbotToggle) {
    chatbotToggle.addEventListener('click', function() {
      if (chatbotWindow.classList.contains('d-none')) {
        chatbotWindow.classList.remove('d-none');
        messageInput.focus();
      } else {
        chatbotWindow.classList.add('d-none');
      }
    });
  }
  
  // Close chatbot window
  const closeButton = document.getElementById('chatbot-close');
  if (closeButton) {
    closeButton.addEventListener('click', function() {
      chatbotWindow.classList.add('d-none');
    });
  }
  
  // Send message on button click
  if (sendButton) {
    sendButton.addEventListener('click', sendMessage);
  }
  
  // Send message on Enter key
  if (messageInput) {
    messageInput.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        sendMessage();
      }
    });
  }
  
  // Function to send message
  function sendMessage() {
    const message = messageInput.value.trim();
    
    if (!message) {
      return;
    }
    
    // Add user message to chat
    addUserMessage(message);
    
    // Clear input
    messageInput.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    // Send message to backend
    fetch('/chatbot/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message })
    })
    .then(response => response.json())
    .then(data => {
      // Hide typing indicator
      hideTypingIndicator();
      
      if (data.success) {
        // Add bot response to chat
        addBotMessage(data.response);
      } else {
        addBotMessage("Sorry, I'm having trouble understanding that right now. Please try again later.");
      }
    })
    .catch(error => {
      console.error('Error sending message:', error);
      
      // Hide typing indicator
      hideTypingIndicator();
      
      // Add error message
      addBotMessage("Sorry, there was an error processing your request. Please try again later.");
    });
  }
  
  // Function to add user message to chat
  function addUserMessage(message) {
    const messageElement = document.createElement('div');
    messageElement.className = 'chatbot-message user-message';
    messageElement.innerHTML = `<div class="message-text">${message}</div>`;
    
    messageContainer.appendChild(messageElement);
    
    // Scroll to bottom
    messageContainer.scrollTop = messageContainer.scrollHeight;
  }
  
  // Function to add bot message to chat
  function addBotMessage(message) {
    const messageElement = document.createElement('div');
    messageElement.className = 'chatbot-message bot-message';
    messageElement.innerHTML = `
      <div class="message-avatar">
        <i class="fas fa-robot"></i>
      </div>
      <div class="message-text">${message}</div>
    `;
    
    messageContainer.appendChild(messageElement);
    
    // Scroll to bottom
    messageContainer.scrollTop = messageContainer.scrollHeight;
  }
  
  // Function to show typing indicator
  function showTypingIndicator() {
    const indicatorElement = document.createElement('div');
    indicatorElement.className = 'chatbot-message bot-message typing-indicator';
    indicatorElement.id = 'typing-indicator';
    indicatorElement.innerHTML = `
      <div class="message-avatar">
        <i class="fas fa-robot"></i>
      </div>
      <div class="message-text">
        <div class="typing-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    `;
    
    messageContainer.appendChild(indicatorElement);
    
    // Scroll to bottom
    messageContainer.scrollTop = messageContainer.scrollHeight;
  }
  
  // Function to hide typing indicator
  function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
      indicator.remove();
    }
  }
});
