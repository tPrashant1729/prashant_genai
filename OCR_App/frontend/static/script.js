document.getElementById("uploadForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);

  try {
    const response = await fetch("/process-image/", {
      method: "POST",
      body: formData,
    });

    const result = await response.json();
    const outputDiv = document.getElementById("markdownOutput");

    // Display the HTML content directly
    outputDiv.innerHTML = result.html; // The backend returns HTML now

    document.getElementById("result").style.display = "block";
  } catch (error) {
    console.error("Error:", error);
  }
});
