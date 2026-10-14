<template>
  <div class="bento-grid grid grid-cols-4 gap-6" aria-label="质控工作台">
    <section
      v-for="(metric, index) in metrics"
      :key="metric.label"
      class="bg-white panel metric rounded-xl border border-zinc-200 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-150"
      :class="`bento-metric-${index + 1}`"
      v-loading="studio.loading"
    >
      <div class="metric-label">
        {{ metric.label }}<el-icon><component :is="metric.icon" /></el-icon>
      </div>
      <div class="metric-value">
        {{ studio.offline ? "—" : metric.value
        }}<small v-if="!studio.offline">{{ metric.unit }}</small>
      </div>
      <div
        class="metric-trend"
        :class="studio.offline ? 'neutral' : metric.trend.direction"
        :title="comparisonLabel"
      >
        <el-icon
          ><component
            :is="
              metric.trend.direction === 'up'
                ? 'Top'
                : metric.trend.direction === 'down'
                  ? 'Bottom'
                  : 'Minus'
            " /></el-icon
        ><span>{{ studio.offline ? "数据暂不可用" : metric.trend.text }}</span
        ><span class="trend-description">{{ metric.note }}</span>
      </div>
    </section>
    <section
      class="bg-white panel chart-panel bento-trend col-span-2 row-span-2 rounded-xl border border-zinc-200 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-150"
    >
      <div class="panel-head">
        <div>
          <h2>
            <el-icon class="tile-icon"><DataLine /></el-icon>报告质控趋势
          </h2>
          <p>{{ chartRangeLabel }}</p>
        </div>
        <div class="chart-legend">
          <span><i class="report-series"></i>报告总数</span
          ><span><i class="error-series"></i>异常记录</span>
        </div>
      </div>
      <div class="panel-body">
        <div class="trend-chart" v-loading="studio.loading">
          <svg
            v-if="dailySeries.some((day) => day.jobs)"
            viewBox="0 0 760 300"
            role="img"
            aria-labelledby="trend-chart-title trend-chart-desc"
          >
            <title id="trend-chart-title">最近七日报告质控数量趋势</title>
            <desc id="trend-chart-desc">{{ chartDescription }}</desc>
            <g v-for="tick in ticks" :key="tick.value">
              <line
                x1="52"
                x2="728"
                :y1="tick.y"
                :y2="tick.y"
                class="chart-grid-line"
              />
              <text
                x="40"
                :y="tick.y + 4"
                text-anchor="end"
                class="chart-axis-label"
              >
                {{ tick.value }}
              </text>
            </g>
            <polygon :points="areaPoints" class="chart-area" />
            <polyline :points="reportPoints" class="chart-report-line" />
            <polyline :points="errorPoints" class="chart-error-line" />
            <g v-for="(day, index) in dailySeries" :key="day.key">
              <circle
                :cx="x(index)"
                :cy="y(day.reports)"
                r="4"
                class="chart-point"
              >
                <title>
                  {{ day.label }}：{{ day.reports }} 份报告，{{ day.errors }}
                  条异常
                </title>
              </circle>
              <text
                :x="x(index)"
                y="278"
                text-anchor="middle"
                class="chart-axis-label"
              >
                {{ day.label }}
              </text>
            </g>
          </svg>
          <div v-else class="chart-empty">
            <el-icon><DataLine /></el-icon
            ><b>{{
              studio.offline ? "暂时无法获取趋势数据" : "暂无报告数据"
            }}</b
            ><span>完成首个质控任务后，将在此显示每日处理量。</span>
          </div>
        </div>
      </div>
    </section>
    <section
      class="bg-white panel chart-panel bento-distribution rounded-xl border border-zinc-200 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-150"
    >
      <div class="panel-head">
        <div>
          <h2>异常类型分布</h2>
          <p>
            最近批次 ·
            {{
              detailsFailed
                ? "明细暂不可用"
                : `${recentErrors.length} 条已加载异常`
            }}
          </p>
        </div>
        <el-icon class="tile-icon"><PieChart /></el-icon>
      </div>
      <div class="panel-body" v-loading="detailsLoading">
        <div class="distribution-chart">
          <template v-if="distribution.length"
            ><div
              class="donut"
              :style="{ background: donutBackground }"
              role="img"
              :aria-label="
                distribution
                  .map((item) => `${item.name} ${item.count} 条`)
                  .join('，')
              "
            >
              <div class="donut-center">
                <b>{{ recentErrors.length }}</b
                ><small>异常记录</small>
              </div>
            </div>
            <div class="legend">
              <div v-for="(item, index) in distribution" :key="item.name">
                <i :style="{ background: colors[index % colors.length] }"></i
                ><span>{{ item.name }}</span
                ><b
                  >{{ item.count }}
                  <small
                    >{{
                      Math.round((item.count / recentErrors.length) * 100)
                    }}%</small
                  ></b
                >
              </div>
            </div></template
          >
          <div v-else class="chart-empty">
            <el-icon><PieChart /></el-icon
            ><b>{{ detailsFailed ? "异常明细加载失败" : "暂无异常分布" }}</b
            ><span>{{
              detailsFailed
                ? "请刷新后重试。"
                : "有异常记录后，将在此显示类型占比。"
            }}</span>
          </div>
        </div>
      </div>
    </section>

    <section
      class="bg-white panel bento-recent col-span-2 rounded-xl border border-zinc-200 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-150"
    >
      <div class="panel-head">
        <div>
          <h2>
            <el-icon class="tile-icon"><Files /></el-icon>最近质控任务
            <span class="count-pill">{{ studio.totalJobs }}</span>
          </h2>
          <p>关注任务进度，及时处理报告异常</p>
        </div>
        <div class="panel-actions">
          <el-button
            :loading="studio.loading"
            @click="loadJobs"
            class="rounded-lg font-medium text-sm transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
            ><el-icon><RefreshRight /></el-icon>&nbsp;刷新</el-button
          >
          <el-button
            type="primary"
            @click="$router.push('/batch-process')"
            class="rounded-lg font-medium text-sm transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
            ><el-icon><Plus /></el-icon>&nbsp;新建质控任务</el-button
          >
          <router-link class="text-link" to="/batch-process"
            >全部任务 →</router-link
          >
        </div>
      </div>
      <el-table
        :data="studio.jobs.slice(0, 4)"
        v-loading="studio.loading"
        empty-text="暂无质控任务，先上传一份报告吧"
      >
        <el-table-column label="任务文件" min-width="240"
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
        >
        <el-table-column label="异常 / 总数" width="115"
          ><template #default="{ row }"
            ><span class="error-count">{{ row.errors }}</span
            ><span class="muted"> / {{ row.total }}</span></template
          ></el-table-column
        >
        <el-table-column label="状态" width="105"
          ><template #default="{ row }"
            ><span class="status" :class="row.status">{{
              statusLabel(row.status)
            }}</span></template
          ></el-table-column
        >
        <el-table-column label="操作" width="80"
          ><template #default="{ row }"
            ><router-link
              class="text-link"
              :to="{ path: '/batch-process', query: { jobId: row.id } }"
              >查看</router-link
            ></template
          ></el-table-column
        >
      </el-table>
    </section>
    <section
      class="bg-white panel bento-review rounded-xl border border-zinc-200 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-150"
    >
      <div class="panel-head">
        <div>
          <h2>
            <el-icon class="tile-icon"><DocumentChecked /></el-icon>人工复核进度
          </h2>
          <p>最近批次 · 复核与标注形成闭环</p>
        </div>
      </div>
      <div class="panel-body">
        <div class="review-banner">
          <span class="welcome-icon"><DocumentChecked /></span>
          <div>
            <b>{{ detailsFailed ? "—" : pending }}</b>
            <p>条异常等待人工复核</p>
          </div>
          <router-link
            class="text-link"
            style="margin-left: auto"
            :to="latestLink"
            >去处理 →</router-link
          >
        </div>
        <div v-for="bar in bars" :key="bar.label" class="bar-row">
          <div>
            <span>{{ bar.label }}</span
            ><b>{{ detailsFailed ? "—" : `${bar.value}%` }}</b>
          </div>
          <div class="bar-track">
            <span
              :style="{ width: bar.value + '%', background: bar.color }"
            ></span>
          </div>
        </div>
        <router-link
          class="quick-link"
          :to="{
            path: '/annotation',
            query: studio.jobs[0] ? { jobId: studio.jobs[0].id } : {},
          }"
          ><el-icon><EditPen /></el-icon>
          <div><b>继续报告标注</b><small>关联影像描述与诊断片段</small></div>
          <span>→</span></router-link
        >
      </div>
    </section>
  </div>
