<script setup lang="ts">
import { getMessage } from "@/utils/getMessage"
import IdlePopup from "@/components/IdlePopup.vue"
import { ref, computed, onMounted, onUnmounted, nextTick } from "vue"

const route = useRoute()
const router = useRouter()
const config = useRuntimeConfig()

const apiBaseUrl = config.public.apiBaseUrl

const code = route.query.code as string
const Fullname = ref("")
const passwordInput = ref<HTMLInputElement | null>(null)

const password = ref("")
const message = ref("")
const errorMessage = ref("")
const workerData = ref<{
  cd: string
  nm: string
  pw: string} | null>(null)

/* =========================
   IDLE TIMER
========================= */

const idleTime = 60
const idleCountdown = ref(0)
const showIdlePopup = ref(false)

let idleTimeout: ReturnType<typeof setTimeout> | null = null
let countdownInterval: ReturnType<typeof setInterval> | null = null

const resetIdleTimer = () => {
  if (idleTimeout) clearTimeout(idleTimeout)
  if (countdownInterval) clearInterval(countdownInterval)

  showIdlePopup.value = false
  idleCountdown.value = 0

  idleTimeout = setTimeout(startIdleWarning, idleTime * 1000)
}

const startIdleWarning = () => {
  showIdlePopup.value = true
  idleCountdown.value = idleTime

  countdownInterval = setInterval(() => {
    idleCountdown.value--

    if (idleCountdown.value <= 0) {
      clearInterval(countdownInterval!)
      countdownInterval = null

      router.push("/ht0010")
    }
  }, 1000)
}

const continueAfterIdle = () => {
  resetIdleTimer()
}

const handleIdleExit = () => {
  if (idleTimeout) clearTimeout(idleTimeout)
  if (countdownInterval) clearInterval(countdownInterval)

  router.push("/ht0010")
}

/* =========================
   NAVIGATION
========================= */

const handleBack = () => {
  router.back()
}

/* =========================
   PASSWORD CHECK
========================= */

const submitPassword = async () => {

  message.value = ""
  errorMessage.value = ""

  if (!password.value.trim()) {
    errorMessage.value = getMessage("E227")
    return
  }

  try {

    const response = await $fetch<{
      success: boolean
      fullname?: string
      message?: string
    }>(
      `${apiBaseUrl}/api/password/`,
      {
        method: "POST",
        body: {
          cd: code,
          password: password.value
        }
      }
    )

    if (response.success) {

      router.push({
        path: "/ht0020",
        query: {
          workerCode: code
        }
      })

    } else {

      errorMessage.value = getMessage("E204")

    }

  } catch {

    errorMessage.value = getMessage("E229")

  }
}
const fetchWorker = async () => {
  try {
    const data = await $fetch<any>(`${apiBaseUrl}/api/worker-info/`, {
      params: { cd: code }
    })

    console.log("🔥 RAW API RESPONSE:", data)
    console.log("🔥 CODE SENT:", code)

    if (data?.success) {

      const name = data.nm

      workerData.value = {
        cd: code,
        nm: name,
        pw: data.pw
      }

      Fullname.value = name

      console.log("✅ FULLNAME SET:", Fullname.value)
    }

  } catch (e) {
    console.error("worker fetch error", e)
  }
}
  const onKeyDown = (e: KeyboardEvent) => {
  console.log("KEY:", e.key, "CODE:", e.code)

  const isF1 = e.key === "F1" || e.code === "F1"
  const isF4 = e.key === "F4" || e.code === "F4"

  if (isF1) {
    e.preventDefault()
    handleBack()
  }

  if (isF4) {
    e.preventDefault()
    submitPassword()
  }
}
const statusLine = computed(() => {
  if (errorMessage.value) return errorMessage.value
  if (message.value) return message.value
  return "HT0011"
})
/* =========================
   LIFECYCLE
========================= */

onMounted(() => {

  window.addEventListener("keydown", onKeyDown, true)
  
  window.addEventListener("mousedown", resetIdleTimer)
  window.addEventListener("touchstart", resetIdleTimer)
  
  resetIdleTimer()

  fetchWorker()

  nextTick(() => {
    passwordInput.value?.focus()
  })
})

onUnmounted(() => {
 
  window.removeEventListener("keydown", onKeyDown, true)
  
  window.removeEventListener("mousedown", resetIdleTimer)
  window.removeEventListener("touchstart", resetIdleTimer)
  
  if (idleTimeout) clearTimeout(idleTimeout)
  if (countdownInterval) clearInterval(countdownInterval)
})
</script>

<template>

<div class="handheld-page">

  <div class="device">

    <header class="topbar">
      TYK出荷検品システム
    </header>

    <div class="title">
      パスワード入力
    </div>

    <div class="instruction">
  パスワードを入力します
</div>

<div class="staff-name">
  {{ Fullname }}
</div>

<div class="password-row">
  <label>パスワード</label>

  <input
    ref="passwordInput"
    v-model="password"
    type="password"
    maxlength="10"
    @keyup.enter="submitPassword"
  />
</div>

    <div class="password-buttons">

      <button
        class="btn-back"
        @click="handleBack"
      >
        F1 戻る
      </button>

      <button
        class="btn-next"
        @click="submitPassword"
      >
        F4 次へ
      </button>
    <IdlePopup
      :visible="showIdlePopup"
      :countdown="idleCountdown"
      @continue="continueAfterIdle"
    />
    </div>

   <footer
  class="footer"
  :class="{ 'footer-error': errorMessage || message }"
>
  {{ statusLine }}
</footer>

  </div>

</div>

</template>

<style scoped>

</style>