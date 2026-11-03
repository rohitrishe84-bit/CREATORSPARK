// CreatorSpark Main JavaScript Helpers

function copyToClipboard(elementId, buttonElement) {
  const target = document.getElementById(elementId);
  if (!target) return;

  const text = target.innerText || target.value;
  navigator.clipboard.writeText(text).then(() => {
    if (buttonElement) {
      const originalHTML = buttonElement.innerHTML;
      buttonElement.innerHTML = '<i class="bi bi-check-lg"></i> Copied!';
      buttonElement.classList.add('btn-success');
      buttonElement.classList.remove('btn-outline-primary', 'btn-outline-secondary');
      setTimeout(() => {
        buttonElement.innerHTML = originalHTML;
        buttonElement.classList.remove('btn-success');
        buttonElement.classList.add('btn-outline-primary');
      }, 2000);
    }
  }).catch(err => {
    console.error('Failed to copy: ', err);
    alert('Unable to copy to clipboard.');
  });
}

// Auto-dismiss Django alert messages after 5 seconds
document.addEventListener('DOMContentLoaded', () => {
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(alert => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });
});
