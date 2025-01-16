document
  .getElementById("imageUpload")
  .addEventListener("change", function (event) {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = function (e) {
        document.getElementById("preview").src = e.target.result;
        document.getElementById("preview").style.display = "block";
        document.getElementById("submitButton").disabled = false;
      };
      reader.readAsDataURL(file);
    }
  });

document.getElementById("submitButton").addEventListener("click", function () {
  const fileInput = document.getElementById("imageUpload");
  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append("image", file);

  document.getElementById("submitButton").disabled = true;
  document.getElementById("preview").style.display = "none";
  document.getElementById("loading").style.display = "block";

  fetch("/process", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("loading").style.display = "none";
      document.getElementById("processedImage").src = data.processed_image_url;
      document.getElementById("result").style.display = "block";

      document.getElementById("originalImage").src =
        document.getElementById("preview").src;
      document.getElementById("processedImageComparison").src =
        data.processed_image_url;
      document.getElementById("comparison").style.display = "block";
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("Error processing image.");
      document.getElementById("submitButton").disabled = false;
      document.getElementById("preview").style.display = "block";
      document.getElementById("loading").style.display = "none";
    });
});
