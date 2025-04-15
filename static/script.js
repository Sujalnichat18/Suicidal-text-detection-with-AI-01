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

    if (!response.ok || result.error) {
        alert("Error analyzing text: " + (result.error || "Unknown error"));
        return;
    }

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

        if (!response.ok || result.error) {
            throw new Error(result.error || "Unknown error occurred.");
        }

        displayResult(result);

    } catch (error) {
        console.error("Error analyzing image:", error);
        alert("Error processing image: " + error.message);
    } finally {
        // Hide loader
        document.getElementById("loader").style.display = "none";
    }
}

function displayResult(result) {
    let resultDiv = document.getElementById("result");

    if (!result || typeof result.risk_percentage !== "number") {
        resultDiv.innerHTML = `<p style="color:red;"><strong>Error:</strong> Invalid result from server.</p>`;
        resultDiv.style.display = "block";
        return;
    }

    resultDiv.innerHTML = `
        <p><strong>Extracted Text:</strong> ${result.text}</p>
        <p><strong>Risk Level:</strong> ${result.risk_level} (${result.risk_percentage.toFixed(2)}%)</p>
    `;
    resultDiv.style.display = "block";
}
