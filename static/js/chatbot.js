/**
 * Chatbot functionality for WE Hub
 * Supports both basic predefined responses and OpenAI-powered responses
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize chatbot elements
    const messageContainer = document.getElementById('chatbot-messages-embed');
    const messageInput = document.getElementById('chatbot-input-embed');
    const sendButton = document.getElementById('chatbot-send-embed');
    
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
                const isAI = data.is_ai || false;
                addBotMessage(data.response, isAI);
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
    function addBotMessage(message, isAI = false) {
        const messageElement = document.createElement('div');
        messageElement.className = 'chatbot-message bot-message';
        
        let aiIndicator = '';
        if (isAI) {
            aiIndicator = '<small class="text-info ai-indicator"><i class="fas fa-brain"></i> AI</small>';
        }
        
        messageElement.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-text">
                ${message}
                ${aiIndicator}
            </div>
        `;
        
        messageContainer.appendChild(messageElement);
        
        // Scroll to bottom
        messageContainer.scrollTop = messageContainer.scrollHeight;
    }
    
    // Function to show typing indicator
    function showTypingIndicator() {
        const indicatorElement = document.createElement('div');
        indicatorElement.className = 'chatbot-message bot-message typing-indicator';
        indicatorElement.id = 'typing-indicator-embed';
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
        const indicator = document.getElementById('typing-indicator-embed');
        if (indicator) {
            indicator.remove();
        }
    }
});
