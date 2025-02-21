const quizData = {
    1: {
        name: 'Random Variables',
        subject: 'Mathematics',
        chapter: 'Random Variables',
        questions: '05',
        duration: '00:10'
    },
    2: {
        name: 'Probability',
        subject: 'Mathematics',
        chapter: 'Probability',
        questions: '10',
        duration: '00:10'
    },
    3: {
        name: 'Statistics',
        subject: 'Mathematics',
        chapter: 'Statistics',
        questions: '15',
        duration: '00:30'
    }
}; 

// Add click handlers to view buttons
document.querySelectorAll('.btn-view').forEach(button => {
    button.addEventListener('click', function() {
        const quizId = this.closest('tr').querySelector('td:first-child').textContent;
        const quiz = quizData[quizId];
        
        // Update modal title with quiz name
        document.querySelector('.modal-title').textContent = quiz.name + ' Quiz';
        
        // Update modal content with quiz details
        document.querySelector('.quiz-subject').textContent = quiz.subject;
        document.querySelector('.quiz-chapter').textContent = quiz.chapter;
        document.querySelector('.quiz-questions').textContent = quiz.questions;
        document.querySelector('.quiz-duration').textContent = quiz.duration;
        
        // Show the modal
        const modal = new bootstrap.Modal(document.getElementById('quizDetailsModal'));
        modal.show();
    });
});