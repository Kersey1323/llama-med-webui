<template>
  <section
    class="bg-white panel annotation-summary rounded-xl border border-zinc-200 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-150"
  >
    <el-button
      @click="$router.push('/batch-process')"
      class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
      ><el-icon><ArrowLeft /></el-icon>&nbsp;返回质控</el-button
    >
    <span class="welcome-icon"><EditPen /></span>
    <div>
      <h2>标注对应关系</h2>
      <p class="tiny muted" style="margin-top: 7px">
        {{
          selectedJob
            ? `任务 #${selectedJob.id} · ${selectedJob.name}`
            : "请先选择一个质控任务"
        }}
      </p>
    </div>
    <el-select
      aria-label="选择标注任务"
      v-model="jobId"
      placeholder="选择任务"
      style="width: 200px"
      :disabled="dirty || loading || saving"
      @change="loadRecords"
      class="bg-zinc-100 border-0 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/30 transition-colors duration-150"
      ><el-option
        v-for="job in studio.jobs"
        :key="job.id"
        :label="`#${job.id} ${job.name}`"
        :value="job.id" /></el-select
    ><el-progress
      aria-label="报告标注完成进度"
      :percentage="percentage"
      :stroke-width="6"
    /><span class="tiny muted"
      >{{ records.filter((r) => r.annotated).length }} /
      {{ records.length }}</span
    ><el-button
      size="small"
      :disabled="!jobId"
      @click="download"
      class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
      >导出标注</el-button
    >
  </section>
  <div v-if="errorMessage" class="notice offline-notice" role="alert">
    <el-icon><Warning /></el-icon><span>{{ errorMessage }}</span
    ><button
      @click="loadRecords"
      class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
    >
      重新加载
    </button>
  </div>
  <div class="annotation-grid" v-loading="loading">
    <section
      class="bg-white panel rounded-xl border border-zinc-200 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-150"
    >
      <div class="panel-head">
        <h2>异常记录</h2>
        <span class="count-pill">{{ records.length }} 条</span>
      </div>
      <div class="annotation-queue">
        <button
          v-for="record in records"
          :key="record.id"
          class="rounded-lg text-sm font-medium transition-colors queue-item px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
          :class="{ active: current?.id === record.id }"
          @click="selectRecord(record)"
        >
          <header>
            <span>第 {{ record.row }} 行</span
            ><span
              :style="{ color: record.annotated ? '#047857' : '#52525b' }"
              >{{ record.annotated ? "已标注" : "待标注" }}</span
            >
          </header>
          <p>{{ record.type }}</p>
          <small>{{ record.original_diagnosis }}</small>
        </button>
        <div class="empty-inline" v-if="!records.length">
          暂无可标注记录<br />请先在批量质控中选择任务
        </div>
      </div>
    </section>
    <section
      class="bg-white panel annotation-paper rounded-xl border border-zinc-200 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-150"
    >
      <div class="panel-head">
        <div>
          <h2>影像描述</h2>
          <p>{{ description.length }} 个片段 · 点击选择</p>
        </div>
        <div class="color-palette" aria-label="标注颜色">
          <button
            v-for="(color, i) in palette"
            :key="color"
            :style="{ background: color }"
            :class="{ active: colorIndex === i }"
            :aria-label="`标注颜色 ${i + 1}`"
            @click="colorIndex = i"
            class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
          ></button>
        </div>
      </div>
      <div v-if="current" class="annotation-text">
        <button
          v-for="(text, i) in description"
          :key="i"
          :class="{ selected: selectedDescription.includes(i) }"
          :style="styleFor('description', i)"
          :aria-pressed="selectedDescription.includes(i)"
          @click="toggle('description', i)"
          class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
        >
          {{ text }}
        </button>
      </div>
      <div v-else class="annotation-empty">
        <el-icon><Document /></el-icon>从左侧选择一条异常记录
      </div>
    </section>
    <section
      class="bg-white panel annotation-paper rounded-xl border border-zinc-200 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-150"
    >
      <div class="panel-head">
        <div>
          <h2>影像诊断</h2>
          <p>{{ diagnosis.length }} 个片段 · 点击选择</p>
        </div>
        <span class="count-pill">原始诊断</span>
      </div>
      <div v-if="current" class="annotation-text">
        <button
          v-for="(text, i) in diagnosis"
          :key="i"
          :class="{ selected: selectedDiagnosis.includes(i) }"
          :style="styleFor('diagnosis', i)"
          :aria-pressed="selectedDiagnosis.includes(i)"
          @click="toggle('diagnosis', i)"
          class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
        >
          {{ text }}
        </button>
      </div>
      <div v-else class="annotation-empty">
        <el-icon><Connection /></el-icon>选择对应的描述与诊断片段
      </div>
    </section>
  </div>
  <div
    class="bg-white panel annotation-toolbar rounded-xl border border-zinc-200 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-150"
  >
    <span class="tiny muted">{{
      dirty ? "有未保存的修改" : "先在两侧选择对应片段，再确认标注组"
    }}</span>
    <div>
      <el-button
        :disabled="!current"
        @click="clearSelection"
        class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
        >清除选择</el-button
      ><el-button
        type="primary"
        plain
        :disabled="!selectedDescription.length || !selectedDiagnosis.length"
        @click="addGroup"
        class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
        >确认当前标注组</el-button
      ><el-button
        type="success"
        :loading="saving"
        :disabled="!current"
        @click="save"
        class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
        >保存当前标注</el-button
      ><el-button
        class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
        :disabled="!current || currentIndex >= records.length - 1"
        @click="next"
        >下一个 →</el-button
      >
    </div>
  </div>
  <section
    class="bg-white panel rounded-xl border border-zinc-200 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-150"
  >
    <div class="panel-head">
      <div>
        <h2>
          当前记录的标注组
          <span class="count-pill">{{ groups.length }} 组</span>
        </h2>
        <p>
          {{
            studio.demo
              ? "示例标注仅在本次页面会话内保留，可导出 JSON 查看"
              : "确认保存后写入任务记录，可随时导出归档"
          }}
        </p>
      </div>
      <el-button
        size="small"
        :disabled="!current || !current.annotated"
        @click="reset"
        class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
        >撤销已保存标注</el-button
      >
    </div>
    <el-table :data="groups" empty-text="还没有标注组，选择两侧片段后点击确认"
      ><el-table-column
        prop="descriptionText"
        label="描述片段"
        min-width="250"
      /><el-table-column
        prop="diagnosisText"
        label="诊断片段"
        min-width="250"
      /><el-table-column label="关联颜色" width="100"
        ><template #default="{ row }"
          ><span
            class="color-swatch"
            :style="{ background: row.color }"
          ></span></template></el-table-column
      ><el-table-column label="操作" width="85"
        ><template #default="{ $index }"
          ><el-button
            link
            type="danger"
            @click="
              groups.splice($index, 1);
              dirty = true;
            "
            class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
            >删除</el-button
          ></template
        ></el-table-column
      ></el-table
    >
  </section>
