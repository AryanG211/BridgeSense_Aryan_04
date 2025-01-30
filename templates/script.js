function gotopage(page){
    window.location.href=page
}


// Ensure DOM content is loaded before executing
document.addEventListener("DOMContentLoaded", function () {
    // Get elements
    const submitBtn = document.getElementById('submitBtn');
    const popup = document.getElementById('result');
    const closeBtn = document.getElementById('closeBtn');
    const resultMessage = document.getElementById('resultMessage');

    // Simulate model output (replace with actual model logic)
    const modelResult = "Model result: Success!";

    // Show popup when submit is clicked
    submitBtn.addEventListener('click', function () {
        // resultMessage.textContent = ;
        fetch("http://127.0.0.1:5500/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                age: parseFloat(age),
                traffic: parseFloat(traffic),
                waterflow: parseFloat(waterflow),
                stress: parseFloat(stress),
                rainfall: parseFloat(rainfall),
                humidity: parseFloat(humidity)
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                resultMessage.textContent = "Error: " + data.error;
            } else {
                resultMessage.textContent = "Prediction: " + data.prediction;  // ✅ Show actual model output
            }
            result.classList.add("active");
        })
        .catch(error => {
            resultMessage.textContent = "Server error!";
            result.classList.add("active");
        });
        
        result.classList.add('active');
    });

    // Close popup when OK button is clicked
    closeBtn.addEventListener('click', function () {
        result.classList.remove('active');
    });
});
