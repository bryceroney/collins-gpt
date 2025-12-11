export type ToastType = 'info' | 'success' | 'warning' | 'danger';

export interface StreamChunk {
  chunk?: string;
  done?: boolean;
  question?: string;
  answer?: string;
  error?: string;
}

// Global functions for onclick handlers
declare global {
  interface Window {
    showToast(message: string, type?: ToastType): void;
    copyToClipboard(type: 'question' | 'answer'): void;
  }
}
