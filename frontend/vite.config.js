import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";

export default defineConfig({
  plugins: [svelte()],
  build: {
    // single self-contained file so app.py can embed it with components.html()
    rollupOptions: { output: { inlineDynamicImports: true } },
  },
});
