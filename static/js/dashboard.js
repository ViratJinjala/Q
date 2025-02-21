let currentQuizId = null;

function viewQuizDetails(quizId) {
    // Convert string ID to number for comparison
    const numericId = parseInt(quizId);
    const quiz = QUIZZES_DATA.find(q => q.id === numericId);
    
    if (quiz) {
        currentQuizId = numericId;
        
        // Update modal content
        document.getElementById('quizDetailsModalLabel').textContent = quiz.name || 'Quiz Details';
        document.querySelector('.quiz-subject').textContent = quiz.subject_name || 'N/A';
        document.querySelector('.quiz-chapter').textContent = quiz.chapter_name || 'N/A';
        document.querySelector('.quiz-questions').textContent = quiz.question_count || '0';
        document.querySelector('.quiz-duration').textContent = 
            quiz.time_duration ? `${quiz.time_duration} minutes` : 'N/A';

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('quizDetailsModal'));
        modal.show();
    }
}

function startQuiz(quizId) {
    // Direct navigation without confirmation
    window.location.href = `/quiz/${quizId}?q=0`;
}

function startQuizFromModal() {
    if (currentQuizId) {
        const modal = bootstrap.Modal.getInstance(document.getElementById('quizDetailsModal'));
        if (modal) modal.hide();
        startQuiz(currentQuizId);
    }
}

function sortQuizzes(by) {
    const tbody = document.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aValue = by === 'date' ? 
            a.cells[3].textContent : 
            a.cells[1].textContent;
        const bValue = by === 'date' ? 
            b.cells[3].textContent : 
            b.cells[1].textContent;
        return aValue.localeCompare(bValue);
    });
    
    tbody.innerHTML = '';
    rows.forEach(row => tbody.appendChild(row));
}

// Initialize quiz result modal if needed
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = JSON.parse(document.getElementById('flashMessages')?.value || '[]');
    flashMessages.forEach(message => {
        if (message && typeof message === 'object' && message.type === 'quiz_result') {
            const resultModal = new bootstrap.Modal(document.getElementById('quizResultModal'));
            document.getElementById('resultScore').textContent = `${message.score}%`;
            document.getElementById('resultTotal').textContent = `Total Questions: ${message.total}`;
            document.getElementById('resultCorrect').textContent = `Correct Answers: ${message.correct}`;
            resultModal.show();
        }
    });
});