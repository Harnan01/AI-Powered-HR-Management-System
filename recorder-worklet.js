class RecorderWorkletProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        this.bufferSize = 2048; // Define a buffer size (can be adjusted)
        this.buffer = new Int16Array(this.bufferSize);
        this.bufferIndex = 0;
    }

    process(inputs, outputs, parameters) {
        const input = inputs[0];
        const channelData = input[0];  // Mono recording (assuming 1 channel)

        // Convert float32 audio data to 16-bit PCM
        for (let i = 0; i < channelData.length; i++) {
            const sample = Math.max(-1, Math.min(1, channelData[i]));  // Clamp to [-1, 1]
            this.buffer[this.bufferIndex++] = sample * 0x7FFF;  // Scale to 16-bit PCM

            // If the buffer is full, send it to the main thread
            if (this.bufferIndex === this.bufferSize) {
                this.port.postMessage(this.buffer.buffer);  // Send PCM data
                this.bufferIndex = 0;  // Reset buffer index
            }
        }

        return true;  // Keep the processor alive
    }
}

registerProcessor('recorder-worklet', RecorderWorkletProcessor);
