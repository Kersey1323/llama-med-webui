<template>
  <div class="batch-top">
    <section
      class="bg-white panel rounded-xl border border-zinc-200 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-150"
    >
      <div class="panel-head">
        <div>
          <h2>上传报告文件</h2>
          <p>请包含「影像描述」「影像诊断」两列，每个文件不超过 16 MB</p>
        </div>
        <span class="count-pill">01 / 导入</span>
      </div>
      <div class="panel-body">
        <el-upload
          class="upload-zone"
          drag
          :auto-upload="false"
          :show-file-list="false"
          accept=".xlsx,.xls,.csv"
          :disabled="busy || studio.demo"
          :on-change="chooseFile"
          ><span class="upload-emblem"
            ><el-icon><UploadFilled /></el-icon></span
          ><b>{{ file?.name || "拖拽文件到此处，或点击浏览上传" }}</b>
          <p>
            {{
              studio.demo
                ? "示例模式已载入虚构报告，请切换真实任务后上传"
                : "支持 .xlsx、.xls、.csv · 请先去除个人身份信息"
            }}
          </p></el-upload
        >
        <div class="upload-actions">
          <el-button
            @click="downloadTemplate"
            class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
            ><el-icon><Download /></el-icon>&nbsp;下载模板</el-button
          ><el-button
            type="primary"
            :loading="busy"
            :disabled="studio.demo || !file"
            @click="start"
            class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
            ><el-icon v-if="!busy"><VideoPlay /></el-icon>&nbsp;{{
              uploading ? "上传中…" : processing ? "正在质检…" : "开始质检"
            }}</el-button
          >
        </div>
      </div>
    </section>
    <section
      class="bg-white panel rounded-xl border border-zinc-200 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-150"
    >
      <div class="panel-head">
        <div>
          <h2>运行状态</h2>
          <p>查看当前任务的处理进度与质控结果</p>
        </div>
        <span class="count-pill">02 / 处理</span>
      </div>
      <div class="panel-body">
        <div style="margin-bottom: 13px">
          <span
            class="status"
            :class="processing ? 'processing' : selectedJob?.status || ''"
            >{{
              uploading
                ? "上传中"
                : processing
                  ? "运行中"
                  : selectedJob
                    ? statusLabel(selectedJob.status)
                    : "等待上传"
            }}</span
          >
        </div>
        <div class="status-box">
          <small>当前任务</small
          ><b>{{ selectedJob ? `任务 #${selectedJob.id}` : "尚未选择任务" }}</b>
        </div>
        <div class="status-box">
          <small>当前文件</small
          ><b>{{ selectedJob?.name || file?.name || "—" }}</b>
        </div>
        <div class="progress-box">
          <div>
            <span>批量质检进度</span
            ><b style="color: var(--primary)">{{ progress }}%</b>
          </div>
          <el-progress
            aria-label="批量质检进度"
            :percentage="progress"
            :show-text="false"
            :stroke-width="6"
          />
        </div>
        <div class="upload-actions">
          <el-button
            :disabled="!selectedJob"
            @click="goAnnotate"
            class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
            >进入标注</el-button
          ><el-button
            :disabled="!selectedJob || selectedJob.status !== 'completed'"
            type="primary"
            plain
            @click="download(false)"
            class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
            ><el-icon><Download /></el-icon>&nbsp;导出质控结果</el-button
          >
        </div>
        <p
          v-if="operationError"
          class="tiny"
          style="color: #b91c1c; margin-top: 12px"
          role="alert"
        >
          {{ operationError }}
        </p>
      </div>
    </section>
  </div>
  <section
    class="bg-white panel batch-section rounded-xl border border-zinc-200 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-150"
  >
    <div class="panel-head">
      <div>
        <h2>
          当前异常结果 <span class="count-pill">{{ totalErrors }} 条</span>
        </h2>
        <p>
          {{
            selectedJob
              ? `任务 #${selectedJob.id} · ${selectedJob.name}`
              : "选择历史任务，或上传文件开始质控"
          }}
        </p>
      </div>
      <div class="section-toolbar">
        <el-button
          size="small"
          :disabled="!selectedJob"
          @click="goAnnotate"
          class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
          ><el-icon><EditPen /></el-icon>&nbsp;报告标注</el-button
        >
      </div>
    </div>
    <el-table
      :data="errors"
      v-loading="loadingErrors"
      empty-text="暂无异常结果，选择一个任务查看"
      ><el-table-column prop="row" label="行号" width="75" /><el-table-column
        prop="type"
        label="异常类型"
        min-width="140"
        ><template #default="{ row }"
          ><el-tag effect="light" type="warning" size="small">{{
            row.type
          }}</el-tag></template
        ></el-table-column
      ><el-table-column
        prop="originalText"
        label="原始描述"
        min-width="220"
        show-overflow-tooltip
      /><el-table-column
        prop="original_diagnosis"
        label="原始诊断"
        min-width="190"
        show-overflow-tooltip
      /><el-table-column label="复核状态" width="105"
        ><template #default="{ row }"
          ><span class="status" :class="row.status">{{
            row.status === "pending" ? "待复核" : statusLabel(row.status)
          }}</span></template
        ></el-table-column
      ><el-table-column label="操作" width="90" fixed="right"
        ><template #default="{ row }"
          ><el-button
            link
            type="primary"
            @click="openDetail(row)"
            class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
            >查看详情</el-button
          ></template
        ></el-table-column
      ></el-table
    >
    <div class="table-footer">
      <span class="task-count">模型识别结果需经人工复核确认</span
      ><el-pagination
        small
        background
        layout="prev, pager, next"
        v-model:current-page="errorPage"
        :page-size="10"
        :total="totalErrors"
        @current-change="fetchErrors"
      />
    </div>
  </section>
  <section
    class="bg-white panel rounded-xl border border-zinc-200 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-150"
  >
    <div class="panel-head">
      <div>
        <h2>历史质控任务</h2>
        <p>回溯处理记录、导出结果与标注内容</p>
      </div>
      <div class="section-toolbar">
        <el-button
          :loading="studio.loading"
          @click="loadJobs"
          class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
          ><el-icon><RefreshRight /></el-icon>&nbsp;刷新任务</el-button
        >
        <el-input
          v-model="search"
          placeholder="搜索文件名称"
          clearable
          style="width: 190px"
          size="small"
          class="bg-zinc-100 border-0 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/30 transition-colors duration-150"
          ><template #prefix
            ><el-icon><Search /></el-icon></template
        ></el-input>
      </div>
    </div>
    <el-table
      :data="filteredJobs.slice((historyPage - 1) * 5, historyPage * 5)"
      empty-text="还没有任务记录"
      v-loading="studio.loading"
      ><el-table-column label="任务文件" min-width="270"
        ><template #default="{ row }"
          ><div class="file-cell">
            <span class="file-icon"
              ><el-icon><Document /></el-icon
            ></span>
            <div>
              <strong>{{ row.name }}</strong
              ><small>#{{ row.id }} · {{ row.time }}</small>
            </div>
          </div></template
        ></el-table-column
      ><el-table-column label="报告 / 异常" width="125"
        ><template #default="{ row }"
          >{{ row.total }} <span class="muted">/</span>
          <span style="color: #92400e">{{ row.errors }}</span></template
        ></el-table-column
      ><el-table-column label="状态" width="100"
        ><template #default="{ row }"
          ><span class="status" :class="row.status">{{
            statusLabel(row.status)
          }}</span></template
        ></el-table-column
      ><el-table-column label="标注状态" min-width="100"
        ><template #default="{ row }"
          ><span class="tiny muted">{{
            row.annotationStatus || "未标注"
          }}</span></template
        ></el-table-column
      ><el-table-column label="操作" min-width="210" fixed="right"
        ><template #default="{ row }"
          ><el-button
            link
            type="primary"
            @click="selectJob(row)"
            class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
            >查看</el-button
          ><el-button
            link
            type="primary"
            :disabled="row.status !== 'completed'"
            @click="download(false, row.id)"
            class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
            >导出结果</el-button
          ><el-button
            link
            type="primary"
            @click="download(true, row.id)"
            class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
            >导出标注</el-button
          ><el-button
            link
            type="danger"
            @click="remove(row)"
            class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
            >删除</el-button
          ></template
        ></el-table-column
      ></el-table
    >
    <div class="table-footer">
      <span class="task-count"
        >已加载最近 {{ studio.jobs.length }} /
        {{ studio.totalJobs }} 个任务</span
      ><el-button
        v-if="studio.jobs.length < studio.totalJobs"
        :loading="studio.loading"
        @click="loadMoreJobs"
        class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
        >加载更多任务</el-button
      ><el-pagination
        small
        background
        layout="prev, pager, next"
        v-model:current-page="historyPage"
        :page-size="5"
        :total="filteredJobs.length"
      />
    </div>
  </section>
  <el-drawer v-model="drawerOpen" size="560px" destroy-on-close
    ><template #header
      ><div class="drawer-header">
        <span class="welcome-icon"><DocumentChecked /></span>
        <div>
          <h2>异常记录详情</h2>
          <p class="tiny muted" style="margin-top: 5px">
            第 {{ detail?.row }} 行 · {{ detail?.type }}
          </p>
        </div>
      </div></template
    ><template v-if="detail"
      ><div class="drawer-section">
        <h3>原始描述</h3>
        <div class="report-text">{{ detail.originalText }}</div>
      </div>
      <div class="drawer-section">
        <h3>原始诊断</h3>
        <div class="report-text">{{ detail.original_diagnosis }}</div>
      </div>
      <div class="drawer-section">
        <h3>参考诊断</h3>
        <div class="report-text">
          {{ detail.genDiagnosis || "暂无参考诊断" }}
        </div>
      </div>
      <div class="drawer-section">
        <h3>修改建议</h3>
        <div class="report-text suggestion">{{ detail.suggestion }}</div>
      </div>
      <div class="drawer-section">
        <h3>分析过程</h3>
        <div class="report-text analysis">{{ detail.content }}</div>
      </div>
      <div class="drawer-section">
        <h3>人工复核</h3>
        <el-radio-group v-model="action" class="review-actions"
          ><el-radio-button value="accept" label="accept"
            >采纳建议</el-radio-button
          ><el-radio-button value="custom" label="custom"
            >自定义修改</el-radio-button
          ><el-radio-button value="ignore" label="ignore"
            >标记非错误</el-radio-button
          ></el-radio-group
        ><el-input
          v-if="action === 'custom'"
          v-model="customText"
          type="textarea"
          :rows="4"
          placeholder="填写人工确认后的诊断内容"
          class="bg-zinc-100 border-0 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/30 transition-colors duration-150"
        />
        <p class="tiny muted" style="line-height: 1.8">
          {{
            studio.demo
              ? "示例操作仅在本次页面会话中保留。"
              : "保存后记录本次人工复核结果。"
          }}
        </p>
      </div></template
    ><template #footer
      ><div class="drawer-footer">
        <el-button
          @click="drawerOpen = false"
          class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
          >暂不处理</el-button
        ><el-button
          type="primary"
          :loading="saving"
          @click="saveReview"
          class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
          >保存复核结果</el-button
        >
      </div></template
    ></el-drawer
  >
