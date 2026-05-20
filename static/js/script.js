// ========================================
// FORM HANDLING & API CALLS
// ========================================

const plannerForm = document.getElementById('plannerForm');
const submitBtn = document.getElementById('submitBtn');
const loadingSpinner = document.getElementById('loadingSpinner');
const errorMessage = document.getElementById('errorMessage');
const resultCard = document.getElementById('resultCard');
const plannerCard = document.querySelector('.planner-card');
const newPlanBtn = document.getElementById('newPlanBtn');

// Handle form submission
plannerForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const city = document.getElementById('city').value.trim();
    const interests = document.getElementById('interests').value.trim();

    // Validation
    if (!city || !interests) {
        showError('Please fill in both City and Interests to proceed.');
        return;
    }

    // Show loading state
    loadingSpinner.style.display = 'block';
    errorMessage.style.display = 'none';
    plannerCard.style.display = 'none';
    resultCard.style.display = 'none';
    submitBtn.disabled = true;

    try {
        const response = await fetch('/generate-itinerary', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                city: city,
                interests: interests
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to generate itinerary');
        }

        // Display result
        displayItinerary(data);

    } catch (error) {
        showError(error.message || 'An error occurred. Please try again.');
    } finally {
        loadingSpinner.style.display = 'none';
        submitBtn.disabled = false;
    }
});

// Display itinerary
function displayItinerary(data) {
    document.getElementById('resultCity').textContent = data.city;
    document.getElementById('resultInterests').textContent = data.interests;
    document.getElementById('itineraryContent').innerHTML = formatItinerary(data.itinerary);

    plannerCard.style.display = 'none';
    resultCard.style.display = 'block';

    // Scroll to result
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Format itinerary text for better readability
function formatItinerary(text) {
    let html = text
        .split('\n')
        .map(line => {
            line = line.trim();
            if (!line) return '';

            // Handle headings
            if (line.match(/^#+\s/)) {
                const level = line.match(/^#+/)[0].length;
                const text = line.replace(/^#+\s/, '');
                return `<h${level}>${escapeHtml(text)}</h${level}>`;
            }

            // Handle bold
            line = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

            // Handle italic
            line = line.replace(/\*(.*?)\*/g, '<em>$1</em>');

            // Handle bullet points
            if (line.startsWith('- ')) {
                return `<li>${escapeHtml(line.substring(2))}</li>`;
            }

            // Handle numbered lists
            if (line.match(/^\d+\.\s/)) {
                return `<li>${escapeHtml(line)}</li>`;
            }

            return `<p>${escapeHtml(line)}</p>`;
        })
        .join('\n');

    // Wrap consecutive lists
    html = html.replace(/(<li>.*?<\/li>)/s, '<ul>$1</ul>');
    html = html.replace(/<\/ul>\n<ul>/g, '');

    return html;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Show error message
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    plannerCard.style.display = 'block';
    resultCard.style.display = 'none';
}

// Handle "Plan Another Trip" button
newPlanBtn.addEventListener('click', () => {
    plannerForm.reset();
    plannerCard.style.display = 'block';
    resultCard.style.display = 'none';
    errorMessage.style.display = 'none';
    plannerForm.scrollIntoView({ behavior: 'smooth', block: 'start' });
});

// Clear error message on input
document.getElementById('city').addEventListener('input', () => {
    if (errorMessage.style.display !== 'none') {
        errorMessage.style.display = 'none';
    }
});

document.getElementById('interests').addEventListener('input', () => {
    if (errorMessage.style.display !== 'none') {
        errorMessage.style.display = 'none';
    }
});
