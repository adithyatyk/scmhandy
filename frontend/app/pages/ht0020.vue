<script setup lang="ts">
const router = useRouter()
const route = useRoute()
const errorMessage = ref("")

const code = (route.query.code as string) || ""
console.log("code:", code)

const handleExit = () => {
  router.push("/ht0010")
}

const handleHT0100 = () => {
  router.push({
        path: "/ht0100",
        query: {
          code: code
      }
      })
}

const handleHT0200 = () => {
  router.push({
        path: "/ht0200",
        query: {
          code:code
      }
      })
}

const handleHT0400 = () => {
  router.push({
        path: "/ht0400",
        query: {
          code: code,
          inventoryFlg: "完成品"
        }
      })
}

const handleHT0500 = () => {
  router.push({
        path: "/ht0500",
        query: {
          code: code,
          inventoryFlg: "立会い"
        }
      })
}

const handleHT0600 = () => {
  router.push({
        path: "/ht0600",
        query: {
          code: code
        }
      })
}

const handleHT0700 = () => {
  router.push({
        path: "/ht0700",
        query: {
          code: code
        }
      })
}

const handleHT0800 = () => {
  router.push({
        path: "/ht0800",
        query: {
          code: code
        }
      })
}

const handleHT0900 = () => {
  router.push({
        path: "/ht0900",
        query: {
          code: code
        }
      })
}

const handleHT1000 = () => {
  router.push({
        path: "/ht1000",
        query: {
          code: code
        }
      })
}

const handleHT1100 = () => {
  router.push({
        path: "/ht1100",
        query: {
          code: code
        }
      })
}

const onKeyDown = (e: KeyboardEvent) => {
  switch (e.key) {
    case "F1":
      e.preventDefault()
      handleExit()
      break

    case "1":
      e.preventDefault()
      handleHT0100()
      break

    case "2":
      e.preventDefault()
      handleHT0200()
      break

    case "3":
      e.preventDefault()
      handleHT0400()
      break

    case "4":
      e.preventDefault()
      handleHT0500()
      break

    case "5":
      e.preventDefault()
      handleHT0600()
      break

    case "6":
      e.preventDefault()
      handleHT0700()
      break

    case "7":
      e.preventDefault()
      handleHT0800()
      break

    case "8":
      e.preventDefault()
      handleHT0900()
      break

    case "9":
      e.preventDefault()
      handleHT1000()
      break

    case "0":
      e.preventDefault()
      handleHT1100()
      break
      
  }
}

onMounted(() => {
  if (import.meta.client) {
    window.addEventListener("keydown", onKeyDown)
  }
})

onUnmounted(() => {
  if (import.meta.client) {
    window.removeEventListener("keydown", onKeyDown)
  }
})
</script>

<template>
  <div class="handheld-page">
    <div class="device">

      <header class="topbar">
        TYK出荷検品システム
      </header>

      <div class="title">
        メニュー
      </div>

      <main class="body">
        <button
          class="menu-btn"
          @click="handleHT0100"
        >
          1. 外注品受入
        </button>

        <button 
          class="menu-btn"
          @click="handleHT0200"
        >
          2. 出荷前検品
        </button>

        <button 
          class="menu-btn"
          @click="handleHT0400"
        >
          3. 棚卸　完成品
        </button>

        <button
          class="menu-btn"
          @click="handleHT0500"
        >
          4. 棚卸　立会い
        </button>

        <button 
          class="menu-btn"
          @click="handleHT0600"
        >
          5. 外注品その他処理
        </button>

        <button 
          class="menu-btn"
          @click="handleHT0700"
        >
          6. 出荷取消
        </button>

        <button 
          class="menu-btn"
          @click="handleHT0800"
        >
          7. 納入先返品受入
        </button>

        <button 
          class="menu-btn"
          @click="handleHT0900"
        >
          8. 得意先返品
        </button>

        <button 
          class="menu-btn"
          @click="handleHT1000"
        >
          9. メーカー返品
        </button>

        <button 
          class="menu-btn"
          @click="handleHT1100"
        >
          10. 廃却
        </button>
      </main>

      <div class="password-buttons">
        <button
          class="btn-back"
          @click="handleExit"
        >
          F1 戻る
        </button>
      </div>
      
      <footer
        class="footer"
        :class="{ 'footer-error': errorMessage }"
      >
        {{ errorMessage || "HT0020" }}
      </footer>

    </div>
  </div>
</template>
