/**
 * Voice Module
 * Web Speech API for voice alerts
 */

// Check if speech synthesis is supported
const speechSupported = 'speechSynthesis' in window;

// Speak a message
function speakAlert(message, options = {}) {
    if (!speechSupported) {
        console.warn('Speech synthesis not supported');
        return false;
    }

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(message);
    utterance.lang = options.lang || 'en-US';
    utterance.rate = options.rate || 0.9;
    utterance.pitch = options.pitch || 1;
    utterance.volume = options.volume || 1;

    utterance.onstart = () => console.log('Speaking:', message);
    utterance.onend = () => console.log('Finished speaking');
    utterance.onerror = (e) => console.error('Speech error:', e);

    window.speechSynthesis.speak(utterance);
    return true;
}

// Predefined alerts
const ALERTS = {
    correct: 'Correct medicine verified. You may take your tablet now.',
    wrong: 'Warning! This is the wrong medicine. Please do not take it.',
    uncertain: 'Unable to identify the tablet. Please try again.',
    reminder: 'Reminder. You have a pending medicine. Please take it now.'
};

// Play predefined alert
function playAlert(type) {
    const message = ALERTS[type] || type;
    return speakAlert(message);
}

// Stop speaking
function stopSpeaking() {
    if (speechSupported) {
        window.speechSynthesis.cancel();
    }
}

// Loop an alert (continuous reminder)
function loopAlert(message, options = {}) {
    if (!speechSupported) return false;

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(message);
    utterance.lang = options.lang || 'en-US';
    utterance.rate = options.rate || 0.9;

    // Automatically repeat when it finishes unless cancelled
    utterance.onend = () => {
        // Wait 2 seconds before repeating
        setTimeout(() => {
            // Must create a new utterance object to avoid bugs in some browsers
            const nextUtterance = new SpeechSynthesisUtterance(message);
            nextUtterance.lang = utterance.lang;
            nextUtterance.rate = utterance.rate;
            nextUtterance.onend = utterance.onend; // re-attach the loop handler
            window.speechSynthesis.speak(nextUtterance);
        }, 2000);
    };

    window.speechSynthesis.speak(utterance);
    return true;
}

window.VoiceModule = {
    speak: speakAlert,
    playAlert,
    stop: stopSpeaking,
    loopAlert: loopAlert,
    supported: speechSupported
};
