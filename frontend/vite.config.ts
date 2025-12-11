import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig(({ mode }) => ({
  root: path.resolve(__dirname, 'src'),
  base: mode === 'production' ? '/static/dist/' : '/',

  build: {
    outDir: path.resolve(__dirname, '../app/static/dist'),
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'src/main.ts'),
        'government-question-writer': path.resolve(__dirname, 'src/pages/government-question-writer.ts'),
      },
    },
  },

  server: {
    port: 5173,
    strictPort: true,
    host: true, // Listen on all addresses (needed for Codespaces)
  },

  css: {
    devSourcemap: true,
    preprocessorOptions: {
      scss: {
        additionalData: `// Global SCSS imports can go here\n`
      }
    }
  },
}));
