export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',

  css: [
    '~/assets/css/handheld.css'
  ],

  runtimeConfig: {
    public: {
      apiBaseUrl: 'http://127.0.0.1:8000'
    }
  },

  devtools: {
    enabled: true
  }
})