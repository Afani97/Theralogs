import AudioRecorder from 'https://cdn.jsdelivr.net/npm/audio-recorder-polyfill/index.js'
import mpegEncoder from 'https://cdn.jsdelivr.net/npm/audio-recorder-polyfill/mpeg-encoder/index.js'

AudioRecorder.encoder = mpegEncoder
AudioRecorder.prototype.mimeType = 'audio/mpeg'
window.MediaRecorder = AudioRecorder