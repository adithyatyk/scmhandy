<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from "vue"
import { getMessage } from "@/utils/getMessage"

type StaffRow = {
  cd: string
  nm: string
  dept?: string
}

const tableRef = ref<HTMLElement | null>(null)
const router = useRouter()

const title1 = ref("TYK出荷検品システム")
const title2 = ref("トップ　作業者選択")

const staffRows = ref<StaffRow[]>([])
const selectedCd = ref("")
const message = ref("")
const errorMessage = ref("")
const isLoading = ref(false)
const config = useRuntimeConfig()
const apiBaseUrl = config.public.apiBaseUrl

/* =========================
   COMPUTED
========================= */
const hasData = computed(() => staffRows.value.length > 0)

/* =========================
   LIFECYCLE
========================= */

onMounted(async () => {
  await loadStaff()

  if (import.meta.client) {
    window.addEventListener("keydown", onKeyDown, true)

  }
})

onUnmounted(() => {

    window.removeEventListener("keydown", onKeyDown, true)
  
})
/* =========================
   KEY EVENTS
========================= */

const onKeyDown = (e: KeyboardEvent) => {

  console.log("KEY:", e.key, "CODE:", e.code)

  if (e.code === "F1") {
    e.preventDefault()
    router.push("/ht0010")
  }

  if (e.code === "F4") {
    e.preventDefault()

    if (!hasData.value) return
    handleNext()
  }
}
/* =========================
   API
========================= */

const loadStaff = async () => {
  isLoading.value = true
  message.value = ""
  errorMessage.value = ""

  try {
    const data = await $fetch(`${apiBaseUrl}/api/form/`, {
      method: "GET",
      cache: "no-store"
    })

    console.log("HT0010 API RESPONSE:", data)

    staffRows.value = data.staff ?? []

    if (staffRows.value.length === 0) {
      errorMessage.value = getMessage("E212", "作業者")
      return
    }

    selectedCd.value = staffRows.value[0].cd

  } catch (err) {
    console.error("HT0010 ERROR:", err)
    errorMessage.value = getMessage("E212", "作業者")
  } finally {
    isLoading.value = false
  }
}

/* =========================
   NAVIGATION
========================= */

const handleNext = async () => {
  errorMessage.value = ""
  message.value = ""

  try {
    const selectedRow = staffRows.value.find(
      row => row.cd === selectedCd.value
    )

    if (!selectedRow) {
      errorMessage.value = getMessage("E211", "作業者")
      return
    }

    await router.push({
      path: "/ht0011",
      query: {
        code: selectedRow.cd      
      }
    })

  } catch (error) {
    console.error(error)
    errorMessage.value = getMessage("E225")
  }
}

</script>

<template>

<div class="handheld-page">

  <div class="device">

    <header class="topbar">
      TYK出荷検品システム
    </header>

    <div class="title">
      トップ　作業者選択
    </div>

    <main class="body">

      <label class="label">
        作業者を選択します
      </label>

      <div class="table-box">

        <table ref="tableRef" tabindex="0">
          <thead>
            <tr>
              <th>コード</th>
              <th>氏名</th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="row in staffRows"
              :key="row.cd"
              :class="{ selected: selectedCd === row.cd }"
              @click="selectedCd = row.cd"
            >
              <td>{{ row.cd }}</td>
              <td>{{ row.nm }}</td>
            </tr>
          </tbody>
        </table>

      </div>

    </main>

    <div class="worker-buttons">

  <button
    v-if="hasData"
    class="btn-next"
    @click="handleNext"
  >
    F4 次へ
  </button>

</div>

  <footer
    class="footer"
    :class="{ 'footer-error': errorMessage }"
  >
    {{ errorMessage || 'HT0010' }}
  </footer>

  </div>

</div>

</template>

<style scoped>

</style>