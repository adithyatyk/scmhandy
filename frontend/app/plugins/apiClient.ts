export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()

  console.log('API Base URL:', config.public.apiBaseUrl)

  const api = $fetch.create({
    baseURL: config.public.apiBaseUrl
  })

  return {
    provide: {
      api
    }
  }
})