</template>
<script setup>
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import api from "../utils/axios";
import {
  studio,
  loadJobs,
  loadMoreJobs,
  getErrors,
  reviewError,
  exportJob,
  saveFile,
  statusLabel,
} from "./store";
const router = useRouter(),
  route = useRoute();
const file = ref(null),
  uploading = ref(false),
  processing = ref(false),
  progress = ref(0),
  selectedId = ref(null),
  operationError = ref("");
const errors = ref([]),
  totalErrors = ref(0),
  errorPage = ref(1),
  loadingErrors = ref(false),
  search = ref(""),
  historyPage = ref(1);
const drawerOpen = ref(false),
  detail = ref(null),
  action = ref("accept"),
  customText = ref(""),
  saving = ref(false);
const busy = computed(() => uploading.value || processing.value);
const selectedJob = computed(() =>
  studio.jobs.find((j) => j.id === selectedId.value),
);
const filteredJobs = computed(() =>
  studio.jobs.filter((j) =>
    j.name.toLowerCase().includes(search.value.toLowerCase()),
  ),
);
let timer,
  active = true,
  fetchVersion = 0;
watch(search, () => (historyPage.value = 1));
watch(
  () => studio.demo,
  () => {
    clearTimeout(timer);
    selectedId.value = null;
    file.value = null;
    processing.value = false;
    progress.value = 0;
    errors.value = [];
    totalErrors.value = 0;
    drawerOpen.value = false;
    operationError.value = "";
    fetchVersion++;
  },
);
watch(
  () => [studio.jobs, route.query.jobId],
  () => {
    if (!studio.jobs.length) {
      selectedId.value = null;
      errors.value = [];
      totalErrors.value = 0;
      return;
    }
    const requested = Number(route.query.jobId);
    const job =
      studio.jobs.find((j) => j.id === requested) ||
      studio.jobs.find((j) => j.id === selectedId.value) ||
      studio.jobs[0];
    selectJob(job);
  },
  { immediate: true },
);
function selectJob(job) {
  selectedId.value = job.id;
  errorPage.value = 1;
  progress.value = job.status === "completed" ? 100 : 0;
  fetchErrors();
}
async function fetchErrors() {
  const version = ++fetchVersion;
  if (!selectedId.value) return;
  loadingErrors.value = true;
  try {
    const result = await getErrors(selectedId.value, errorPage.value);
    if (version === fetchVersion && active) {
      errors.value = result.data;
      totalErrors.value = result.total;
    }
  } catch {
    if (version === fetchVersion && active) {
      errors.value = [];
      totalErrors.value = 0;
      ElMessage.error("异常记录加载失败，请重试");
    }
  } finally {
    if (version === fetchVersion) loadingErrors.value = false;
  }
}
function chooseFile(upload) {
  const raw = upload.raw;
  if (!/\.(xlsx|xls|csv)$/i.test(raw.name)) {
    ElMessage.warning("请选择 Excel 或 CSV 文件");
    return;
  }
  if (raw.size > 16 * 1024 * 1024) {
    ElMessage.warning("文件大小不能超过 16 MB");
    return;
  }
  file.value = raw;
  operationError.value = "";
}
function downloadTemplate() {
  saveFile(
    new Blob(
      [
        "\uFEFF影像描述,影像诊断\r\n双肺纹理清晰未见明显异常密度影。,双肺未见明显异常。\r\n",
      ],
      { type: "text/csv;charset=utf-8" },
    ),
    "影像报告导入模板.csv",
  );
}
async function poll() {
  try {
    const { data } = await api.get("/api/batch/progress", { timeout: 10000 });
    if (!active || studio.demo) return;
    progress.value = Math.min(100, Math.max(0, Number(data.progress) || 0));
  } catch {
    if (active)
      operationError.value = "进度暂时无法获取，可稍后刷新任务确认结果。";
  }
  if (active && processing.value) timer = setTimeout(poll, 3000);
}
async function start() {
  if (!file.value || studio.demo || busy.value) return;
  uploading.value = true;
  operationError.value = "";
  const modeAtStart = studio.demo;
  try {
    const form = new FormData();
    form.append("file", file.value);
    const { data } = await api.post("/api/batch/upload", form, {
      timeout: 60000,
    });
    if (!active || studio.demo !== modeAtStart) return;
    selectedId.value = data.job_id;
    await loadJobs();
    uploading.value = false;
    processing.value = true;
    progress.value = 0;
    poll();
    const result = await api.get("/api/batch/startProcess", {
      params: { job_id: data.job_id },
      timeout: 0,
    });
    if (!active || studio.demo !== modeAtStart) return;
    if (result.data.error) throw new Error(result.data.error);
    progress.value = 100;
    file.value = null;
    await loadJobs();
    await fetchErrors();
    ElMessage.success("质控任务已完成");
  } catch (error) {
    if (active && !studio.demo) {
      operationError.value =
        error.response?.data?.error || "任务未完成，请检查服务状态后刷新确认。";
      ElMessage.error(operationError.value);
    }
  } finally {
    if (active) {
      uploading.value = false;
      processing.value = false;
      clearTimeout(timer);
    }
  }
}
function openDetail(row) {
  detail.value = { ...row };
  action.value = "accept";
  customText.value = row.suggestion || "";
  drawerOpen.value = true;
}
async function saveReview() {
  if (!detail.value || saving.value) return;
  if (action.value === "custom" && !customText.value.trim()) {
    ElMessage.warning("请填写修改内容");
    return;
  }
  saving.value = true;
  try {
    await reviewError(detail.value, action.value, customText.value);
    drawerOpen.value = false;
    await fetchErrors();
    ElMessage.success(
      studio.demo ? "示例复核已保存（本次会话）" : "复核结果已保存",
    );
  } catch {
    ElMessage.error("保存失败，请稍后重试");
  } finally {
    saving.value = false;
  }
}
function goAnnotate() {
  if (selectedId.value)
    router.push({ path: "/annotation", query: { jobId: selectedId.value } });
}
async function download(annotation, id = selectedId.value) {
  try {
    await exportJob(id, annotation);
  } catch {
    ElMessage.error(
      annotation
        ? "标注导出失败，确认该任务已有保存的标注"
        : "结果导出失败，请重试",
    );
  }
}
async function remove(row) {
  if (studio.demo) {
    ElMessage.info("示例任务用于预览，不支持删除");
    return;
  }
  try {
    await ElMessageBox.confirm(
      `删除任务「${row.name}」？此操作无法撤销。`,
      "删除任务",
      {
        type: "warning",
        confirmButtonText: "确认删除",
        cancelButtonText: "取消",
      },
    );
    await api.delete(`/api/batch/jobs/${row.id}`);
    await loadJobs();
    ElMessage.success("任务已删除");
  } catch (e) {
    if (e !== "cancel" && e !== "close") ElMessage.error("删除失败，请重试");
  }
}
onBeforeUnmount(() => {
  active = false;
  fetchVersion++;
  clearTimeout(timer);
});
</script>
