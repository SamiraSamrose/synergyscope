//# File: frontend/static/js/meta_chat.js

// Meta Chat Interface
class MetaChat {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.messagesDiv = this.container.querySelector('.chat-messages');
        this.inputField = this.container.querySelector('.chat-input');
        this.sendButton = this.container.querySelector('.send-button');
        
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
    }
    
    async sendMessage() {
        const message = this.inputField.value.trim();
        if (!message) return;
        
        this.addMessage(message, 'user');
        this.inputField.value = '';
        
        try {
            const response = await fetch('/api/v1/meta/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    summoner_id: 'current_user',
                    question: message
                })
            });
            
            const data = await response.json();
            this.addMessage(data.response, 'bot');
        } catch (error) {
            this.addMessage('Sorry, an error occurred.', 'bot');
        }
    }
    
    addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;
        messageDiv.innerHTML = `<p>${text}</p>`;
        this.messagesDiv.appendChild(messageDiv);
        this.messagesDiv.scrollTop = this.messagesDiv.scrollHeight;
    }
}