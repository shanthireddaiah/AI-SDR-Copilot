/* ==========================================================================
   AI SDR Research Copilot - Light Corporate SaaS JavaScript
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // Mobile Sidebar Toggle Handler
  const menuToggle = document.getElementById('menu-toggle');
  const sidebarWrapper = document.getElementById('sidebar-wrapper');
  if (menuToggle && sidebarWrapper) {
    menuToggle.addEventListener('click', (e) => {
      e.preventDefault();
      sidebarWrapper.classList.toggle('toggled');
    });
  }

  // Initialize Bootstrap Toasts
  const toastElList = document.querySelectorAll('.toast');
  const toastList = [...toastElList].map(toastEl => new bootstrap.Toast(toastEl, { delay: 5000 }));
  toastList.forEach(toast => toast.show());

  // Show/Hide Password Toggle Handler
  const passwordToggles = document.querySelectorAll('.password-toggle-btn');
  passwordToggles.forEach(toggle => {
    toggle.addEventListener('click', () => {
      const targetId = toggle.getAttribute('data-target');
      const passwordInput = document.getElementById(targetId);
      if (passwordInput) {
        const isPassword = passwordInput.type === 'password';
        passwordInput.type = isPassword ? 'text' : 'password';
        const icon = toggle.querySelector('i');
        if (icon) {
          icon.className = isPassword ? 'bi bi-eye-slash-fill' : 'bi bi-eye-fill';
        }
      }
    });
  });

  // Attach Loading Spinners to AI Action Forms
  const aiForms = document.querySelectorAll('.form-ai-action');
  aiForms.forEach(form => {
    form.addEventListener('submit', function() {
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        const btnText = submitBtn.getAttribute('data-loading-text') || 'Processing AI Request...';
        submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> ${btnText}`;
      }
    });
  });
});

// Copy to Clipboard Utility Function
function copyToClipboard(elementId, buttonElement) {
  const textElement = document.getElementById(elementId);
  if (!textElement) return;

  const textToCopy = textElement.value || textElement.innerText;
  navigator.clipboard.writeText(textToCopy).then(() => {
    const originalText = buttonElement.innerHTML;
    buttonElement.innerHTML = `<i class="bi bi-check2"></i> Copied!`;
    buttonElement.classList.replace('btn-saas-secondary', 'btn-success');
    buttonElement.style.backgroundColor = '#22C55E';
    buttonElement.style.color = '#FFFFFF';
    buttonElement.style.borderColor = '#22C55E';

    setTimeout(() => {
      buttonElement.innerHTML = originalText;
      buttonElement.style.backgroundColor = '';
      buttonElement.style.color = '';
      buttonElement.style.borderColor = '';
      buttonElement.classList.replace('btn-success', 'btn-saas-secondary');
    }, 2200);
  }).catch(err => {
    console.error('Failed to copy text: ', err);
  });
}

// Auto-Scroll Chat Stream Window to Bottom
function scrollChatToBottom() {
  const container = document.getElementById('chat-messages-container');
  if (container) {
    container.scrollTop = container.scrollHeight;
  }
}
