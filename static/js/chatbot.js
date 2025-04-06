/**
 * Women Entrepreneurs Hub Chatbot
 * Handles the interaction between the user and the chatbot
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize chatbot elements
    const chatToggle = document.getElementById('chat-toggle');
    const chatContainer = document.getElementById('chat-container');
    const chatClose = document.getElementById('chat-close');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');

    // Check if elements exist
    if (!chatToggle || !chatContainer || !chatClose || !chatForm || !chatInput || !chatMessages) {
        console.error('Chatbot elements not found');
        return;
    }

    // Toggle chatbot visibility
    chatToggle.addEventListener('click', function() {
        chatContainer.classList.toggle('d-none');
        
        // If this is the first time opening the chat, add a welcome message
        if (chatMessages.children.length === 0) {
            addMessage('assistant', 'Hello! I\'m WE Hub Assistant. How can I help you today?');
        }
        
        // Focus on input
        chatInput.focus();
    });

    // Close chatbot
    chatClose.addEventListener('click', function() {
        chatContainer.classList.add('d-none');
    });

    // Submit message
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const message = chatInput.value.trim();
        if (!message) return;
        
        // Add user message
        addMessage('user', message);
        
        // Clear input
        chatInput.value = '';
        
        // Get response from bot
        getChatbotResponse(message);
    });

    // Function to add a message to the chat
    function addMessage(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message', sender);
        
        const avatar = document.createElement('div');
        avatar.classList.add('chat-avatar');
        
        if (sender === 'assistant') {
            avatar.innerHTML = '<i class="fas fa-robot"></i>';
        } else {
            avatar.innerHTML = '<i class="fas fa-user"></i>';
        }
        
        const content = document.createElement('div');
        content.classList.add('chat-content');
        content.innerText = message;
        
        messageElement.appendChild(avatar);
        messageElement.appendChild(content);
        
        chatMessages.appendChild(messageElement);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to get a response from the chatbot
    function getChatbotResponse(message) {
        // Show typing indicator
        const typingIndicator = document.createElement('div');
        typingIndicator.classList.add('chat-message', 'assistant', 'typing-indicator');
        
        const avatar = document.createElement('div');
        avatar.classList.add('chat-avatar');
        avatar.innerHTML = '<i class="fas fa-robot"></i>';
        
        const content = document.createElement('div');
        content.classList.add('chat-content');
        content.innerHTML = '<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>';
        
        typingIndicator.appendChild(avatar);
        typingIndicator.appendChild(content);
        
        chatMessages.appendChild(typingIndicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Send request to server
        fetch('/chatbot/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            // Remove typing indicator
            chatMessages.removeChild(typingIndicator);
            
            if (data.success) {
                // Add response
                addMessage('assistant', data.response);
            } else {
                // Add error message
                addMessage('assistant', 'Sorry, I encountered an error. Please try again later.');
            }
        })
        .catch(error => {
            // Remove typing indicator
            chatMessages.removeChild(typingIndicator);
            
            console.error('Error:', error);
            addMessage('assistant', 'Sorry, I encountered an error. Please try again later.');
        });
    }
});

// Add custom CSS for chatbot
document.addEventListener('DOMContentLoaded', function() {
    const style = document.createElement('style');
    style.textContent = `
        .chat-toggle {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background-color: var(--bs-primary);
            color: white;
            border: none;
            cursor: pointer;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            z-index: 1000;
            transition: transform 0.3s, background-color 0.3s;
        }

        .chat-toggle:hover {
            transform: scale(1.1);
            background-color: var(--bs-primary-hover, var(--bs-primary));
        }

        .chat-container {
            position: fixed;
            bottom: 90px;
            right: 20px;
            width: 350px;
            height: 500px;
            border-radius: 10px;
            background-color: var(--bs-body-bg);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            z-index: 1000;
            border: 1px solid var(--bs-border-color);
        }

        .chat-header {
            background-color: var(--bs-primary);
            padding: 15px;
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .chat-header h5 {
            margin: 0;
            font-size: 1.1rem;
        }

        .chat-messages {
            flex-grow: 1;
            padding: 15px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .chat-message {
            display: flex;
            max-width: 85%;
        }

        .chat-message.user {
            align-self: flex-end;
            flex-direction: row-reverse;
        }

        .chat-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background-color: var(--bs-gray-200);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 10px;
        }

        .chat-message.user .chat-avatar {
            background-color: var(--bs-primary);
            color: white;
        }

        .chat-content {
            background-color: var(--bs-gray-200);
            padding: 10px 15px;
            border-radius: 18px;
            color: var(--bs-gray-800);
        }

        .chat-message.user .chat-content {
            background-color: var(--bs-primary);
            color: white;
        }

        .chat-form {
            display: flex;
            padding: 10px;
            border-top: 1px solid var(--bs-border-color);
        }

        .chat-form input {
            flex-grow: 1;
            padding: 10px 15px;
            border: 1px solid var(--bs-border-color);
            border-radius: 20px;
            margin-right: 10px;
            background-color: var(--bs-body-bg);
            color: var(--bs-body-color);
        }

        .chat-form button {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            border: none;
            background-color: var(--bs-primary);
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .typing-indicator .chat-content {
            display: flex;
            align-items: center;
            min-height: 24px;
        }

        .typing-dot {
            width: 8px;
            height: 8px;
            background-color: var(--bs-gray-500);
            border-radius: 50%;
            margin: 0 2px;
            animation: typing 1.5s infinite;
        }

        .typing-dot:nth-child(2) {
            animation-delay: 0.5s;
        }

        .typing-dot:nth-child(3) {
            animation-delay: 1s;
        }

        @keyframes typing {
            0%, 60%, 100% {
                transform: translateY(0);
            }
            30% {
                transform: translateY(-5px);
            }
        }
    `;
    document.head.appendChild(style);
});