</template>
<script setup>
import { ref, computed, watch, onBeforeUnmount } from "vue";
import { useRoute, onBeforeRouteLeave } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  studio,
  getErrors,
  getGroups,
  saveGroups,
  resetGroups,
  exportJob,
} from "./store";
const route = useRoute();
const jobId = ref(null),
  records = ref([]),
  current = ref(null),
  groups = ref([]),
  loading = ref(false),
  saving = ref(false),
  dirty = ref(false),
  errorMessage = ref("");
const selectedDescription = ref([]),
  selectedDiagnosis = ref([]),
  colorIndex = ref(0);
const palette = [
  "#fce6a6",
  "#f5c0c9",
  "#c7deff",
  "#bae3d1",
  "#ddccf5",
  "#f8d4b5",
];
let version = 0,
  active = true;
const selectedJob = computed(() =>
  studio.jobs.find((j) => j.id === jobId.value),
);
const currentIndex = computed(() =>
  records.value.findIndex((r) => r.id === current.value?.id),
);
const percentage = computed(() =>
  records.value.length
    ? Math.round(
        (records.value.filter((r) => r.annotated).length /
          records.value.length) *
          100,
      )
    : 0,
);
// Preserve delimiters so group indices remain compatible with the original punctuation-based annotation format.
const split = (text) =>
  (text || "").split(/[,，;；.。!！?？]/).filter((p) => p.trim());
const description = computed(() => split(current.value?.originalText)),
  diagnosis = computed(() => split(current.value?.original_diagnosis));
