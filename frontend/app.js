/* =====================================================
   DASHBOARD
   ===================================================== */

async function loadDashboard() {
    try {
        const response = await fetch("/dashboard");

        if (!response.ok) {
            throw new Error("Dashboard request failed");
        }

        const data = await response.json();

        const unitsSold = document.getElementById("unitsSold");
        const revenue = document.getElementById("revenue");
        const criticalStock = document.getElementById("criticalStock");
        const salesSpikes = document.getElementById("salesSpikes");

        if (unitsSold) {
            unitsSold.textContent =
                Number(data.units_sold || 0).toLocaleString();
        }

        if (revenue) {
            revenue.textContent = data.revenue ?? "—";
        }

        if (criticalStock) {
            criticalStock.textContent =
                data.critical_stock ?? "—";
        }

        if (salesSpikes) {
            salesSpikes.textContent =
                data.sales_spikes ?? "—";
        }

    } catch (error) {
        console.error("Dashboard error:", error);
    }
}


/* =====================================================
   ASK RETAILIQ
   ===================================================== */

async function askQuestion(question = null) {

    const questionInput =
        document.getElementById("question");

    const askButton =
        document.getElementById("askButton");

    const loading =
        document.getElementById("loading");

    const responseContainer =
        document.getElementById("responseContainer");

    let response =
        document.getElementById("response");

    const errorContainer =
        document.getElementById("errorContainer");

    const errorMessage =
        document.getElementById("errorMessage");


    /* Safety checks */

    if (!questionInput) {
        console.error("RetailIQ: #question element not found.");
        return;
    }

    if (!askButton) {
        console.error("RetailIQ: #askButton element not found.");
        return;
    }


    /* Quick question */

    if (question !== null) {
        questionInput.value = question;
    }


    const userQuestion =
        questionInput.value.trim();


    if (!userQuestion) {
        questionInput.focus();
        return;
    }


    /*
     * If the response element is missing for any reason,
     * create it instead of crashing the application.
     */

    if (!responseContainer) {
        console.error(
            "RetailIQ: #responseContainer element not found."
        );
    }

    if (!response) {

        console.warn(
            "RetailIQ: #response element not found. Creating it."
        );

        if (responseContainer) {

            response =
                document.createElement("div");

            response.id = "response";
            response.className = "response";

            responseContainer.appendChild(response);

        } else {

            response =
                document.createElement("div");

            response.id = "response";
            response.className = "response";

            document.body.appendChild(response);
        }
    }


    /* Reset previous states */

    if (responseContainer) {
        responseContainer.classList.add("hidden");
    }

    if (errorContainer) {
        errorContainer.classList.add("hidden");
    }

    response.textContent = "";


    /* Loading state */

    if (loading) {
        loading.classList.remove("hidden");
    }

    askButton.disabled = true;
    askButton.textContent = "Analyzing...";


    try {

        console.log(
            "RetailIQ: Sending question:",
            userQuestion
        );


        const result =
            await fetch("/ask", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    question: userQuestion
                })

            });


        const data =
            await result.json();


        console.log(
            "RetailIQ: Server response:",
            data
        );


        if (!result.ok) {

            throw new Error(
                data.error ||
                "Unable to process your question."
            );
        }


        /* Show AI answer */

        response.textContent =
            data.answer ||
            data.summary ||
            "No answer was returned.";


        if (responseContainer) {

            responseContainer.classList.remove(
                "hidden"
            );

            responseContainer.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        }


    } catch (error) {

        console.error(
            "RetailIQ error:",
            error
        );


        if (errorMessage) {

            errorMessage.textContent =
                error.message ||
                "Unable to analyze the question.";
        }

        if (errorContainer) {

            errorContainer.classList.remove(
                "hidden"
            );
        }

    } finally {

        if (loading) {
            loading.classList.add("hidden");
        }

        askButton.disabled = false;

        askButton.textContent =
            "Ask RetailIQ";
    }
}


/* =====================================================
   QUICK QUESTIONS
   ===================================================== */

function useQuestion(question) {

    askQuestion(question);
}


/* =====================================================
   PAGE INITIALIZATION
   ===================================================== */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        loadDashboard();


        const questionInput =
            document.getElementById("question");


        if (questionInput) {

            questionInput.addEventListener(
                "keydown",
                function (event) {

                    if (
                        event.key === "Enter" &&
                        event.ctrlKey
                    ) {

                        event.preventDefault();

                        askQuestion();
                    }

                }
            );
        }

    }
);