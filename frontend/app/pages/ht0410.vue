<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onUnmounted } from "vue"
import { getMessage } from "@/utils/getMessage"

const router = useRouter()
const route = useRoute()
const config = useRuntimeConfig()

const apiBaseUrl = config.public.apiBaseUrl
const taciaiflg = (route.query.taciaiflg as string) || "0"

/* =========================
   PARAMETERS
========================= */

const code = (route.query.code as string) || ""
const inventoryFlag = (route.query.inventoryFlag as string) || ""
const mode = (route.query.mode as string) || "Input"
console.log("Route Query:", route.query)
console.log("code:", code)


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
    ? "【棚卸 完成品】削除"
    : "【棚卸 完成品】読取"

})

/* =========================
   REFS
========================= */

const tableRef = ref<HTMLElement | null>(null)
const qrInput = ref<HTMLInputElement | null>(null)

/* =========================
   VARIABLES
========================= */

type WarehouseRow = {
  code: string
  name: string
}

const warehouseRows = ref<WarehouseRow[]>([])
const selectedWarehouseCode = ref("")
const selectedWarehouseName = ref("")

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

      code: code,

      inventoryFlag: "立会い",
      taciaiflg

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

  tableRef.value?.focus()

}

const handleClear = () => {

  qrCode.value = ""

  detailList.value = []

  errorMessage.value = ""

  message.value = ""

  nextTick(() => {
    tableRef.value?.focus()
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

  // 1. Load Warehouse Master
  await loadWarehouse()

  // 3. Get number of pages read
  await loadCount()

  // 4. Get Sequential Number
  await loadSerial()

  //await loadDetailList()
  await loadDetailList()

  nextTick(() => {
    tableRef.value?.focus()
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
      code?: string
      message?: string
    }>(
      `${apiBaseUrl}/api/ht0410/warehouse/`
    )

    if (response.success) {

    warehouseRows.value = response.rows

    if (warehouseRows.value.length > 0) {

        selectedWarehouseCode.value = warehouseRows.value[0].code
        selectedWarehouseName.value = warehouseRows.value[0].name

    } else {

        errorMessage.value = getMessage("E212", "倉庫名")

    }

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
      code?: string
    }>(
      `${apiBaseUrl}/api/ht0410/count/`,
      {
        method: "POST",

        body: {

          code,
          warehouseCode: selectedWarehouseCode.value,
          mode,
          taciaiflg

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
          mode,
          taciaiflg

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

const selectWarehouse = async (row: WarehouseRow) => {

  selectedWarehouseCode.value = row.code
  selectedWarehouseName.value = row.name

  qrCode.value = ""

  detailList.value = []

  errorMessage.value = ""

  await loadCount()

  await loadSerial()

  await loadDetailList()

  nextTick(() => {
    qrInput.value?.focus()
  })

}

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
          mode,
          taciaiflg

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

  console.log("ENTER PRESSED")
  console.log("QR:", qrCode.value)

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
    code?: string
    }>(
        `${apiBaseUrl}/api/ht0410/scan/`,
        {
            method: "POST",
            body: {
                code,
                warehouseCode: selectedWarehouseCode.value,
                qrCode: qrCode.value,
                mode,
                taciaiflg
            }
        }
    )

    if (response.success) {

      qrCode.value = ""

      await loadCount()

      await loadSerial()

      await loadDetailList()

      nextTick(() => {

        qrInput.value?.focus()

      })

    }
    else {

      if (response.code) {
        errorMessage.value = getMessage(response.code)
      }

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
        <div
  ref="tableRef"
  class="list-box warehouse-box"
  tabindex="0"
>
  <table>

    <thead>
      <tr>
        <th>倉庫名</th>
      </tr>
    </thead>

    <tbody>
      <tr
        v-for="row in warehouseRows"
        :key="row.code"
        :class="{ selected: selectedWarehouseCode === row.code }"
        @click="selectWarehouse(row)"
      >
        <td>{{ row.name }}</td>
      </tr>
    </tbody>

  </table>
</div>
        <div class="qr-message-row">

          <button
            v-if="mode === '削除'"
            class="cancel-btn"
          >
            取消
          </button>
          
          <div
            v-else
            class="cancel-placeholder"
          ></div>
          <div class="qr-label">
            QRをスキャンして下さい
          </div>

        </div>

        <!-- Scan -->
        <div class="scan-row">          

          <input
            ref="qrInput"
            v-model="qrCode"
            class="scan-input"
            @keyup.enter="handleEnter"
          >

        </div>

        <!-- Warehouse -->
        <div class="info-row">

          <span class="label1">倉庫</span>
          <span class="colon">：</span>
          <span class="value1">{{ selectedWarehouseName }}</span>

        </div>

        <!-- Count -->
        <div class="count-row">

          <span class="label2">読取枚数</span>
          <span class="colon">：</span>
          <span class="value2">{{ readCount }}</span>

          <span class="label3">連番</span>
          <span class="colon">：</span>
          <span class="value3">{{ serialNo }}</span>

        </div>

        <!-- Table -->
        <div class="material-box">

          <table>

            <thead>

              <tr>

                <th style="width:10%">
                  材質
                </th>

                <th style="width:10%">
                  符号
                </th>

                <th style="width:10%">
                  数量
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
        :class="errorMessage ? 'footer footer-error' : 'footer footer-normal'"
      >
        {{ statusLine }}
      </footer>

    </div>
  </div>
</template>