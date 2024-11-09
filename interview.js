let audioContext;
let audioWorkletNode;
let socket;
let isInterviewActive = false;
let audioBuffer = [];  // Buffer to accumulate audio chunks
const MIN_AUDIO_SAMPLES = 1323000;  // 0.1 seconds of audio at 44100 Hz

document.getElementById('start-button').addEventListener('click', () => {
    startInterview();
    document.getElementById('start-button').disabled = true;
    document.getElementById('stop-button').style.display = 'inline-block';
});

document.getElementById('stop-button').addEventListener('click', () => {
    stopInterview();
    document.getElementById('start-button').disabled = false;
    document.getElementById('stop-button').style.display = 'none';
});

// Helper function to get candidate, job, and company IDs from the URL
function getQueryParams() {
    const urlParams = new URLSearchParams(window.location.search);
    const candidateId = urlParams.get('candidate_id');
    const jobId = urlParams.get('job_id');
    const companyId = urlParams.get('company_id');
    
    return { candidateId, jobId, companyId };
}

// Start the interview by establishing a WebSocket connection
async function startInterview() {
    const statusElement = document.getElementById('status');
    const transcriptElement = document.getElementById('transcript');
    
    // Get dynamic parameters from the URL
    const { candidateId, jobId, companyId } = getQueryParams();  // Get candidate_id, job_id, and company_id from URL

    if (!candidateId || !jobId || !companyId) {
        statusElement.textContent = 'Invalid interview link. Please contact support.';
        document.getElementById('start-button').disabled = true;
        return;
    }

    const WEBSOCKET_URI = `ws://localhost:8005/ws/interview/${candidateId}/${jobId}/${companyId}/`;

    transcriptElement.innerHTML = '';
    statusElement.textContent = 'Connecting to the interview server...';

    socket = new WebSocket(WEBSOCKET_URI);
    socket.binaryType = 'arraybuffer';  // Expecting binary data for audio

    socket.onopen = function () {
        statusElement.textContent = 'Interview started.';
        console.log('WebSocket connection opened.');
        isInterviewActive = true;

        startRecording();  // Start recording and sending audio
    };

    socket.onmessage = function (event) {
        if (event.data instanceof ArrayBuffer) {
            console.log('Received audio data from server.');
            playAudio(event.data);  // Play the audio response from the server
        } else if (typeof event.data === 'string') {
            console.log('Received text message from server:', event.data);
            const data = JSON.parse(event.data);
            if (data.response) {
                transcriptElement.innerHTML += '<p><strong>AI:</strong> ' + data.response + '</p>';
            }
        }
    };

    socket.onerror = function (error) {
        console.error('WebSocket error:', error);
        statusElement.textContent = 'Error during interview. Please check your connection.';
    };

    socket.onclose = function () {
        statusElement.textContent = 'Interview ended.';
        console.log('WebSocket connection closed.');
        isInterviewActive = false;
        stopRecording();
    };
}

// Stop the interview and close WebSocket connection
function stopInterview() {
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.close();  // Close the WebSocket connection
    }
    stopRecording();  // Stop the recording
    isInterviewActive = false;
    document.getElementById('status').textContent = 'Interview stopped.';
}

// Start recording and processing audio data
async function startRecording() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert('Your browser does not support audio recording.');
        return;
    }

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioContext = new (window.AudioContext || window.webkitAudioContext)();

        // Load the AudioWorklet module (recorder-worklet.js should handle raw PCM data)
        await audioContext.audioWorklet.addModule('recorder-worklet.js');

        // Create an AudioWorkletNode to process the audio stream
        audioWorkletNode = new AudioWorkletNode(audioContext, 'recorder-worklet');

        // Listen for audio data from the AudioWorklet
        audioWorkletNode.port.onmessage = (event) => {
            const rawAudioData = new Int16Array(event.data);

            // Add raw PCM data to the audio buffer
            audioBuffer.push(...rawAudioData);

            // Check if we have enough samples to send (0.1 seconds worth of samples)
            if (audioBuffer.length >= MIN_AUDIO_SAMPLES) {
                const pcmData = audioBuffer.slice(0, MIN_AUDIO_SAMPLES);
                const wavBlob = createWAVBlob(pcmData);
                sendWAVToServer(wavBlob);

                // Remove the processed part from the buffer
                audioBuffer = audioBuffer.slice(MIN_AUDIO_SAMPLES);
            }
        };

        // Create a MediaStreamAudioSourceNode from the input stream
        const input = audioContext.createMediaStreamSource(stream);
        input.connect(audioWorkletNode);

        console.log("Recording started");

    } catch (error) {
        console.error('Error accessing microphone:', error);
        if (error.name === 'NotAllowedError') {
            alert('You need to allow microphone access for this interview.');
        } else {
            alert('Error accessing microphone.');
        }
    }
}

// Helper function to create a WAV blob from raw PCM data
function createWAVBlob(rawAudioData) {
    const wavHeader = createWAVHeader(rawAudioData);
    return new Blob([wavHeader, new Int16Array(rawAudioData)], { type: 'audio/wav' });
}

// Helper function to create a WAV header
function createWAVHeader(audioBuffer) {
    const numOfChannels = 1;  // Mono audio
    const sampleRate = 44100;  // 44.1 kHz sample rate
    const bitsPerSample = 16;  // 16-bit PCM
    const blockAlign = numOfChannels * bitsPerSample / 8;
    const byteRate = sampleRate * blockAlign;
    const dataSize = audioBuffer.length * 2;  // Each sample is 2 bytes
    const buffer = new ArrayBuffer(44);
    const view = new DataView(buffer);

    writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + dataSize, true);
    writeString(view, 8, 'WAVE');

    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);  // Linear PCM format
    view.setUint16(22, numOfChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, byteRate, true);
    view.setUint16(32, blockAlign, true);
    view.setUint16(34, bitsPerSample, true);

    writeString(view, 36, 'data');
    view.setUint32(40, dataSize, true);

    return buffer;
}

// Helper function to write a string into a DataView for the WAV header
function writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
    }
}

// Helper function to send the WAV blob to the server
function sendWAVToServer(wavBlob) {
    const reader = new FileReader();
    reader.onload = function(event) {
        const arrayBuffer = event.target.result;
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(arrayBuffer);  // Send the WAV data as ArrayBuffer
            console.log('Sent WAV data to server');
        } else {
            console.error('Error: WebSocket is closed.');
        }
    };
    reader.readAsArrayBuffer(wavBlob);  // Convert the Blob into an ArrayBuffer for sending via WebSocket
}

// Stop the recording and close the audio context
function stopRecording() {
    if (audioContext) {
        audioContext.close();
        console.log("Recording stopped");
    }
}

// Play audio received from the server
function playAudio(arrayBuffer) {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    audioContext.decodeAudioData(arrayBuffer, function (buffer) {
        const source = audioContext.createBufferSource();
        source.buffer = buffer;
        source.connect(audioContext.destination);
        source.start(0);  // Play the audio
    }, function (error) {
        console.error('Error decoding audio data:', error);
    });
}
