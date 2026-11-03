// CreatorSpark Global Assistant Chat Widget
// Communicates with /api/assistant/chat/ and persists to MongoDB backend

(function () {
  let conversationId = localStorage.getItem('cs_conversation_id');
  if (!conversationId) {
    conversationId = 'conv_' + Math.random().toString(36).substring(2, 11) + '_' + Date.now();
    localStorage.setItem('cs_conversation_id', conversationId);
  }

  const launcher = document.getElementById('cs-chat-launcher');
  const container = document.getElementById('cs-chat-container');
  const closeBtn = document.getElementById('cs-chat-close');
  const minimizeBtn = document.getElementById('cs-chat-minimize');
  const form = document.getElementById('cs-chat-form');
  const input = document.getElementById('cs-chat-input');
  const messagesContainer = document.getElementById('cs-chat-messages');

  if (!launcher || !container) return;

  function toggleChat(show) {
    if (show === undefined) {
      const isVisible = container.style.display === 'flex';
      container.style.display = isVisible ? 'none' : 'flex';
      launcher.style.display = isVisible ? 'flex' : 'none';
      if (!isVisible) input.focus();
    } else if (show) {
      container.style.display = 'flex';
      launcher.style.display = 'none';
      input.focus();
    } else {
      container.style.display = 'none';
      launcher.style.display = 'flex';
    }
  }

  launcher.addEventListener('click', () => toggleChat(true));
  closeBtn.addEventListener('click', () => toggleChat(false));
  minimizeBtn.addEventListener('click', () => toggleChat(false));

  function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  function appendMessage(role, text, timeStr) {
    const time = timeStr || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${role}`;

    // Format newlines and basic markdown bolding
    let formatted = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br>');

    bubble.innerHTML = `<div>${formatted}</div><span class="timestamp">${time}</span>`;
    messagesContainer.appendChild(bubble);
    scrollToBottom();
    return bubble;
  }

  function appendTicketPrompt(suggestedSubject, suggestedDesc) {
    const promptDiv = document.createElement('div');
    promptDiv.className = 'p-2 bg-light rounded border mt-2 text-center';
    promptDiv.innerHTML = `
      <div class="small text-muted mb-2"><i class="bi bi-ticket-perforated"></i> Need direct help from our team?</div>
      <button class="btn btn-sm btn-primary w-100" id="cs-confirm-ticket-btn">
        <i class="bi bi-plus-circle"></i> Create Support Ticket Now
      </button>
    `;
    messagesContainer.appendChild(promptDiv);
    scrollToBottom();

    const btn = promptDiv.querySelector('#cs-confirm-ticket-btn');
    btn.addEventListener('click', async () => {
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Creating ticket...';

      try {
        const res = await fetch('/api/assistant/chat/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') || ''
          },
          body: JSON.stringify({
            conversation_id: conversationId,
            action: 'confirm_ticket',
            ticket_subject: suggestedSubject || 'Escalated Assistant Inquiry',
            ticket_desc: suggestedDesc || 'User confirmed escalation through Assistant chat widget.'
          })
        });

        const data = await res.json();
        promptDiv.remove();
        appendMessage('assistant', data.reply);
      } catch (err) {
        promptDiv.innerHTML = '<div class="text-danger small">Failed to create ticket. Please use the Support page.</div>';
      }
    });
  }

  function appendFeedbackWidget() {
    const feedbackDiv = document.createElement('div');
    feedbackDiv.className = 'd-flex align-items-center justify-content-end gap-2 mt-1 mb-2 px-1';
    feedbackDiv.innerHTML = `
      <span class="text-muted" style="font-size: 0.72rem;">Was this helpful?</span>
      <button class="btn btn-sm btn-outline-secondary py-0 px-2 btn-feedback" data-rating="5" title="Helpful" style="font-size: 0.75rem;">👍</button>
      <button class="btn btn-sm btn-outline-secondary py-0 px-2 btn-feedback" data-rating="1" title="Not helpful" style="font-size: 0.75rem;">👎</button>
    `;
    messagesContainer.appendChild(feedbackDiv);
    scrollToBottom();

    feedbackDiv.querySelectorAll('.btn-feedback').forEach(b => {
      b.addEventListener('click', async () => {
        const rating = b.getAttribute('data-rating');
        feedbackDiv.innerHTML = '<span class="text-success" style="font-size: 0.72rem;"><i class="bi bi-check2"></i> Thank you!</span>';
        try {
          await fetch('/api/assistant/feedback/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken') || ''
            },
            body: JSON.stringify({
              conversation_id: conversationId,
              rating: parseInt(rating),
              feedback_text: 'Inline chat rating'
            })
          });
        } catch (e) {
          console.warn('Feedback log error:', e);
        }
      });
    });
  }

  async function sendMessage(text) {
    if (!text || !text.trim()) return;

    appendMessage('user', text.trim());
    input.value = '';

    // Show typing loader
    const loader = document.createElement('div');
    loader.className = 'chat-bubble assistant text-muted fst-italic';
    loader.id = 'cs-typing-indicator';
    loader.innerHTML = '<span class="spinner-grow spinner-grow-sm me-1" role="status"></span> Assistant is checking knowledge base...';
    messagesContainer.appendChild(loader);
    scrollToBottom();

    try {
      const response = await fetch('/api/assistant/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken') || ''
        },
        body: JSON.stringify({
          message: text.trim(),
          conversation_id: conversationId
        })
      });

      const indicator = document.getElementById('cs-typing-indicator');
      if (indicator) indicator.remove();

      if (response.ok) {
        const data = await response.json();
        appendMessage('assistant', data.reply);

        if (data.can_create_ticket) {
          appendTicketPrompt(data.suggested_subject, data.suggested_description);
        } else {
          appendFeedbackWidget();
        }
      } else {
        appendMessage('assistant', 'Sorry, I encountered an issue connecting to the knowledge base. Please check back shortly or visit our Support page. (Ref: CS-API-001)');
      }
    } catch (err) {
      const indicator = document.getElementById('cs-typing-indicator');
      if (indicator) indicator.remove();
      appendMessage('assistant', 'Network connection error. Please ensure you are online. (Ref: CS-API-001)');
    }
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    sendMessage(input.value);
  });

  // Suggestion chips
  document.querySelectorAll('.chat-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const prompt = chip.getAttribute('data-prompt');
      if (prompt) sendMessage(prompt);
    });
  });

  // Global helper accessible by 404/500 pages
  window.openAssistantWithPrompt = function (promptText) {
    toggleChat(true);
    if (promptText) {
      sendMessage(promptText);
    }
  };

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
})();
