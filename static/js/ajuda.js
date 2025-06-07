document.addEventListener('DOMContentLoaded', function() {
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const toggle = item.querySelector('.faq-toggle');
        const content = item.querySelector('.faq-content');
        const arrow = item.querySelector('.arrow');
        
        toggle.addEventListener('click', () => {
            // Fecha todos os outros itens
            faqItems.forEach(otherItem => {
                if (otherItem !== item) {
                    otherItem.querySelector('.faq-content').classList.remove('show');
                    otherItem.querySelector('.arrow').classList.remove('rotate');
                }
            });
            
            // Alterna o item atual
            content.classList.toggle('show');
            arrow.classList.toggle('rotate');
        });
    });
});