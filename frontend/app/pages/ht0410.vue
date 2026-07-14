<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from "vue"
import { getMessage } from "@/utils/getMessage"

const router = useRouter()
const route = useRoute()
const config = useRuntimeConfig()

const apiBaseUrl = config.public.apiBaseUrl

/* =========================
   PARAMETERS
========================= */

const code = (route.query.code as string) || ""
const inventoryFlag = (route.query.inventoryFlag as string) || ""
const mode = (route.query.mode as string) || "Input"

/* =========================
   SCREEN TITLE
========================= */

const title = computed(() => {

  if (inventoryFlag === "completed") {

    return mode === "Delete"
      ? "【棚卸 完成品】削除"
      : "【棚卸 完成品】読取"

  }

  return mode === "Delete"
    ? "【棚卸】削除"
    : "【棚卸】読取"

})

/* =========================
   REFS
========================= */

const warehouseRef = ref<HTMLSelectElement | null>(null)
const qrInput = ref<HTMLInputElement | null>(null)

/* =========================
   VARIABLES
========================= */

const warehouseList = ref<
{
  code: string
  name: string
}[]
>([])

const selectedWarehouse = ref("")
const selectedWarehouseCode = ref("")

const qrCode = ref("")

const readCount = ref(0)
const serialNo = ref(0)

const detailList = ref<any[]>([])

const message = ref("")
const errorMessage = ref("")

const loading = ref(false)

/* =========================
   STATUS LINE
========================= */

const statusLine = computed(() => {

  if (errorMessage.value)
    return errorMessage.value

  if (message.value)
    return message.value

  return "HT0410"

})

/* =========================
   BUTTONS
========================= */

const handleBack = () => {

  router.push({

    path: "/ht0400",

    query: {

      code,

      inventoryFlag

    }

  })

}

const handleQR = () => {

  qrCode.value = ""

  nextTick(() => {

    qrInput.value?.focus()

  })

}

const handleList = () => {

  warehouseRef.value?.focus()

}

const handleClear = () => {

  qrCode.value = ""

  detailList.value = []

  errorMessage.value = ""

  message.value = ""

  nextTick(() => {

    qrInput.value?.focus()

  })

}

/* =========================
   KEYBOARD
========================= */

const onKeyDown = (e: KeyboardEvent) => {

  const isF1 = e.key === "F1" || e.code === "F1"
  const isF2 = e.key === "F2" || e.code === "F2"
  const isF3 = e.key === "F3" || e.code === "F3"
  const isF4 = e.key === "F4" || e.code === "F4"

  if (isF1) {

    e.preventDefault()

    handleBack()

  }

  if (isF2) {

    e.preventDefault()

    handleQR()

  }

  if (isF3) {

    e.preventDefault()

    handleList()

  }

  if (isF4) {

    e.preventDefault()

    handleClear()

  }

}

/* =========================
   LIFECYCLE
========================= */

onMounted(async () => {

  window.addEventListener("keydown", onKeyDown, true)

  await loadWarehouse()

  await loadCount()

  await loadSerial()

  await loadDetailList()

  nextTick(() => {
    qrInput.value?.focus()
  })

})

onUnmounted(() => {

  window.removeEventListener("keydown", onKeyDown, true)

})

/* =========================
   LOAD WAREHOUSE
========================= */

const loadWarehouse = async () => {

  loading.value = true

  errorMessage.value = ""

  try {

    const response = await $fetch<{
      success: boolean
      rows: {
        code: string
        name: string
      }[]
    }>(
      `${apiBaseUrl}/api/ht0410/warehouse/`
    )

    if (response.success) {

      warehouseList.value = response.rows

      if (warehouseList.value.length > 0) {

        selectedWarehouse.value = warehouseList.value[0].name

        selectedWarehouseCode.value = warehouseList.value[0].code

      }

    }
    else {

      errorMessage.value = getMessage("E203")

    }

  }
  catch {

    errorMessage.value = getMessage("E229")

  }

  loading.value = false

}

/* =========================
   LOAD READ COUNT
========================= */

const loadCount = async () => {

  try {

    const response = await $fetch<{
      success: boolean
      count: number
    }>(
      `${apiBaseUrl}/api/ht0410/count/`,
      {
        method: "POST",

        body: {

          code,

          warehouseCode: selectedWarehouseCode.value,

          mode

        }

      }
    )

    if (response.success) {

      readCount.value = response.count

    }

  }
  catch {

    readCount.value = 0

  }

}

/* =========================
   LOAD SERIAL
========================= */

const loadSerial = async () => {

  try {

    const response = await $fetch<{
      success: boolean
      serial: number
    }>(
      `${apiBaseUrl}/api/ht0410/serial/`,
      {
        method: "POST",

        body: {

          code,

          warehouseCode: selectedWarehouseCode.value,

          mode

        }

      }
    )

    if (response.success) {

      serialNo.value = response.serial

    }

  }
  catch {

    serialNo.value = 0

  }

}
/* =========================
   WAREHOUSE CHANGED
========================= */

