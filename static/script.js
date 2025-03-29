async function analyzeText() {
    let text = document.getElementById("manualText").value.trim();
    if (!text) {
        alert("Please enter text before analyzing!");
        return;
    }

    let response = await fetch("/analyze_text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text })
    });

    let result = await response.json();
    displayResult(result);
}

async function analyzeImage() {
    let imageFile = document.getElementById("imageInput").files[0];

    if (!imageFile) {
        alert("Please select an image!");
        return;
    }

    let formData = new FormData();
    formData.append("image", imageFile);

    // Show loader
    document.getElementById("loader").style.display = "block";

    try {
        let response = await fetch("/analyze_image", {
            method: "POST",
            body: formData
        });

        let result = await response.json();
        displayResult(result);
    } catch (error) {
        console.error("Error analyzing image:", error);
        alert("Error processing image. Please try again.");
    } finally {
        // Hide loader when process is complete
        document.getElementById("loader").style.display = "none";
    }
}



function displayResult(result) {
    let resultDiv = document.getElementById("result");
    resultDiv.innerHTML = `
        <p><strong>Extracted Text:</strong> ${result.text}</p>
        <p><strong>Risk Level:</strong> ${result.risk_level} (${result.risk_percentage.toFixed(2)}%)</p>
    `;
    resultDiv.style.display = "block";
}
