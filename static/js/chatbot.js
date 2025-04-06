// AI-powered chatbot for Women Entrepreneurs Hub
document.addEventListener('DOMContentLoaded', () => {
  const chatToggle = document.getElementById('chat-toggle');
  const chatContainer = document.getElementById('chat-container');
  const chatMessages = document.getElementById('chat-messages');
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input');
  const chatClose = document.getElementById('chat-close');
  
  // Check if chat elements exist
  if (!chatToggle || !chatContainer || !chatMessages || !chatForm || !chatInput) {
    console.error('Chat elements not found');
    return;
  }
  
  // Toggle chat visibility
  chatToggle.addEventListener('click', () => {
    chatContainer.classList.toggle('d-none');
    
    // If opening the chat for the first time, show welcome message
    if (!chatContainer.classList.contains('d-none') && chatMessages.children.length === 0) {
      addBotMessage('Hello! 👋 I\'m your WE Hub assistant. How can I help you today?');
      
      // Add quick reply buttons for common questions
      const quickReplies = document.createElement('div');
      quickReplies.className = 'quick-replies mt-2';
      
      const commonQuestions = [
        'How do I create a business profile?',
        'How do I add products?',
        'How do I register for events?',
        'Tell me about payment options'
      ];
      
      commonQuestions.forEach(question => {
        const button = document.createElement('button');
        button.className = 'btn btn-sm btn-outline-primary me-1 mb-1';
        button.textContent = question;
        button.addEventListener('click', () => {
          addUserMessage(question);
          handleUserMessage(question);
        });
        quickReplies.appendChild(button);
      });
      
      chatMessages.appendChild(quickReplies);
    }
  });
  
  // Close chat
  chatClose.addEventListener('click', () => {
    chatContainer.classList.add('d-none');
  });
  
  // Handle chat form submission
  chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const message = chatInput.value.trim();
    if (!message) return;
    
    // Add user message to chat
    addUserMessage(message);
    
    // Clear input
    chatInput.value = '';
    
    // Handle user message
    handleUserMessage(message);
  });
  
  // Add a bot message to the chat
  function addBotMessage(message) {
    const messageEl = document.createElement('div');
    messageEl.className = 'message bot-message';
    messageEl.innerHTML = `
      <div class="message-avatar">
        <i class="fa fa-robot"></i>
      </div>
      <div class="message-content">
        ${message}
      </div>
    `;
    
    chatMessages.appendChild(messageEl);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
  
  // Add a user message to the chat
  function addUserMessage(message) {
    const messageEl = document.createElement('div');
    messageEl.className = 'message user-message';
    messageEl.innerHTML = `
      <div class="message-content">
        ${message}
      </div>
      <div class="message-avatar">
        <i class="fa fa-user"></i>
      </div>
    `;
    
    chatMessages.appendChild(messageEl);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
  
  // Handle user message and generate response
  function handleUserMessage(message) {
    // Show typing indicator
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'message bot-message typing-indicator';
    typingIndicator.innerHTML = `
      <div class="message-avatar">
        <i class="fa fa-robot"></i>
      </div>
      <div class="message-content">
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
      </div>
    `;
    
    chatMessages.appendChild(typingIndicator);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Process the message using our simple rule-based system
    // In a real implementation, this would be replaced with Dialogflow or another NLP service
    setTimeout(() => {
      // Remove typing indicator
      chatMessages.removeChild(typingIndicator);
      
      // Get response based on message content
      const response = generateResponse(message.toLowerCase());
      
      // Add bot response
      addBotMessage(response);
    }, 1000);
  }
  
  // Generate response based on user input
  function generateResponse(message) {
    // Simple keyword-based response generation
    // In a real implementation, this would use Dialogflow or another NLP service
    
    // Check for greetings
    if (message.match(/hello|hi|hey|greetings/i)) {
      return 'Hello! How can I assist you today?';
    }
    
    // Check for thanks
    if (message.match(/thank you|thanks|thx/i)) {
      return 'You\'re welcome! Is there anything else I can help you with?';
    }
    
    // Check for business profile questions
    if (message.match(/business profile|create profile|update profile|edit profile/i)) {
      return 'To create or update your business profile, go to your Dashboard and click on "Profile" in the sidebar. From there, you can add your business details, logo, and connect with Google My Business.';
    }
    
    // Check for product related questions
    if (message.match(/product|add product|sell product|listing/i)) {
      return 'To add products, go to the E-commerce section from your Dashboard and click "Add New Product". Fill in the details, add images, set your price, and publish. Your products will then be visible in your shop!';
    }
    
    // Check for payment related questions
    if (message.match(/payment|google pay|pay|transaction|pricing|fees/i)) {
      return 'We support Google Pay for secure transactions. The standard transaction fee is 2.9% + $0.30 per transaction. To set up payments, go to Settings > Payment Methods from your Dashboard.';
    }
    
    // Check for event related questions
    if (message.match(/event|workshop|register|signup|join event/i)) {
      return 'You can browse upcoming events in the Community section. To register for an event, simply click the "Register Now" button on the event page. You\'ll receive a confirmation email with event details.';
    }
    
    // Check for community related questions
    if (message.match(/community|forum|post|comment|discussion/i)) {
      return 'Our community forum is a great place to connect with other women entrepreneurs. You can start discussions, ask questions, and share your expertise. Head to the Community section to get started!';
    }
    
    // Check for marketing related questions
    if (message.match(/marketing|advertise|promote|ad campaign|google ads/i)) {
      return 'In the Marketing Tools section, you can create and manage Google Ad campaigns, track analytics, and optimize your SEO. We provide templates and guides to help you get started with your marketing efforts.';
    }
    
    // Check for analytics related questions
    if (message.match(/analytics|stats|metrics|data|performance|track/i)) {
      return 'Your business analytics are available in the Dashboard. You can view sales trends, customer demographics, and marketing performance. Data is updated in real-time to help you make informed decisions.';
    }
    
    // Check for mentorship related questions
    if (message.match(/mentor|mentorship|advice|guidance|coach/i)) {
      return 'We offer mentorship programs connecting you with experienced entrepreneurs. Check the "Mentorship" tab in the Community section to browse available mentors and request mentoring sessions.';
    }
    
    // Check for help or support
    if (message.match(/help|support|contact|assistance/i)) {
      return 'For additional support, you can email us at support@wehub.com or use the Help Center accessible from the footer of any page. Our support team is available Monday-Friday, 9 AM - 5 PM EST.';
    }
    
    // Default response for unrecognized queries
    return 'I\'m not sure I understand. Could you rephrase your question? You can ask me about creating a business profile, adding products, payments, events, or community features.';
  }
});
