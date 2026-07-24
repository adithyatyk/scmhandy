<script setup lang="ts">
const router = useRouter()
const route = useRoute()
const errorMessage = ref("")
const messageCode = ref("")
const showConfirm = ref(false)

const code = (route.query.code as string) || ""

const handleBack = () => {
  router.push({
    path: "/ht0020",
    query: {
      code
    }
  })
}

const handleGoods = () => {
  router.push({
    path: "/ht0120",
    query: {
      code,
      inboundcanFlg: "入庫"
    }
  })
}

const handleResult = () => {
  router.push({
    path: "/ht0130",
    query: {
      code
    }
  })
}

const handleTransfer = () => {
  showConfirm.value = true
}

const executeTransfer = async () => {
  errorMessage.value = ""

  try {
    const config = useRuntimeConfig()
    const apiBaseUrl = config.public.apiBaseUrl

    const res = await fetch(`${apiBaseUrl}/api/ht0100/transfer/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        code,
      }),
    })

    const data = await res.json()

    messageCode.value = data.messageCode

    if (data.success) {
      errorMessage.value = getMessage(data.messageCode)
    } else {
      errorMessage.value = getMessage(data.messageCode)
    }
  } catch (err) {
    console.error(err)
    messageCode.value = "E103"
    errorMessage.value = getMessage("E103")
  }
}
const handleYes = () => {
  showConfirm.value = false
  executeTransfer()
}

const handleNo = () => {
  showConfirm.value = false
}

const handleCancel = () => {
  router.push({
    path: "/ht0120",
    query: {
      code,
      inboundcanFlg: "取消"
    }
  })
}

const onKeyDown = (e: KeyboardEvent) => {
  switch (e.key) {
    case "F1":
      e.preventDefault()
      handleBack()
      break

    case "1":
      e.preventDefault()
      handleGoods()
      break

    case "2":
      e.preventDefault()
      handleResult()
      break

    case "3":
      e.preventDefault()
      handleTransfer()
      break

    case "4":
      e.preventDefault()
      handleCancel()
      break
  }
}

onMounted(() => {
  window.addEventListener("keydown", onKeyDown)
})

onUnmounted(() => {
  window.removeEventListener("keydown", onKeyDown)
})
</script>
<template>

  <div class="handheld-page">
    <div class="device">

      <header class="topbar">
        TYK出荷検品システム
      </header>

      <div class="title">
        【外注品受入】メニュー
      </div>

      <main class="body">

        <button class="menu-btn" @click="handleGoods">
          1. 入庫
        </button>

        <button class="menu-btn" @click="handleResult">
          2. 入庫照合結果
        </button>

        <button class="menu-btn" @click="handleTransfer">
          3. 転送
        </button>

        <button class="menu-btn" @click="handleCancel">
          4. 入庫取消
        </button>

      </main>

      <div class="password-buttons">
        <button
          class="btn-back"
          @click="handleBack"
        >
          F1 戻る
        </button>
      </div>

      <footer
        class="footer"
        :class="{
          'footer-info': messageCode.startsWith('I'),
          'footer-error': messageCode.startsWith('E')
        }"
      >
        {{ errorMessage || "HT0100" }}
      </footer>

      <div v-if="showConfirm" class="confirm-overlay">
        <div class="confirm-box">
          <div class="confirm-message">
            {{ getMessage("Q201","受入") }}
          </div>

          <div class="confirm-buttons">
            <button @click="handleYes">はい</button>
            <button @click="handleNo">いいえ</button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>