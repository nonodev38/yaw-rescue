/**
 * AUTO-YAW DECK — Common modal helpers (P5.1)
 * Used by info.js (config help ⓘ) and readme.js (about / troubleshooting).
 * Expected DOM (both modales share the same classes):
 *   .info-modal > .info-panel > .info-panel-header (.info-close) + .info-panel-body
 * where the body receives .info-section / .info-heading / .info-text blocks.
 */
function openModal(modalEl, titleEl, bodyEl, data) {
    titleEl.textContent = data.title;
    bodyEl.innerHTML = data.sections.map(s =>
        `<div class="info-section">
            <div class="info-heading">${s.heading}</div>
            <div class="info-text">${s.text.replace(/\n/g, '<br>')}</div>
        </div>`
    ).join('');
    modalEl.classList.add('open');
}

function closeModal(modalEl) {
    modalEl.classList.remove('open');
}

function initModal(modalEl) {
    if (!modalEl || modalEl.getAttribute('data-modal-inited') === '1') return;
    modalEl.setAttribute('data-modal-inited', '1');

    // Close on backdrop click
    modalEl.addEventListener('click', (e) => {
        if (e.target === modalEl) closeModal(modalEl);
    });

    // Close on the X button
    const closeBtn = modalEl.querySelector('.info-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            closeModal(modalEl);
        });
    }

    // Close on Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal(modalEl);
    });
}