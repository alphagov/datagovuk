import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  // Point to our frontend asset directory
  root: resolve(__dirname, 'frontend'),

  server: {
    // Enable CORS so your python app on localhost:5050 can fetch assets from localhost:5173
    cors: true,
    strictPort: true,
    port: 5173,
    hmr: {
      host: 'localhost',
    },
  },
  build: {
    // Output directly to your Python application's static folder
    outDir: resolve(__dirname, 'app/static/dist'),
    emptyOutDir: true,

    // Disable asset hashing for simpler integration in the live build
    rollupOptions: {
      input: resolve(__dirname, 'frontend/main.js'),
      output: {
        entryFileNames: 'assets/bundle.js',
        assetFileNames: 'assets/bundle.[ext]',
      },
    },
  },
});
