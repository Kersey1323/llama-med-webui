import { computed, reactive } from "vue";
import api from "../utils/axios";

export const studio = reactive({
  demo: sessionStorage.getItem("studio.preview") === "true",
  jobs: [],
  totalJobs: 0,
  loading: false,
  offline: false,
  updatedAt: "",
});
const clone = (value) => JSON.parse(JSON.stringify(value));
const examples = [
  {
    row: 13,
    type: "方位不一致",
    originalText:
      "右肺上叶后段见一枚实性结节，大小约 6 mm × 5 mm，边缘较清晰。双肺其余未见明显异常密度影。纵隔未见明显肿大淋巴结。",
    original_diagnosis: "左肺上叶小结节，建议随访。",
    suggestion: "右肺上叶小结节，建议随访。",
    genDiagnosis: "右肺上叶实性小结节，建议结合临床随访。",
    content: "描述为“右肺上叶”，诊断为“左肺上叶”，侧别不一致。",
  },
  {
    row: 28,
    type: "文字错误",
    originalText:
      "肝脏形态、大小正常，肝实质密度均匀，未见明确占位性病变。胆囊未见明显异常。",
    original_diagnosis: "肝脏未见明显异尝。",
    suggestion: "肝脏未见明显异常。",
    genDiagnosis: "肝脏、胆囊未见明显异常。",
    content: "“异尝”为错别字，结合上下文建议复核为“异常”。",
  },
  {
    row: 46,
    type: "描述与诊断不一致",
    originalText:
      "双侧胸廓对称，右侧胸腔见少量积液。双肺纹理清晰，未见明显实变影。心影大小正常。",
    original_diagnosis: "胸部 CT 平扫未见明显异常。",
    suggestion: "右侧少量胸腔积液。",
    genDiagnosis: "右侧少量胸腔积液，请结合临床。",
    content:
      "影像描述提示右侧少量胸腔积液，原始诊断未提及，建议人工复核是否遗漏。",
  },
];
const demoJobs = [
  {
    id: 1004,
    name: "胸部影像报告_示例.xlsx",
    time: "2026-10-14 09:30:00",
    total: 100,
    errors: 3,
    status: "completed",
    annotationStatus: "未标注",
  },
  {
    id: 1003,
    name: "腹部影像报告_示例.xlsx",
    time: "2026-10-13 16:20:00",
    total: 100,
    errors: 3,
    status: "completed",
    annotationStatus: "未标注",
  },
  {
    id: 1002,
    name: "放射科质控_示例.csv",
    time: "2026-10-13 11:05:00",
    total: 100,
    errors: 3,
    status: "completed",
    annotationStatus: "未标注",
  },
  {
    id: 1001,
    name: "影像报告抽检_示例.xlsx",
    time: "2026-10-12 14:40:00",
    total: 100,
    errors: 3,
    status: "completed",
    annotationStatus: "未标注",
  },
];
const demoErrors = reactive(
  Object.fromEntries(
    demoJobs.map((job) => [
      job.id,
      examples.map((e, i) => ({
        ...clone(e),
        id: job.id * 10 + i,
        status: "pending",
        annotated: false,
      })),
    ]),
  ),
);
const demoGroups = reactive({});
let generation = 0;
function syncPreviewAnnotations() {
  for (const job of studio.jobs) {
    const rows = demoErrors[job.id] || [];
    job.annotatedCount = rows.filter((row) => row.annotated).length;
    job.annotationStatus = !job.annotatedCount
      ? "未标注"
      : job.annotatedCount === rows.length
        ? "标注完成"
        : "标注中";
  }
}
export function loadJobs() {
  return fetchJobs(1, false);
}
export function loadMoreJobs() {
  return fetchJobs(Math.floor(studio.jobs.length / 100) + 1, true);
}
async function fetchJobs(page, append) {
  const request = ++generation;
  studio.loading = true;
  studio.offline = false;
  try {
    const result = studio.demo
      ? { data: clone(demoJobs), total: demoJobs.length }
      : (
          await api.get("/api/batch/jobs", {
            params: { page, page_size: 100 },
            timeout: 8000,
          })
        ).data;
    if (request !== generation) return;
    studio.jobs = append
      ? [...studio.jobs, ...(result.data || [])]
      : result.data || [];
    if (studio.demo) syncPreviewAnnotations();
    studio.totalJobs = Number(result.total || 0);
    studio.updatedAt = new Date().toLocaleTimeString("zh-CN", {
      hour12: false,
    });
  } catch {
    if (request !== generation) return;
    if (!append) {
      studio.jobs = [];
      studio.totalJobs = 0;
    }
    studio.offline = true;
  } finally {
    if (request === generation) studio.loading = false;
  }
}
export async function setDemo(value) {
  studio.demo = value;
  sessionStorage.setItem("studio.preview", String(value));
  studio.jobs = [];
  studio.updatedAt = "";
  await loadJobs();
}
export async function getErrors(id, page = 1, pageSize = 10) {
  if (!studio.demo)
    return (
      await api.get(`/api/batch/jobs/${id}/errors`, {
        params: { page, page_size: pageSize },
        timeout: 12000,
      })
    ).data;
  const rows = demoErrors[id] || [];
  return {
    data: clone(rows.slice((page - 1) * pageSize, page * pageSize)),
    total: rows.length,
  };
}
export async function reviewError(error, action, correctedText) {
  if (!studio.demo)
    return (
      await api.put(`/api/batch/errors/${error.id}`, {
        action_type: action,
        corrected_text: correctedText,
      })
    ).data;
  const row = Object.values(demoErrors)
    .flat()
    .find((e) => e.id === error.id);
  if (row)
    Object.assign(row, {
      status: action === "ignore" ? "ignored" : "corrected",
      content: action === "custom" ? correctedText : error.suggestion,
    });
}
export async function getGroups(id) {
  if (studio.demo) return clone(demoGroups[id] || []);
  const response = await api.get(`/api/annotation/error/${id}/groups`);
  if (!response.data.success) throw new Error("加载标注失败");
  return response.data.data;
}
export async function saveGroups(id, groups) {
  if (studio.demo) {
    demoGroups[id] = clone(groups);
    const row = Object.values(demoErrors)
      .flat()
      .find((e) => e.id === id);
    if (row) row.annotated = true;
    syncPreviewAnnotations();
    return;
  }
  const response = await api.post(`/api/annotation/error/${id}/groups`, {
    annotationGroups: groups,
  });
  if (!response.data.success) throw new Error("保存标注失败");
}
export async function resetGroups(id) {
  if (!studio.demo) await api.post(`/api/annotation/error/${id}/reset`);
  else {
    delete demoGroups[id];
    const row = Object.values(demoErrors)
      .flat()
      .find((e) => e.id === id);
    if (row) row.annotated = false;
    syncPreviewAnnotations();
  }
}
export const stats = computed(() => {
  const rows = studio.jobs.reduce((n, j) => n + Number(j.total || 0), 0);
  const errors = studio.jobs.reduce((n, j) => n + Number(j.errors || 0), 0);
  return {
    rows,
    errors,
    completed: studio.jobs.filter((j) => j.status === "completed").length,
    rate: rows ? Math.max(0, ((rows - errors) / rows) * 100).toFixed(1) : null,
  };
});
export function statusLabel(status) {
  return (
    {
      completed: "已完成",
      processing: "运行中",
      pending: "待处理",
      failed: "失败",
      corrected: "已修正",
      ignored: "非错误",
    }[status] ||
    status ||
    "待复核"
  );
}
export function saveFile(blob, name) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = name;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
export async function exportJob(id, annotation = false) {
  if (studio.demo) {
    const rows = annotation
      ? Object.fromEntries(
          (demoErrors[id] || []).map((e) => [e.id, demoGroups[e.id] || []]),
        )
      : demoErrors[id] || [];
    saveFile(
      new Blob([JSON.stringify(rows, null, 2)], { type: "application/json" }),
      `示例_${annotation ? "标注" : "质控"}_${id}.json`,
    );
  } else {
    const response = await api.get(
      `/api/batch/jobs/${id}/${annotation ? "export-annotation" : "export"}`,
      { responseType: "blob" },
    );
    saveFile(response.data, `${annotation ? "标注" : "质控结果"}_${id}.xlsx`);
  }
}
