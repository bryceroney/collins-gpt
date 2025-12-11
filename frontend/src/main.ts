import './styles/custom.scss';
import { initializeBootstrap } from './modules/bootstrap-init';
import { initializeSmoothScroll } from './modules/smooth-scroll';
import { initializeAnimations } from './modules/animations';
import { showToast } from './modules/toast';

// Expose globally for onclick handlers
window.showToast = showToast;

document.addEventListener('DOMContentLoaded', () => {
  initializeBootstrap();
  initializeSmoothScroll();
  initializeAnimations();
  console.log('CollinsGPT initialized successfully!');
});
