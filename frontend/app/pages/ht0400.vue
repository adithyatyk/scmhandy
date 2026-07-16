<script setup lang="ts">
import { useRouter, useRoute } from "vue-router"
import { getMessage } from "@/utils/getMessage"
import { computed, ref, onMounted, onUnmounted } from "vue"

const router = useRouter()
const route = useRoute()

// Parameters
const code = (route.query.code as string) || ""
const inventoryFlag = (route.query.inventoryFlag as string) || ""

// Screen title
const title = computed(() =>
  inventoryFlag === "supervisor"
    ? "【棚卸 監督】メニュー"
    : "【棚卸 完成品】メニュー"
)

// Footer message
const lblMsg = ref("")
const lblMsgVisible = ref(false)
const lblMsgType = ref<"info" | "error">("info")

function showMsg(msg: string, type: "info" | "error" = "info") {
  lblMsg.value = msg
  lblMsgType.value = type
  lblMsgVisible.value = true
}

function clearMsg() {
  lblMsg.value = ""
  lblMsgVisible.value = false
}

// Confirmation popup
const showConfirm = ref(false)
const confirmMessage = ref("")

const isDeleting = ref(false)

// Button 1
const handleInput = () => {
  clearMsg()

  router.push({
    path: "/ht0410",
    query: {
      mode: "入力",
      code: code
    },
  })
}

// Button 2
const handleDelete = () => {
  clearMsg()

  router.push({
    path: "/ht0410",
    query: {
      mode: "削除",
      code: code
    },
  })
}

// Button 3
const handleDeleteTemp = () => {
  clearMsg()

  confirmMessage.value = getMessage("Q204", code)
  showConfirm.value = true
}

// Cancel
const handleCancel = () => {
  showConfirm.value = false
}

// OK
const handleOk = async () => {
  showConfirm.value = false
  isDeleting.value = true

  try {
    const config = useRuntimeConfig()
    const apiBaseUrl = config.public.apiBaseUrl

    const res = await fetch(`${apiBaseUrl}/api/ht0400/delete-temp/`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        code,
      }),
    })

    const data = await res.json()

    if (res.ok) {
      if (data.success) {
        showMsg(getMessage("I202"), "info")
      } else {
        showMsg(getMessage("I203"), "code")
      }
    } else {
      showMsg(getMessage("E225"), "error")
    }
  } catch (error) {
    console.error(error)
    showMsg(getMessage("E225"), "error")
  } finally {
    isDeleting.value = false
  }
}

const handleBack = () => {
  router.push({
    path: "/ht0020",
    query: {
      code,      
    },
  })
}
const handleKeyDown = (event: KeyboardEvent) => {
  switch (event.key) {
    case "F1":
      event.preventDefault()
      handleBack()
      break

    case "1":
      event.preventDefault()
      handleInput()
      break

    case "2":
      event.preventDefault()
      handleDelete()
      break

    case "3":
      event.preventDefault()
      handleDeleteTemp()
      break
  }
}

onMounted(() => {
  console.log(route.query)
  console.log("code =", code)
  console.log("inventoryFlag =", inventoryFlag)

  window.addEventListener("keydown", handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener("keydown", handleKeyDown)
})
</script>

<template>
  <div class="handheld-page">
    <div class="device">

      <!-- Header -->
      <header class="topbar">
        TYK出荷検品システム
      </header>

      <!-- Screen title -->
      <div class="title">
        {{ title }}
      </div>

      <!-- Menu -->
      <div class="body">

        <button
          class="menu-btn"
          @click="handleInput"
        >
          1.入力
        </button>

        <button
          class="menu-btn"
          @click="handleDelete"
        >
          2.削除
        </button>

        <button
          class="menu-btn"
          :disabled="isDeleting"
          @click="handleDeleteTemp"
        >
          3.一時保存データ削除
        </button>

      </div>

      <!-- F1 -->
      <div class="password-buttons">
        <button
          class="btn-back"
          @click="handleBack"
        >
          F1 戻る
        </button>
      </div>

      <!-- Confirmation Popup -->
      <div
        v-if="showConfirm"
        class="confirm-overlay"
      >
        <div class="confirm-box">

          <div class="confirm-message">
            {{ confirmMessage }}
          </div>

          <div class="confirm-buttons">
            <button @click="handleOk">
              オーケー
            </button>

            <button @click="handleCancel">
              取り消し
            </button>
          </div>

        </div>
      </div>

      <footer
        class="footer"
        :class="{ 'footer-error': lblMsgVisible }"
      >
        <span v-if="lblMsgVisible">
          {{ lblMsg }}
        </span>

        <span v-else>
          HT0400
        </span>
      </footer>
    </div>
  </div>
</template>