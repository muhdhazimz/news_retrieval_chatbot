const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");

function appendMessage(message, sender) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add(sender);

    // Process the message to handle formatting
    messageDiv.innerHTML = formatMessage(message);  // Using innerHTML for formatted text

    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the latest message
}

function formatMessage(message) {
    // Convert markdown-like syntax to HTML
    let formattedMessage = message;

    // Replace **bold** with <b>bold</b>
    formattedMessage = formattedMessage.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');

    // Replace *italic* with <i>italic</i>
    formattedMessage = formattedMessage.replace(/\*(.*?)\*/g, '<i>$1</i>');

    // Replace __underline__ with <u>underline</u>
    formattedMessage = formattedMessage.replace(/__(.*?)__/g, '<u>$1</u>');

    // Replace newlines (\n) with <br> tags
    formattedMessage = formattedMessage.replace(/\n/g, '<br>');

    return formattedMessage;
}

async function sendMessage() {
    const userMessage = userInput.value;
    if (userMessage.trim() === "") return;

    // Display the user message
    appendMessage(userMessage, "user");

    // Get the client_id (can be hardcoded or dynamically generated)
    const client_id = "28";  // Replace with actual client_id if needed

    try {
        const myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");  // Set content type to JSON
        
        const raw = JSON.stringify({
          "query": userMessage,
          "client_id": client_id
        });
        
        const requestOptions = {
          method: "POST",
          headers: myHeaders,
          body: raw,
          redirect: "follow"
        };
        
        // Send the POST request to the backend
        const response = await fetch("http://localhost:8000/chat", requestOptions);

        // Parse the response as text
        const data = await response.text();

        // Remove any leading or trailing quotation marks from the response
        const cleanedResponse = data.replace(/^"|"$/g, "");

        // Display the bot's response
        const botResponse = cleanedResponse || "No response from bot";  // If no response, fallback message
        appendMessage(botResponse, "bot");
    } catch (error) {
        console.error("Error:", error);
        appendMessage("Sorry, something went wrong. Please try again.", "bot");
    }

    // Clear input field
    userInput.value = "";
}

// Add an event listener for the "Enter" key to trigger sending the message
userInput.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        event.preventDefault(); // Prevent the default "Enter" key behavior (e.g., form submission)
        sendMessage();
    }
});