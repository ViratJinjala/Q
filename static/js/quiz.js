// Get quiz data from hidden input
const quizDataElement = document.getElementById('quizData');
const quizDuration = parseInt(quizDataElement.dataset.duration) * 60; // in seconds

// Initialize quiz when page loads
window.onload = function() {
    // Check if timer is already running
    if (!localStorage.getItem('quizStarted')) {
        initializeQuiz();
    } else {
        startTimer();
        loadSavedAnswers();
    }
};

function initializeQuiz() {
    // Clear any existing quiz data
    localStorage.clear();
    
    // Start quiz immediately without confirmation
    localStorage.setItem('quizStarted', 'true');
    localStorage.setItem('quizStartTime', Date.now().toString());
    startTimer();
}

function startTimer() {
    let timerInterval;
    
    function updateTimer() {
        const startTime = parseInt(localStorage.getItem('quizStartTime'));
        const now = Date.now();
        const elapsedSeconds = Math.floor((now - startTime) / 1000);
        const remainingSeconds = quizDuration - elapsedSeconds;

        if (remainingSeconds <= 0) {
            clearInterval(timerInterval);
            alert('Time is up! Submitting quiz...');
            document.getElementById('quizForm').submit();
            return;
        }

        const hours = Math.floor(remainingSeconds / 3600);
        const minutes = Math.floor((remainingSeconds % 3600) / 60);
        const seconds = remainingSeconds % 60;

        const timeString = `Time Left: ${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        document.getElementById('timer').textContent = timeString;
    }

    updateTimer();
    timerInterval = setInterval(updateTimer, 1000);
}

function saveAnswer() {
    const form = document.getElementById('quizForm');
    const formData = new FormData(form);
    const answers = {};
    
    for (let pair of formData.entries()) {
        answers[pair[0]] = pair[1];
    }
    
    localStorage.setItem('quizAnswers', JSON.stringify(answers));
}

function loadSavedAnswers() {
    const savedAnswers = localStorage.getItem('quizAnswers');
    if (savedAnswers) {
        const answers = JSON.parse(savedAnswers);
        for (let name in answers) {
            const input = document.querySelector(`input[name="${name}"][value="${answers[name]}"]`);
            if (input) input.checked = true;
        }
    }
}

function submitQuiz() {
    localStorage.clear(); // Clear all stored quiz data
}

// Save answers before page unloads
window.onbeforeunload = function() {
    if (localStorage.getItem('quizStarted')) {
        saveAnswer();
    }
};