watch(
  () => [studio.demo, studio.jobs],
  () => {
    if (!studio.jobs.length) {
      version++;
      jobId.value = null;
      current.value = null;
      records.value = [];
      groups.value = [];
      dirty.value = false;
      return;
    }
    const target = Number(route.query.jobId);
    jobId.value =
      studio.jobs.find((j) => j.id === target)?.id ||
      studio.jobs.find((j) => j.id === jobId.value)?.id ||
      studio.jobs[0].id;
    loadRecords();
  },
  { immediate: true },
);
async function loadRecords() {
  const seq = ++version;
  records.value = [];
  current.value = null;
  groups.value = [];
  dirty.value = false;
  errorMessage.value = "";
  if (!jobId.value) return;
  loading.value = true;
  try {
    let page = 1,
      rows = [],
      result;
    do {
      result = await getErrors(jobId.value, page++, 1000);
      rows.push(...result.data);
      if (seq !== version || !active) return;
    } while (result.data.length && rows.length < result.total);
    records.value = rows;
    if (rows.length)
      await selectRecord(rows.find((r) => !r.annotated) || rows[0]);
  } catch {
    if (seq === version) errorMessage.value = "记录或标注加载失败，请重试。";
  } finally {
    if (seq === version) loading.value = false;
  }
}
async function allowDiscard() {
  if (
    !dirty.value &&
    !selectedDescription.value.length &&
    !selectedDiagnosis.value.length
  )
    return true;
  try {
    await ElMessageBox.confirm(
      "当前记录有未保存内容，确定离开并放弃这些修改吗？",
      "未保存的标注",
      {
        confirmButtonText: "放弃修改",
        cancelButtonText: "继续编辑",
        type: "warning",
      },
    );
    return true;
  } catch {
    return false;
  }
}
async function selectRecord(record) {
  if (saving.value || !(await allowDiscard())) return;
  const seq = ++version;
  loading.value = true;
  errorMessage.value = "";
  try {
    const loaded = await getGroups(record.id);
    if (seq !== version || !active) return;
    current.value = record;
    groups.value = loaded;
    dirty.value = false;
    clearSelection();
    colorIndex.value = groups.value.length % palette.length;
  } catch {
    if (seq === version)
      errorMessage.value = "该记录的标注加载失败，请重新选择。";
  } finally {
    if (seq === version) loading.value = false;
  }
}
function clearSelection() {
  selectedDescription.value = [];
  selectedDiagnosis.value = [];
}
function toggle(type, index) {
  const key =
    type === "description" ? "descriptionIndices" : "diagnosisIndices";
  if (groups.value.some((g) => g[key].includes(index))) {
    ElMessage.info("这个片段已有关联，可先删除原标注组再修改");
    return;
  }
  const indices =
    type === "description" ? selectedDescription : selectedDiagnosis;
  indices.value = indices.value.includes(index)
    ? indices.value.filter((i) => i !== index)
    : [...indices.value, index];
}
function styleFor(type, index) {
  const group = groups.value.find((g) =>
    g[
      type === "description" ? "descriptionIndices" : "diagnosisIndices"
    ].includes(index),
  );
  const selected =
    type === "description"
      ? selectedDescription.value
      : selectedDiagnosis.value;
  return {
    background:
      group?.color ||
      (selected.includes(index) ? palette[colorIndex.value] : ""),
  };
}
function addGroup() {
  if (!selectedDescription.value.length || !selectedDiagnosis.value.length)
    return;
  const a = [...selectedDescription.value].sort((a, b) => a - b),
    b = [...selectedDiagnosis.value].sort((a, b) => a - b);
  groups.value.push({
    descriptionIndices: a,
    diagnosisIndices: b,
    descriptionText: a.map((i) => description.value[i]).join("，"),
    diagnosisText: b.map((i) => diagnosis.value[i]).join("，"),
    color: palette[colorIndex.value],
  });
  dirty.value = true;
  clearSelection();
  colorIndex.value = (colorIndex.value + 1) % palette.length;
}
async function save() {
  if (!current.value || saving.value) return;
  if (selectedDescription.value.length || selectedDiagnosis.value.length) {
    ElMessage.warning("请先确认当前标注组，或清除选择");
    return;
  }
  if (!groups.value.length) {
    ElMessage.warning("请先建立至少一组对应关系；清空已有标注请使用撤销按钮");
    return;
  }
  saving.value = true;
  try {
    await saveGroups(current.value.id, groups.value);
    current.value.annotated = true;
    dirty.value = false;
    ElMessage.success(
      studio.demo ? "示例标注已保存（本次会话）" : "当前标注已保存",
    );
  } catch {
    ElMessage.error("标注保存失败，修改已保留，可重试");
  } finally {
    saving.value = false;
  }
}
async function reset() {
  if (!current.value) return;
  try {
    await ElMessageBox.confirm("撤销这条记录的全部已保存标注？", "撤销标注", {
      type: "warning",
      confirmButtonText: "确认撤销",
      cancelButtonText: "取消",
    });
    await resetGroups(current.value.id);
    current.value.annotated = false;
    groups.value = [];
    dirty.value = false;
    clearSelection();
    ElMessage.success("标注已撤销");
  } catch (e) {
    if (e !== "cancel" && e !== "close") ElMessage.error("撤销失败");
  }
}
function next() {
  if (currentIndex.value < records.value.length - 1)
    selectRecord(records.value[currentIndex.value + 1]);
}
async function download() {
  try {
    await exportJob(jobId.value, true);
  } catch {
    ElMessage.error("导出失败，请先保存标注后重试");
  }
}
onBeforeRouteLeave(allowDiscard);
function beforeUnload(event) {
  if (dirty.value) {
    event.preventDefault();
    event.returnValue = "";
  }
}
window.addEventListener("beforeunload", beforeUnload);
onBeforeUnmount(() => {
  active = false;
  version++;
  window.removeEventListener("beforeunload", beforeUnload);
});
</script>
