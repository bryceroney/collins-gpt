import type { StreamChunk } from '../types/app';
import { showToast } from '../modules/toast';

class GovernmentQuestionWriter {
  private form: HTMLFormElement;
  private submitBtn: HTMLButtonElement;
  private btnText: HTMLElement;
  private btnLoading: HTMLElement;
  private emptyState: HTMLElement;
  private loadingState: HTMLElement;
  private resultState: HTMLElement;
  private streamOutput: HTMLElement;
  private cursor: HTMLElement;
  private errorAlert: HTMLElement;
  private errorMessage: HTMLElement;
  private wordCountSlider: HTMLInputElement;
  private wordCountValue: HTMLElement;
  private csrfToken: string | null;

  constructor() {
    // Get DOM elements
    this.form = document.getElementById('government-question-form') as HTMLFormElement;
    this.submitBtn = document.getElementById('submit-btn') as HTMLButtonElement;
    this.btnText = document.getElementById('btn-text') as HTMLElement;
    this.btnLoading = document.getElementById('btn-loading') as HTMLElement;
    this.emptyState = document.getElementById('empty-state') as HTMLElement;
    this.loadingState = document.getElementById('loading-state') as HTMLElement;
    this.resultState = document.getElementById('result-state') as HTMLElement;
    this.streamOutput = document.getElementById('stream-output') as HTMLElement;
    this.cursor = document.getElementById('cursor') as HTMLElement;
    this.errorAlert = document.getElementById('error-alert') as HTMLElement;
    this.errorMessage = document.getElementById('error-message') as HTMLElement;
    this.wordCountSlider = document.getElementById('word_count') as HTMLInputElement;
    this.wordCountValue = document.getElementById('word-count-value') as HTMLElement;

    const csrfInput = document.querySelector<HTMLInputElement>('input[name="csrf_token"]');
    this.csrfToken = csrfInput?.value || null;

    this.init();
  }

  private init(): void {
    // Initialize slider display
    if (this.wordCountValue && this.wordCountSlider) {
      this.wordCountValue.textContent = this.wordCountSlider.value;
    }

    // Event listeners
    this.wordCountSlider.addEventListener('input', (e) => {
      this.wordCountValue.textContent = (e.target as HTMLInputElement).value;
    });

    // Cursor blink animation
    setInterval(() => {
      if (this.cursor) {
        this.cursor.style.opacity = this.cursor.style.opacity === '0' ? '1' : '0';
      }
    }, 530);

    this.form.addEventListener('submit', (e) => this.handleSubmit(e));
  }

  private clearFieldErrors(): void {
    const invalids = document.querySelectorAll('.is-invalid');
    invalids.forEach(el => el.classList.remove('is-invalid'));
    const feedbacks = document.querySelectorAll('.invalid-feedback.js-field-error');
    feedbacks.forEach(f => f.remove());
  }

  private showFieldErrors(errors: Record<string, string>): void {
    this.clearFieldErrors();
    for (const [field, msg] of Object.entries(errors)) {
      const el = document.querySelector<HTMLElement>(`[name="${field}"]`);
      if (el) {
        el.classList.add('is-invalid');
        const fb = document.createElement('div');
        fb.className = 'invalid-feedback js-field-error d-block';
        fb.textContent = msg;
        el.parentNode?.appendChild(fb);
      }
    }
  }

  private showError(message: string): void {
    // Parse field-specific errors
    if (message && message.includes(':')) {
      const parts = message.split(';').map(p => p.trim()).filter(Boolean);
      const errors: Record<string, string> = {};
      parts.forEach(part => {
        const [key, ...rest] = part.split(':');
        if (key && rest.length) {
          errors[key.trim()] = rest.join(':').trim();
        }
      });
      if (Object.keys(errors).length) {
        this.showFieldErrors(errors);
        return;
      }
    }

    this.errorMessage.textContent = message;
    this.errorAlert.classList.remove('d-none');
  }

  private hideError(): void {
    this.errorAlert.classList.add('d-none');
  }

  private setLoading(isLoading: boolean): void {
    if (isLoading) {
      this.btnText.classList.add('d-none');
      this.btnLoading.classList.remove('d-none');
      this.submitBtn.disabled = true;
      this.emptyState.classList.add('d-none');
      this.resultState.classList.add('d-none');
      this.loadingState.classList.remove('d-none');
      this.streamOutput.textContent = '';
      this.cursor.classList.remove('d-none');
    } else {
      this.btnText.classList.remove('d-none');
      this.btnLoading.classList.add('d-none');
      this.submitBtn.disabled = false;
      this.cursor.classList.add('d-none');
    }
  }

  private countWords(text: string): number {
    return text.trim().split(/\s+/).filter(word => word.length > 0).length;
  }

  private showResult(question: string, answer: string): void {
    this.loadingState.classList.add('d-none');
    this.resultState.classList.remove('d-none');

    const questionText = document.getElementById('question-text') as HTMLElement;
    const answerText = document.getElementById('answer-text') as HTMLElement;
    const answerWordCount = document.getElementById('answer-word-count') as HTMLElement;

    questionText.textContent = question;
    answerText.textContent = answer;
    answerWordCount.textContent = this.countWords(answer).toString();
  }

  private async handleSubmit(e: Event): Promise<void> {
    e.preventDefault();
    this.hideError();
    this.setLoading(true);

    const formData = {
      word_count: parseInt((document.getElementById('word_count') as HTMLInputElement).value),
      topic: (document.getElementById('topic') as HTMLInputElement).value,
      other_instructions: (document.getElementById('other_instructions') as HTMLTextAreaElement).value,
      strategy: (document.getElementById('strategy') as HTMLSelectElement).value,
      model: (document.getElementById('model') as HTMLSelectElement).value,
    };

    try {
      const response = await fetch('/government-question-writer/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(this.csrfToken && { 'X-CSRFToken': this.csrfToken }),
        },
        body: JSON.stringify(formData),
      });

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data: StreamChunk = JSON.parse(line.slice(6));

              if (data.error) {
                this.setLoading(false);
                this.emptyState.classList.remove('d-none');
                this.loadingState.classList.add('d-none');
                this.showError(data.error);
                return;
              }

              if (data.chunk) {
                this.streamOutput.textContent += data.chunk;
                this.streamOutput.scrollTop = this.streamOutput.scrollHeight;
              }

              if (data.done && data.question && data.answer) {
                this.setLoading(false);
                this.showResult(data.question, data.answer);
              }
            } catch (parseError) {
              console.error('Parse error:', parseError);
            }
          }
        }
      }
    } catch (error) {
      this.setLoading(false);
      this.emptyState.classList.remove('d-none');
      this.loadingState.classList.add('d-none');
      this.showError(`Network error: ${(error as Error).message}`);
    }
  }
}

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
  new GovernmentQuestionWriter();
});

// Export copyToClipboard globally for onclick handlers
export function copyToClipboard(type: 'question' | 'answer'): void {
  const textElement = document.getElementById(
    type === 'question' ? 'question-text' : 'answer-text'
  ) as HTMLElement;
  const text = textElement.innerText;

  navigator.clipboard.writeText(text).then(
    () => showToast('Copied to clipboard!', 'success'),
    () => showToast('Failed to copy text', 'danger')
  );
}

window.copyToClipboard = copyToClipboard;
