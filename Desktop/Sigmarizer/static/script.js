document.getElementById('summarize-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    // Get DOM elements with null checks
    const form = document.getElementById('summarize-form');
    const loading = document.getElementById('loading');
    const result = document.getElementById('result');

    if (!form) {
        console.error('Form element not found');
        return;
    }
    if (!loading) {
        console.error('Loading element not found');
        return;
    }
    if (!result) {
        console.error('Result element not found');
        return;
    }

    // Show loading spinner, hide result
    loading.style.display = 'flex';
    result.style.display = 'none';

    // Get form data
    const formData = new FormData(this);
    
    try {
        // Call the API endpoint
        const response = await fetch('/api/summarize', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            // Update summary
            const summaryText = document.getElementById('summary-text');
            if (summaryText) {
                summaryText.textContent = data.summary;
            } else {
                console.warn('Summary text element not found');
            }

            // Update video link
            const videoLink = document.getElementById('video-link');
            if (videoLink) {
                videoLink.href = data.video_url || '#';
                videoLink.textContent = data.video_url || 'Not available';
            } else {
                console.warn('Video link element not found');
            }

            // Update sentiment with highlights
            const sentimentText = document.getElementById('sentiment-text');
            if (sentimentText) {
                sentimentText.innerHTML = data.sentiment || 'No sentiment analysis available.';
                sentimentText.classList.remove('positive', 'negative', 'neutral', 'excitement', 'frustration', 'curiosity');
                if (data.sentiment) {
                    const sentimentLower = data.sentiment.toLowerCase();
                    if (sentimentLower.includes('positive')) sentimentText.classList.add('positive');
                    if (sentimentLower.includes('negative')) sentimentText.classList.add('negative');
                    if (sentimentLower.includes('neutral')) sentimentText.classList.add('neutral');
                    if (sentimentLower.includes('excitement')) sentimentText.classList.add('excitement');
                    if (sentimentLower.includes('frustration')) sentimentText.classList.add('frustration');
                    if (sentimentLower.includes('curiosity')) sentimentText.classList.add('curiosity');
                }
            } else {
                console.warn('Sentiment text element not found');
            }

            // Update audio player
            const audioPlayer = document.getElementById('audio-player');
            if (audioPlayer) {
                if (formData.get('tts_enabled') === 'on' && data.video_url) {
                    audioPlayer.style.display = 'block';
                    audioPlayer.src = '/play_audio?' + new Date().getTime();
                } else {
                    audioPlayer.style.display = 'none';
                }
            } else {
                console.warn('Audio player element not found');
            }

            // Show result, hide loading
            result.style.display = 'block';
        } else {
            if (summaryText) {
                summaryText.textContent = `Error: ${data.error}`;
            }
            result.style.display = 'block';
        }
    } catch (error) {
        if (summaryText) {
            summaryText.textContent = `Error: ${error.message}`;
        }
        result.style.display = 'block';
    } finally {
        loading.style.display = 'none';
    }
});