watch(selectedWarehouse, async (value) => {

  const item = warehouseList.value.find(
    x => x.name === value
  )

  if (!item)
    return

  selectedWarehouseCode.value = item.code

  qrCode.value = ""

  detailList.value = []

  errorMessage.value = ""

  await loadCount()

  await loadSerial()

  nextTick(() => {

    qrInput.value?.focus()

  })

})

/* =========================
   LOAD DETAIL LIST
========================= */

const loadDetailList = async () => {

  try {

    const response = await $fetch<{
      success: boolean
      rows: any[]
    }>(
      `${apiBaseUrl}/api/ht0410/list/`,
      {
        method: "POST",

        body: {

          code,

          warehouseCode: selectedWarehouseCode.value,

          mode

        }

      }
    )

    if (response.success) {

      detailList.value = response.rows

    }

  }
  catch {

    detailList.value = []

  }

}

/* =========================
   QR SCAN
========================= */

const handleEnter = async () => {

  errorMessage.value = ""

  message.value = ""

  if (selectedWarehouseCode.value === "") {

    errorMessage.value = getMessage("E212")

    return

  }

  if (qrCode.value.trim() === "") {

    errorMessage.value = getMessage("E227")

    return

  }

  loading.value = true

  try {

    const response = await $fetch<{
      success: boolean
      message: string
    }>(
      `${apiBaseUrl}/api/ht0410/scan/`,
      {
        method: "POST",

        body: {

          code,

          inventoryFlag,

          warehouseCode: selectedWarehouseCode.value,

          qrCode: qrCode.value,

          mode

        }

      }
    )

    if (response.success) {

      qrCode.value = ""

      await loadCount()

      await loadSerial()

      await loadDetailList()

      message.value = response.message

      nextTick(() => {

        qrInput.value?.focus()

      })

    }
    else {

      errorMessage.value = response.message

      nextTick(() => {

        qrInput.value?.focus()

      })

    }

  }
  catch {

    errorMessage.value = getMessage("E229")

  }

  loading.value = false

}
</script>   
<template>
  <div class="handheld-page">
    <div class="device">

      <!-- Header -->
      <header class="topbar">
        TYK出荷検品システム
      </header>

      <!-- Title -->
      <div class="title">
        {{ title }}
      </div>

      <div class="ht0410-container">

        <!-- Warehouse -->
        <div class="warehouse-block">

          <div class="warehouse-title">
            倉庫名
          </div>

          <select
            ref="warehouseRef"
            v-model="selectedWarehouse"
            class="warehouse-select"
            size="8"
          >
            <option
              v-for="item in warehouseList"
              :key="item.code"
              :value="item.name"
            >
              {{ item.name }}
            </option>
          </select>

        </div>

        <!-- Scan -->
        <div class="scan-row">

          <button
            class="cancel-btn"
            v-if="mode==='Delete'"
          >
            cancel
          </button>

          <input
            ref="qrInput"
            v-model="qrCode"
            class="scan-input"
            placeholder="Please scan the QR code."
            @keyup.enter="handleEnter"
          >

        </div>

        <!-- Warehouse -->
        <div class="info-row">

          <span class="label1">
            warehouse
          </span>

          <span class="value1">
            {{ selectedWarehouse }}
          </span>

        </div>

        <!-- Count -->
        <div class="count-row">

          <span class="label2">
            Number of paper
          </span>

          <span class="value2">
            {{ readCount }}
          </span>

          <span class="label3">
            Sequential
          </span>

          <span class="value3">
            {{ serialNo }}
          </span>

        </div>

        <!-- Table -->
        <div class="table-box">

          <table>

            <thead>

              <tr>

                <th style="width:40%">
                  Material
                </th>

                <th style="width:10%">
                  sign
                </th>

                <th style="width:10%">
                  quantity
                </th>

              </tr>

            </thead>

            <tbody>

              <tr
                v-for="(row,index) in detailList"
                :key="index"
              >
                <td>{{ row.material }}</td>
                <td>{{ row.symbol }}</td>
                <td style="text-align:right">
                  {{ row.qty }}
                </td>
              </tr>

            </tbody>

          </table>

        </div>

      </div>

      <!-- Buttons -->
      <div class="ht0410-buttons">

        <button
          class="btn-back"
          @click="handleBack"
        >
          F1 戻る
        </button>

        <button
          class="btn-blue"
          @click="handleQR"
        >
          F2 QRへ
        </button>

        <button
          class="btn-green"
          @click="handleList"
        >
          F3 ﾘｽﾄへ
        </button>

        <button
          class="btn-next"
          @click="handleClear"
        >
          F4 クリア
        </button>

      </div>

      <!-- Error -->
      <footer
        class="footer footer-error"
      >
        {{ statusLine }}
      </footer>

    </div>
  </div>
</template>