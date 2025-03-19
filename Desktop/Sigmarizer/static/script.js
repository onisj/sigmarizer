document.getElementById('summarize-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const loading = document.getElementById('loading');
    const result = document.getElementById('result');
    loading.style.display = 'flex';
    result.style.display = 'none';

    const formData = new FormData(this);
    try {
        const response = await fetch('/api/summarize', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if (response.ok) {
            document.getElementById('summary-text').textContent = data.summary;
            document.getElementById('video-link').href = data.video_url || '#';
            document.getElementById('video-link').textContent = data.video_url || 'Not available';

            // Set thumbnail URL
            const thumbnail = document.getElementById('thumbnail');
            thumbnail.src = data.thumbnail_url || ''; // Default to empty if null
            thumbnail.style.display = data.thumbnail_url ? 'block' : 'none';

            const sentimentText = document.getElementById('sentiment-text');
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

            const audioPlayer = document.getElementById('audio-player');
            if (formData.get('tts_enabled') === 'on' && data.video_url) {
                audioPlayer.style.display = 'block';
                audioPlayer.src = '/play_audio?' + new Date().getTime();
            } else {
                audioPlayer.style.display = 'none';
            }
            result.style.display = 'block';
        }
    } catch (error) {
        console.error('Error:', error);
    } finally {
        loading.style.display = 'none';
    }
});