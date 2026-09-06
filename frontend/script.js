const API_URL = "http://127.0.0.1:8000";


// =========================
// PDF Upload
// =========================

const pdfInput = document.getElementById("pdfInput");
const uploadButton = document.getElementById("uploadButton");
const uploadStatus = document.getElementById("uploadStatus");


uploadButton.addEventListener("click", async () => {

    const file = pdfInput.files[0];

    if (!file) {
        uploadStatus.textContent = "Please select a PDF.";
        return;
    }

    const formData = new FormData();

    formData.append("file", file);


    try {

        uploadStatus.textContent = "Uploading...";

        const response = await fetch(
            `${API_URL}/documents/uploads`,
            {
                method: "POST",
                body: formData
            }
        );


        if (!response.ok) {

            const errorText = await response.text();

            throw new Error(
                `Upload failed (${response.status}): ${errorText}`
            );
        }


        const data = await response.json();


        uploadStatus.textContent =
            `Uploaded ${data.file_name}. ` +
            `${data.chunks} chunks created. ` +
            `${data.embeddings} embeddings created.`;


    } catch (error) {

        uploadStatus.textContent =
            error.message;

        console.error("UPLOAD ERROR:", error);
    }

});


// =========================
// Ask Question
// =========================

const questionInput = document.getElementById("questionInput");
const askButton = document.getElementById("askButton");
const answer = document.getElementById("answer");


askButton.addEventListener("click", async () => {

    const question = questionInput.value.trim();


    if (!question) {

        answer.textContent =
            "Please enter a question.";

        return;
    }


    try {

        answer.textContent = "Thinking...";


        // Send question to FastAPI
        const response = await fetch(
            `${API_URL}/chat/`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    question: question
                })
            }
        );


        // Check HTTP status
        if (!response.ok) {

            const errorText = await response.text();

            throw new Error(
                `Server error (${response.status}): ${errorText}`
            );
        }


        // Make sure the browser received a stream
        if (!response.body) {

            throw new Error(
                "The server did not return a response body."
            );
        }


        // Clear "Thinking..."
        answer.textContent = "";


        // Get the response stream
        const reader = response.body.getReader();

        const decoder = new TextDecoder();


        // Read chunks continuously
        let fullAnswer = "";

        while (true) {

            const { value, done } = await reader.read();

            if (done) {
                break;
            }

            const text = decoder.decode(value, {
                stream: true
            });

            fullAnswer += text;

            answer.innerHTML = marked.parse(fullAnswer);
        }


    } catch (error) {

        answer.textContent =
            error.message;

        console.error("CHAT ERROR:", error);
    }

});