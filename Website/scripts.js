let mediaRecorder;
let audioChunks = [];
let source_language = '';
let customer = true;
// let language_support_score = 0.1;

const serverUrl = "http://127.0.0.1:8000";

function startRecording() {
    customer = true;
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

    fetch(serverUrl + "/upload", {
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
    fetch(serverUrl + "/transcribe", {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({fileKey: filename})
    })
    .then(response => response.json())
    .then(data => {
        // language_support_score = data.transcribedTextScore;
        translateText(data.transcribedText, data.transcribedTextScore);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function translateText(text, score) {

    if (score < 0.7){
        document.querySelector('#translation_to_crew').innerText = 'Language not supported.';
        document.querySelector('#translation_to_customer').innerText = 'Language not supported.';
    } else {
        let requestBody;

        if (customer){
            requestBody = JSON.stringify({ text: text, targetLanguage: 'en' });
        } else {
            requestBody = JSON.stringify({ text: text, targetLanguage: source_language});
        }


        fetch(serverUrl + '/translate', {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: requestBody
        })
        .then(response => response.json())
        .then(data => {
            if (customer){
                document.querySelector('#translation_to_crew').innerText = data.translatedText;
                document.querySelector('#translation_to_customer').innerText = ' ';
                source_language = data.sourceLanguage;
            } else {
                document.querySelector('#translation_to_customer').innerText = data.translatedText;
                document.querySelector('#translation_to_crew').innerText = ' ';
            }
        });
    }
}

function startRecordingCrew() {
    customer = false;
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };
            mediaRecorder.start();
        });
}

function stopRecordingCrew() {
    mediaRecorder.stop();
    mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { 'type' : 'audio/mp3' });
        audioChunks = [];

        uploadFile(audioBlob);
    };
}