document.getElementById('sendBtn').addEventListener('click', async () => {
  const userInput = document.getElementById('userInput').value;

  if (userInput.trim() === "") return;

  // Display user message
  const chatbox = document.getElementById('chatbox');
  const userMessage = document.createElement('div');
  userMessage.textContent = `You: ${userInput}`;
  chatbox.appendChild(userMessage);

  // Send message to backend
  try {
    const response = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ prompt: userInput })
    });

    const data = await response.json();
    const modelMessage = document.createElement('div');
    modelMessage.textContent = `Model: ${data.response}`;
    chatbox.appendChild(modelMessage);
  } catch (error) {
    const errorMessage = document.createElement('div');
    errorMessage.textContent = `Error: ${error.message}`;
    chatbox.appendChild(errorMessage);
  }

  // Clear input
  document.getElementById('userInput').value = "";
  chatbox.scrollTop = chatbox.scrollHeight;
});
