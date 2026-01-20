const chatWindow = document.getElementById("chat-window");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const statusIndicator = document.getElementById("status-indicator");

function addMessage(text, sender) {
    const msg = document.createElement("div");
    msg.classList.add("message", sender);
    msg.textContent = text;
    chatWindow.appendChild(msg);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    addMessage(text, "user");
    userInput.value = "";

    const response = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: text })
    });

    const data = await response.json();
    addMessage(data.response, "sonny");
}

sendBtn.addEventListener("click", sendMessage);

userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        e.preventDefault();
        sendMessage();
    }
});

async function checkStatus() {
    try {
        console.log("Checking status...");
        const res = await fetch("/health");
        console.log("Health response:", res);
        if (res.ok) {
            statusIndicator.textContent = "● Online";
            statusIndicator.classList.remove("offline");
            statusIndicator.classList.add("online");
            console.log("Status set to online");
        } else {
            throw new Error();
        }
    } catch (error) {
        console.log("Status check failed:", error);
        statusIndicator.textContent = "● Offline";
        statusIndicator.classList.remove("online");
        statusIndicator.classList.add("offline");
    }
}

// Periodically check server status
setInterval(checkStatus, 5000);
checkStatus();