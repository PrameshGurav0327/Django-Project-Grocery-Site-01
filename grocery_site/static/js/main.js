
setTimeout(() => {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        alert.classList.add('fade');
        setTimeout(() => alert.remove(), 500);
    });
}, 3000);

document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        btn.innerHTML = "✔️ Added!";
        btn.classList.remove('btn-success');
        btn.classList.add('btn-outline-success');
        setTimeout(() => {
            btn.innerHTML = "🛒 Add to Cart";
            btn.classList.add('btn-success');
            btn.classList.remove('btn-outline-success');
        }, 1500);
    });
});
