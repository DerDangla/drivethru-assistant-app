let mediaRecorder;
let audioChunks = [];

const serverUrl = "http://127.0.0.1:8000";

function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };
            mediaRecorder.start();
        });
}

function stopRecording() {
    mediaRecorder.stop();
    mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { 'type' : 'audio/mp3' });
        audioChunks = [];

        // // Create a URL for the blob
        // const audioUrl = URL.createObjectURL(audioBlob);

        // // Create a temporary link to download the file
        // const downloadLink = document.createElement('a');
        // downloadLink.href = audioUrl;
        // // The default file name could be anything you prefer
        // downloadLink.download = `recorded-${new Date().toISOString().replace(/:|\./g, '-')}.mp3`;
        // document.body.appendChild(downloadLink);
        // downloadLink.click();
        // document.body.removeChild(downloadLink);

        uploadFile(audioBlob);
    };
}

async function uploadFile(audioBlob) {
    // Convert blob to base64
    const base64String = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(audioBlob);
        reader.onload = () => resolve(reader.result.toString().replace(/^data:(.*,)?/, ''));
        reader.onerror = error => reject(error);
    });

    fetch(serverUrl + "/upload", { // This should match your Chalice API endpoint for uploading
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({filebytes: base64String})
    })
    .then(response => response.json())
    .then(data => {
        transcribeAudio(data.filename);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function transcribeAudio(filename) {
    fetch(serverUrl + "/transcribe", { // Updated to POST and endpoint structure
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({fileKey: filename})
    })
    .then(response => response.json())
    .then(data => {
        translateText(data.transcribedText);
        //console.log(data)
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function translateText(text) {
    fetch(serverUrl + '/translate', { // Your endpoint for translating
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text })
    })
    .then(response => response.json())
    .then(data => {
        document.querySelector('#translation').innerText = data.translatedText; // Displaying translated text
    });
}




