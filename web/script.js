const startButton = document.getElementById('startButton');
const stopButton = document.getElementById('stopButton');
const segmentsContainer = document.getElementById('transcribeResult');

let mediaRecorder;
let audioChunks = [];

startButton.addEventListener('click', async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.addEventListener('dataavailable', event => {
        audioChunks.push(event.data);
    });

    mediaRecorder.addEventListener('stop', async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const audioData = await audioBlob.arrayBuffer();
        websocket.send(audioData);

        const saveAudioData = URL.createObjectURL(audioBlob);
        const downloadLink = document.createElement('a');
        downloadLink.href = saveAudioData;
        downloadLink.download = 'audio_recording.mp4';
        downloadLink.textContent = 'Download Audio';
        segmentsContainer.appendChild(downloadLink);
        audioChunks = [];
    });

    mediaRecorder.start();
    startButton.disabled = true;
    stopButton.disabled = false;
});

stopButton.addEventListener('click', () => {
    mediaRecorder.stop();
    startButton.disabled = false;
    stopButton.disabled = true;
    mediaRecorder = null; // Reset mediaRecorder object
    audioChunks = []; // Clear previous audio chunks
});

const websocket = new WebSocket('ws://192.168.0.26:8765');

websocket.onopen = () => {
    document.getElementById('status').innerText = 'WebSocket Connected';
    document.getElementById("status").style.backgroundColor = "#d9edf7";
    console.log('WebSocket connected');
};

websocket.onerror = (error) => {
    console.error('WebSocket error:', error);
};

websocket.onmessage = (event) => {
    const data = JSON.parse(event.data); // Parse the JSON data
    console.log('Message from server:', event.data);
    data.forEach(segment => {
        const { text, start, end } = segment;
        displaySegment(text, start, end);
        console.log(`Text: ${text}, Start: ${start}, End: ${end}`);
    });
    //displayMessage(event.data);
    // You can handle the message here, for example, display it on the webpage
};

function displaySegment(text, start, end) {
    const segmentElement = document.createElement('div');
    segmentElement.classList.add('segment');
    segmentElement.innerHTML = `
        <p>${start} : ${end} -> ${text}</p>
    `;
    segmentsContainer.appendChild(segmentElement);
}

function displayMessage(message) {
    const messageElement = document.createElement('p');
    messageElement.textContent = message;
    messageContainer.appendChild(messageElement);
}
