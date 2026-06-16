// The Warden - CipherGuard's Chatbot Guardian (API Ready)
// Engineered & Crafted by Raj

document.addEventListener('DOMContentLoaded', () => {
    const wardenFab = document.getElementById('warden-fab');
    const wardenPanel = document.getElementById('warden-panel');
    const wardenClose = document.getElementById('warden-close');
    const chatInput = document.getElementById('warden-input');
    const sendBtn = document.getElementById('warden-send');
    const chatContent = document.getElementById('warden-chat-content');

    if (!wardenFab || !wardenPanel) return;

    let isOpen = false;

    // --- Logic ---
    
    function toggleWarden() {
        if (!isOpen) {
            wardenPanel.classList.remove('hidden');
            requestAnimationFrame(() => {
                wardenPanel.classList.add('warden-open');
                wardenFab.classList.add('scale-0');
            });
            isOpen = true;
            if (chatContent.children.length === 1) { // 1 is the bg runes
                appendMessage("The Warden", "I am awakened. State your query, and I shall consult the oracles (Gemini API).", 'bot');
            }
        } else {
            wardenPanel.classList.remove('warden-open');
            wardenFab.classList.remove('scale-0');
            setTimeout(() => {
                wardenPanel.classList.add('hidden');
            }, 400); 
            isOpen = false;
        }
    }

    function appendMessage(sender, text, type) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `flex flex-col relative z-10 w-full ${type === 'user' ? 'items-end' : 'items-start'} animate-fadeIn`;
        
        const senderSpan = document.createElement('span');
        senderSpan.className = `font-heading text-[10px] uppercase tracking-widest mb-1 opacity-70 ${type === 'user' ? 'text-highlight' : 'text-danger'}`;
        senderSpan.textContent = sender;

        const textDiv = document.createElement('div');
        if (type === 'user') {
            textDiv.className = `inline-block px-4 py-2.5 rounded-2xl rounded-tr-sm font-body text-sm bg-panel border border-divider text-primary shadow-sm max-w-[85%] leading-relaxed`;
        } else {
            textDiv.className = `inline-block px-4 py-2.5 rounded-2xl rounded-tl-sm font-body text-[14px] bg-panel-light border border-[#C9A84C] text-primary shadow-md max-w-[90%] leading-relaxed`;
        }
        textDiv.innerHTML = text;

        msgDiv.appendChild(senderSpan);
        msgDiv.appendChild(textDiv);
        
        chatContent.appendChild(msgDiv);
        chatContent.scrollTop = chatContent.scrollHeight;
        
        return textDiv;
    }

    async function handleSend() {
        const text = chatInput.value.trim();
        if (!text) return;

        // Display user message
        appendMessage("You", text, 'user');
        chatInput.value = '';
        
        // Show typing indicator
        const typingIndicator = appendMessage("The Warden", "<span class='animate-pulse'>Communing with Gemini...</span>", 'bot');
        
        try {
            const response = await fetch('http://localhost:3001/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(`API Error: ${data.details || data.error || "Unknown server error"}`);
            }
            
            // Replace typing indicator with real response
            const formattedResponse = data.response.replace(/\n/g, '<br>');
            typingIndicator.innerHTML = formattedResponse;
            chatContent.scrollTop = chatContent.scrollHeight;
            
        } catch (error) {
            let errorMsg = "The connection to the oracle was severed. Try again.";
            
            if (error.message.includes("API key not valid") || error.message.includes("missing from .env") || error.message.includes("API_KEY_INVALID")) {
                errorMsg = "[ERROR] Gemini API key is missing or invalid. Please add a valid key to your .env file and restart the Node server.";
            } else if (error.message.includes("Failed to fetch")) {
                errorMsg = "[ERROR] Cannot reach the Node.js server. Please ensure you have run 'npm start' in backend/node_server.";
            } else if (error.message.includes("API Error")) {
                errorMsg = error.message;
            }

            typingIndicator.innerHTML = errorMsg;
            typingIndicator.classList.add('text-[#8B1A1A]', 'border-[#8B1A1A]'); // danger colors
            console.error("Warden Chat Error:", error);
        }
    }

    // --- Event Listeners ---
    wardenFab.addEventListener('click', toggleWarden);
    wardenClose.addEventListener('click', toggleWarden);
    sendBtn.addEventListener('click', handleSend);
    
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSend();
        }
    });
});