</template>
<script setup>
import { computed, ref, watch, onBeforeUnmount } from "vue";
import { studio, stats, loadJobs, getErrors, statusLabel } from "./store";
const recentErrors = ref([]),
  detailsLoading = ref(false),
  detailsFailed = ref(false);
let request = 0;
watch(
  () => [studio.demo, studio.jobs],
  async () => {
    const version = ++request;
    recentErrors.value = [];
    detailsFailed.value = false;
    detailsLoading.value = false;
    if (!studio.jobs[0]) return;
    detailsLoading.value = true;
    try {
      let page = 1,
        rows = [],
        result;
      do {
        result = await getErrors(studio.jobs[0].id, page++, 1000);
        if (version !== request) return;
        rows.push(...result.data);
      } while (result.data.length && rows.length < result.total);
      recentErrors.value = rows;
    } catch {
      if (version === request) detailsFailed.value = true;
    } finally {
      if (version === request) detailsLoading.value = false;
    }
  },
  { immediate: true },
);
onBeforeUnmount(() => request++);
const pending = computed(
  () => recentErrors.value.filter((e) => e.status === "pending").length,
);
const latestLink = computed(() => ({
  path: "/batch-process",
  query: studio.jobs[0] ? { jobId: studio.jobs[0].id } : {},
}));
const keyFor = (date) =>
  `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
const datedJobs = computed(() =>
  studio.jobs
    .map((job) => ({
      ...job,
      date: new Date(String(job.time || "").replace(" ", "T")),
    }))
    .filter((job) => Number.isFinite(job.date.getTime())),
);
const activeDays = computed(() =>
  [...new Set(datedJobs.value.map((job) => keyFor(job.date)))].sort().reverse(),
);
const daySummary = (key) => {
  const jobs = datedJobs.value.filter((job) => keyFor(job.date) === key);
  return {
    jobs: jobs.length,
    reports: jobs.reduce((n, j) => n + Number(j.total || 0), 0),
    errors: jobs.reduce((n, j) => n + Number(j.errors || 0), 0),
    rate: jobs.length
      ? (jobs.filter((j) => j.status === "completed").length / jobs.length) *
        100
      : 0,
  };
};
const comparisonLabel = computed(() =>
  activeDays.value.length > 1
    ? `日增量对比：${activeDays.value[0]} / ${activeDays.value[1]}`
    : "趋势对比需要至少两个有任务的日期",
);
function trend(key, points = false) {
  if (activeDays.value.length < 2)
    return { direction: "neutral", text: "暂无对比" };
  const current = daySummary(activeDays.value[0])[key],
    previous = daySummary(activeDays.value[1])[key];
  const difference = current - previous;
  if (!difference) return { direction: "flat", text: "持平" };
  const direction = difference > 0 ? "up" : "down";
  if (!previous && !points) return { direction, text: "新增" };
  const value = points
    ? Math.abs(difference)
    : Math.abs((difference / previous) * 100);
  return {
    direction,
    text: `${difference > 0 ? "增长" : "下降"} ${value.toFixed(1)}${points ? " 个百分点" : "%"}`,
  };
}
const metrics = computed(() => [
  {
    label: "累计质控报告",
    value: stats.value.rows.toLocaleString(),
    unit: "份",
    icon: "DocumentChecked",
    trend: trend("reports"),
    note: "日处理量",
  },
  {
    label: "累计异常记录",
    value: stats.value.errors.toLocaleString(),
    unit: "条",
    icon: "Warning",
    trend: trend("errors"),
    note: "日发现量",
  },
  {
    label: "历史质控任务",
    value: studio.totalJobs.toLocaleString(),
    unit: "个",
    icon: "Files",
    trend: trend("jobs"),
    note: "日新增量",
  },
  {
    label: "任务完成率",
    value: studio.jobs.length
      ? ((stats.value.completed / studio.jobs.length) * 100).toFixed(1)
      : "—",
    unit: studio.jobs.length ? "%" : "",
    icon: "CircleCheck",
    trend: trend("rate", true),
    note: "日完成率",
  },
]);
const dailySeries = computed(() => {
  if (!activeDays.value.length) return [];
  const end = new Date(`${activeDays.value[0]}T12:00:00`);
  return Array.from({ length: 7 }, (_, index) => {
    const date = new Date(end);
    date.setDate(date.getDate() - 6 + index);
    const key = keyFor(date);
    return {
      key,
      label: `${date.getMonth() + 1}/${date.getDate()}`,
      ...daySummary(key),
    };
  });
});
const chartRangeLabel = computed(() =>
  dailySeries.value.length
    ? `${dailySeries.value[0].key} — ${dailySeries.value[6].key} · 已加载 ${studio.jobs.length}/${studio.totalJobs} 个任务`
    : "最近七个自然日 · 等待任务数据",
);
const chartDescription = computed(() =>
  dailySeries.value
    .map((day) => `${day.key}：${day.reports} 份报告，${day.errors} 条异常`)
    .join("；"),
);
const maxValue = computed(() =>
  Math.max(
    4,
    Math.ceil(
      Math.max(
        0,
        ...dailySeries.value.map((day) => Math.max(day.reports, day.errors)),
      ) / 4,
    ) * 4,
  ),
);
const x = (index) => 52 + (index * 676) / 6,
  y = (value) => 240 - (value / maxValue.value) * 210;
const ticks = computed(() =>
  Array.from({ length: 5 }, (_, i) => ({
    value: (maxValue.value * i) / 4,
    y: y((maxValue.value * i) / 4),
  })),
);
const reportPoints = computed(() =>
  dailySeries.value.map((day, i) => `${x(i)},${y(day.reports)}`).join(" "),
);
const errorPoints = computed(() =>
  dailySeries.value.map((day, i) => `${x(i)},${y(day.errors)}`).join(" "),
);
const areaPoints = computed(() => `52,240 ${reportPoints.value} 728,240`);
const colors = ["#6366f1", "#10b981", "#f59e0b", "#ef4444", "#6b7280"];
const distribution = computed(() => {
  const counts = {};
  recentErrors.value.forEach(
    (e) => (counts[e.type] = (counts[e.type] || 0) + 1),
  );
  return Object.entries(counts).map(([name, count]) => ({ name, count }));
});
const donutBackground = computed(() => {
  let position = 0;
  if (!recentErrors.value.length) return "#f3f4f6";
  return `conic-gradient(${distribution.value
    .map((item, index) => {
      const start = position;
      position += (item.count / recentErrors.value.length) * 100;
      return `${colors[index % colors.length]} ${start}% ${position}%`;
    })
    .join(",")})`;
});
const bars = computed(() => [
  {
    label: "异常复核完成率",
    value: recentErrors.value.length
      ? Math.round(
          ((recentErrors.value.length - pending.value) /
            recentErrors.value.length) *
            100,
        )
      : 0,
    color: "#6366f1",
  },
  {
    label: "报告标注完成率",
    value: recentErrors.value.length
      ? Math.round(
          (recentErrors.value.filter((e) => e.annotated).length /
            recentErrors.value.length) *
            100,
        )
      : 0,
    color: "#10b981",
  },
]);
</script>
