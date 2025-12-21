document.addEventListener('DOMContentLoaded', function() {
    // Обработка выбора способа оплаты
    const paymentSelect = document.querySelector('select[name="payment_method"]');
    const paymentOptions = document.querySelectorAll('.payment-option');
    
    function updatePaymentSelection() {
        const selectedValue = paymentSelect.value;
        
        paymentOptions.forEach(option => {
            option.classList.remove('selected');
            if (option.classList.contains(selectedValue)) {
                option.classList.add('selected');
            }
        });
    }
    
    updatePaymentSelection();

    paymentSelect.addEventListener('change', updatePaymentSelection);

    paymentOptions.forEach(option => {
        option.addEventListener('click', function() {
            const paymentType = this.classList.contains('cash') ? 'cash' : 'card';
            paymentSelect.value = paymentType;
            updatePaymentSelection();
        });
    });
    
    // Валидация формы
    const orderForm = document.getElementById('orderForm');
    
    orderForm.addEventListener('submit', function(event) {
        let isValid = true;
        const requiredFields = orderForm.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.style.borderColor = '#f44336';
                
                if (!field.nextElementSibling || !field.nextElementSibling.classList.contains('error')) {
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'error';
                    errorDiv.textContent = 'Это поле обязательно для заполнения';
                    field.parentNode.insertBefore(errorDiv, field.nextSibling);
                }
            } else {
                field.style.borderColor = '';
                if (field.nextElementSibling && field.nextElementSibling.classList.contains('error')) {
                    field.nextElementSibling.remove();
                }
            }
        });
        
        if (!isValid) {
            event.preventDefault();
            alert('Пожалуйста, заполните все обязательные поля.');
        }
    });
    
    const phoneInput = document.querySelector('input[name="phone"]');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            let x = e.target.value.replace(/\D/g, '').match(/(\d{0,1})(\d{0,3})(\d{0,3})(\d{0,2})(\d{0,2})/);
            e.target.value = '+7' + (x[2] ? ' (' + x[2] : '') + (x[3] ? ') ' + x[3] : '') + (x[4] ? '-' + x[4] : '') + (x[5] ? '-' + x[5] : '');
        });
    }
});