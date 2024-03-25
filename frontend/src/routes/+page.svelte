<script>
    let url = location.protocol + "//" + location.host;

    let predictedPrice = "n.a.";

    async function predict() {
        let last12MonthEarnings = parseInt(document.getElementById("last12MonthEarnings").value);
        let dollarAge = parseInt(document.getElementById("dollarAge").value);

        let result = await fetch(
            url + "/api/predict",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ last12MonthEarnings, dollarAge })
            }
        );
        let data = await result.json();
        predictedPrice = data.predictedPrice;

        document.getElementById("predictedPrice").innerText = predictedPrice;
    }
</script>

<h1>Sales Prediction</h1>

<p>
    <strong>Last 12 Month Earnings:</strong>
    <input type="number" id="last12MonthEarnings" min="0" max="100000" />
</p>

<p>
    <strong>Dollar Age:</strong>
    <input type="number" id="dollarAge" min="0" max="100" />
</p>

<button onclick="predict()">Predict</button>

<p>Predicted Price: <span id="predictedPrice">{predictedPrice}</span></p>
