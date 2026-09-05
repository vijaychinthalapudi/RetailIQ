async function askQuestion() {
    const questionInput = document.getElementById("question");
    const askButton = document.getElementById("askButton");

    const loading = document.getElementById("loading");
    const responseContainer = document.getElementById("responseContainer");
    const response = document.getElementById("response");

    const errorContainer = document.getElementById("errorContainer");
    const errorMessage = document.getElementById("errorMessage");

    const question = questionInput.value.trim();

    if (!question) {
        questionInput.focus();
        return;
    }

    // Reset previous result
    responseContainer.classList.add("hidden");
    errorContainer.classList.add("hidden");

    // Show loading
    loading.classList.remove("hidden");
    askButton.disabled = true;
    askButton.textContent = "Analyzing...";

    try {
        const result = await fetch("/ask", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question: question
            })
        });

        const data = await result.json();

        if (!result.ok) {
            throw new Error(
                data.error || "Unable to process your question."
            );
        }

        response.textContent = data.answer;

        responseContainer.classList.remove("hidden");

    } catch (error) {

        errorMessage.textContent = error.message;

        errorContainer.classList.remove("hidden");

    } finally {

        loading.classList.add("hidden");

        askButton.disabled = false;
        askButton.textContent = "Ask RetailIQ";
    }
}


/*
 * Put an example question into the question box.
 */
function useQuestion(question) {

    const questionInput = document.getElementById("question");

    questionInput.value = question;

    questionInput.focus();
}


/*
 * Allow Ctrl + Enter to submit the question.
 */
document.getElementById("question").addEventListener(
    "keydown",
    function (event) {

        if (event.ctrlKey && event.key === "Enter") {
            askQuestion();
        }

    }
);