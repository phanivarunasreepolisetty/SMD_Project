/**
 * Camera Module
 * WebRTC camera capture for tablet verification
 */

let videoStream = null;

// Initialize camera
async function initCamera() {
    const video = document.getElementById('cameraFeed');
    if (!video) return;

    try {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            throw new Error("Camera API not available. If accessing from another device, you must use HTTPS instead of HTTP.");
        }
        
        let stream;
        try {
            // Try rear camera first (which worked for you previously)
            stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: 'environment',
                    width: { ideal: 640 },
                    height: { ideal: 480 }
                }
            });
        } catch (initialError) {
            console.warn('Rear camera not found or failed, falling back to default camera...', initialError);
            // Fall back to ANY available camera
            stream = await navigator.mediaDevices.getUserMedia({
                video: true
            });
        }

        video.srcObject = stream;
        videoStream = stream;
        console.log('Camera initialized successfully');

        // Clean up any error state if camera eventually succeeds
        const overlay = document.getElementById('cameraErrorOverlay');
        if (overlay) overlay.style.display = 'none';

    } catch (error) {
        console.error('Camera error:', error);
        showCameraError(error);
    }
}

// Stop camera
function stopCamera() {
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
    }
}

// Capture image from video
function captureFrame() {
    const video = document.getElementById('cameraFeed');
    const canvas = document.getElementById('captureCanvas');

    if (!video || !canvas) return null;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);

    return canvas.toDataURL('image/jpeg', 0.8);
}

// Show camera error
function showCameraError(error) {
    const cameraSection = document.getElementById('cameraSection');
    if (!cameraSection) return;

    let overlay = document.getElementById('cameraErrorOverlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'cameraErrorOverlay';
        overlay.className = 'empty-state';
        overlay.style.position = 'absolute';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100%';
        overlay.style.height = '100%';
        overlay.style.background = 'rgba(255, 255, 255, 0.9)';
        overlay.style.zIndex = '10';
        overlay.style.display = 'flex';
        overlay.style.flexDirection = 'column';
        overlay.style.alignItems = 'center';
        overlay.style.justifyContent = 'center';

        const container = cameraSection.querySelector('.camera-container') || cameraSection;
        container.style.position = 'relative';
        container.appendChild(overlay);
    }

    overlay.style.display = 'flex';
    overlay.innerHTML = `
        <div class="empty-icon">📷</div>
        <h3>Camera Access Failed</h3>
        <p>${error.message || 'Please allow camera access and try again.'}</p>
        <button class="btn btn-primary" onclick="initCamera()" style="margin-top: 1rem;">Try Again</button>
    `;
}

// Export functions
window.CameraModule = {
    init: initCamera,
    stop: stopCamera,
    capture: captureFrame
};
