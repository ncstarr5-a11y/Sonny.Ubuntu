const chatWindow = document.getElementById("chat-window");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const statusIndicator = document.getElementById("status-indicator");

// Create a message bubble and return the DOM element
function addMessage(text, sender) {
    const msg = document.createElement("div");
    msg.classList.add("message", sender);
    msg.textContent = text;
    chatWindow.appendChild(msg);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return msg;
}

// Update an existing message bubble
function updateMessage(msgElement, newText) {
    msgElement.textContent = newText;
    chatWindow.scrollTop = chatWindow.scrollHeight;
}
// Handle sending a message
async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    addMessage(text, "user");
    userInput.value = "";

    const sonnyMsg = addMessage("…", "sonny");

    const response = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: text })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    let fullText = "";

    while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        fullText += chunk;

        updateMessage(sonnyMsg, fullText);
    }
}

sendBtn.addEventListener("click", sendMessage);

userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        e.preventDefault();
        sendMessage();
    }
});

// Health check
async function checkStatus() {
    try {
        const res = await fetch("/health");
        if (res.ok) {
            statusIndicator.textContent = "● Online";
            statusIndicator.classList.remove("offline");
            statusIndicator.classList.add("online");
        } else {
            throw new Error();
        }
    } catch (error) {
        statusIndicator.textContent = "● Offline";
        statusIndicator.classList.remove("online");
        statusIndicator.classList.add("offline");
    }
}
//
setInterval(checkStatus, 5000);
checkStatus();