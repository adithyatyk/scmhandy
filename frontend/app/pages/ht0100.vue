<script setup lang="ts">
const router = useRouter()
const route = useRoute()
const errorMessage = ref("")

const code = (route.query.code as string) || ""

const handleBack = () => {
  router.push({
    path: "/ht0020",
    query: {
      code
    }
  })
}

const handleNyuko = () => {
  router.push({
    path: "/ht0120",
    query: {
      code
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
  router.push({
    path: "/ht0140",
    query: {
      code
    }
  })
}

const handleCancel = () => {
  router.push({
    path: "/ht0150",
    query: {
      code
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
      handleNyuko()
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

        <button class="menu-btn" @click="handleNyuko">
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
        :class="{ 'footer-error': errorMessage }"
      >
        {{ errorMessage || "HT0110" }}
      </footer>

    </div>
  </div>
</template>