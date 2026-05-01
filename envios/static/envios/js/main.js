/* envios/static/envios/js/main.js
   Sipán Trans — Scripts básicos
-------------------------------------------------- */

document.addEventListener('DOMContentLoaded', function () {

    // ── 1. Auto-dismiss de alertas Bootstrap ────────────────
    const alerts = document.querySelectorAll('.alert.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 4000);  // cierra después de 4 segundos
    });

    // ── 2. Confirmación antes de eliminar ───────────────────
    const deleteForms = document.querySelectorAll('form[data-confirm]');
    deleteForms.forEach(function (form) {
        form.addEventListener('submit', function (e) {
            const msg = form.dataset.confirm || '¿Estás seguro de que deseas eliminar este registro?';
            if (!confirm(msg)) {
                e.preventDefault();
            }
        });
    });

    // ── 3. Tooltips Bootstrap ───────────────────────────────
    const tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    tooltipTriggerList.forEach(function (el) {
        new bootstrap.Tooltip(el);
    });

});
