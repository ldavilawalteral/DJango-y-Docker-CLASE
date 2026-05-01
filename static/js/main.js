/* static/js/main.js  —  Sipán Trans */

document.addEventListener('DOMContentLoaded', function () {

    // ── 1. Auto-dismiss alertas Bootstrap (4 seg) ──────────
    document.querySelectorAll('.alert.alert-dismissible').forEach(function (alert) {
        setTimeout(function () {
            const instance = bootstrap.Alert.getOrCreateInstance(alert);
            if (instance) instance.close();
        }, 4000);
    });

    // ── 2. Confirmación antes de eliminar ──────────────────
    document.querySelectorAll('form[data-confirm]').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            const msg = form.dataset.confirm || '¿Estás seguro?';
            if (!confirm(msg)) e.preventDefault();
        });
    });

    // ── 3. Tooltips Bootstrap ──────────────────────────────
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
        new bootstrap.Tooltip(el);
    });

});
