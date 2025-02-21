document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Confirm delete
    const deleteButtons = document.querySelectorAll('.btn-outline-danger');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });

    // Clear form on modal close
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('hidden.bs.modal', function() {
            const forms = this.querySelectorAll('form');
            forms.forEach(form => form.reset());
        });
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Search functionality enhancement
    const searchInput = document.querySelector('input[type="search"]');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            this.classList.toggle('is-valid', this.value.length > 2);
        });
    }

    // Dynamic Subject-Chapter Selection
    const subjectSelect = document.getElementById('subject-select');
    const chapterSelect = document.getElementById('chapter-select');

    if (subjectSelect && chapterSelect) {
        subjectSelect.addEventListener('change', function() {
            const subjectId = this.value;
            chapterSelect.disabled = !subjectId;
            
            if (subjectId) {
                fetch(`/get_chapters/${subjectId}`)
                    .then(response => response.json())
                    .then(chapters => {
                        chapterSelect.innerHTML = '<option value="">Select Chapter</option>';
                        if (chapters.length > 0) {
                            chapters.forEach(chapter => {
                                chapterSelect.innerHTML += `
                                    <option value="${chapter.id}">${chapter.name}</option>
                                `;
                            });
                            chapterSelect.disabled = false;
                        } else {
                            chapterSelect.innerHTML = '<option value="">No chapters available</option>';
                            chapterSelect.disabled = true;
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching chapters:', error);
                        chapterSelect.innerHTML = '<option value="">Error loading chapters</option>';
                        chapterSelect.disabled = true;
                    });
            } else {
                chapterSelect.innerHTML = '<option value="">Select Chapter</option>';
                chapterSelect.disabled = true;
            }
        });
    }
});

function submitQuestionForm(event, form) {
    event.preventDefault();
    
    fetch(form.action, {
        method: 'POST',
        body: new FormData(form)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Close modal
            const modal = bootstrap.Modal.getInstance(form.closest('.modal'));
            modal.hide();
            
            // Reset form
            form.reset();
            
            // Refresh the page after a short delay
            setTimeout(() => {
                window.location.reload();
            }, 500);
        } else {
            alert(data.message || 'Error adding question');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error adding question');
    });
}

// Close modal on successful submission
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        if (message.classList.contains('alert-success')) {
            const modals = document.querySelectorAll('.modal');
            modals.forEach(modal => {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            });
        }
    });
}); 