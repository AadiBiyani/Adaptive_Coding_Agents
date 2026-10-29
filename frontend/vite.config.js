import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import tailwindcss from "@tailwindcss/vite"
import { fileURLToPath, URL } from "node:url"

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: { alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) } },
  build: { outDir: "../backend/src/adaptive_coding_agents/web", emptyOutDir: true },
  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8765",
        changeOrigin: true,
        configure(proxy) {
          proxy.on("proxyReq", (proxyReq, req) => {
            if (["http://127.0.0.1:5173", "http://localhost:5173"].includes(req.headers.origin)) {
              proxyReq.setHeader("Origin", "http://127.0.0.1:8765")
            }
          })
        },
      },
    },
  },
})
