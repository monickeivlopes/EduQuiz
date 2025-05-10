
        const toggles = document.querySelectorAll('.faq-toggle');
        const answers = document.querySelectorAll('.faq-answer');
        const arrows = document.querySelectorAll('.arrow');
    
        toggles.forEach((btn, index) => {
            btn.addEventListener('click', () => {
                answers.forEach((answer, i) => {
                    if (i === index) {
                        const isActive = answer.classList.contains('active');
                        answer.classList.toggle('active', !isActive);
                        arrows[i].classList.toggle('rotate', !isActive);
                    } else {
                        answer.classList.remove('active');
                        arrows[i].classList.remove('rotate');
                    }
                });
            });
        });
