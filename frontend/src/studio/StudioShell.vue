<template>
  <div class="studio-shell" :class="{ 'sidebar-collapsed': collapsed }">
    <aside
      id="studio-navigation"
      class="studio-sidebar bg-white w-64"
      :class="{ 'is-open': menuOpen }"
      :inert="narrow && !menuOpen ? true : undefined"
      aria-label="工作空间导航"
    >
      <router-link
        to="/"
        class="studio-brand"
        :aria-label="collapsed ? 'CDU-MED Studio 首页' : undefined"
        @click="closeMenu"
      >
        <span class="brand-mark"
          ><el-icon><FirstAidKit /></el-icon
        ></span>
        <span class="brand-copy"
          ><strong>CDU-MED <em>Studio</em></strong
          ><small>医学影像报告质控平台</small></span
        >
      </router-link>
      <span class="nav-caption">工作空间</span>
      <nav class="studio-nav" aria-label="主导航">
        <el-tooltip
          v-for="item in nav"
          :key="item.path"
          :content="item.label"
          placement="right"
          :disabled="!collapsed || narrow"
          :show-after="200"
        >
          <router-link
            :to="item.path"
            :aria-label="item.label"
            @click="closeMenu"
          >
            <el-icon><component :is="item.icon" /></el-icon
            ><span class="nav-label">{{ item.label }}</span
            ><span class="nav-arrow" aria-hidden="true">›</span>
          </router-link>
        </el-tooltip>
      </nav>
      <div class="sidebar-bottom">
        <button
          class="sidebar-collapse rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
          :aria-label="collapsed ? '展开侧边栏' : '收起侧边栏'"
          :aria-expanded="!collapsed"
          aria-controls="studio-navigation"
          @click="toggleSidebar"
        >
          <el-icon><component :is="collapsed ? 'Expand' : 'Fold'" /></el-icon
          ><span class="nav-label">收起侧边栏</span>
        </button>
        <div class="sidebar-user">
          <span class="avatar">{{ AUTH_DISABLED ? "访" : "U" }}</span>
          <div class="user-copy">
            <b>{{ AUTH_DISABLED ? "本地访客" : "当前用户" }}</b
            ><small>{{ AUTH_DISABLED ? "免登录体验" : "已登录" }}</small>
          </div>
          <el-tooltip
            v-if="!AUTH_DISABLED"
            content="退出登录"
            :disabled="!collapsed"
            ><el-button
              class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
              text
              aria-label="退出登录"
              @click="logout"
              ><el-icon><SwitchButton /></el-icon></el-button
          ></el-tooltip>
        </div>
      </div>
    </aside>
    <button
      v-if="menuOpen"
      class="nav-backdrop rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
      aria-label="关闭导航"
      @click="closeMenu"
    ></button>
    <div class="studio-workspace ml-64">
      <header class="studio-topbar">
        <div class="topbar-title">
          <el-button
            ref="menuButton"
            class="mobile-menu rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
            text
            :aria-expanded="menuOpen"
            aria-controls="studio-navigation"
            aria-label="打开导航"
            @click="openMenu"
            ><el-icon><Menu /></el-icon
          ></el-button>
          <div>
            <h1>{{ title }}</h1>
            <small>医学影像报告智能质控工作空间</small>
          </div>
        </div>
        <div class="topbar-search">
          <el-popover
            v-model:visible="searchOpen"
            placement="bottom-start"
            :width="350"
            trigger="click"
            :hide-after="0"
            popper-class="studio-search-popover"
          >
            <template #reference>
              <el-input
                v-model="searchQuery"
                aria-label="搜索页面和已加载任务"
                placeholder="搜索页面、报告任务…"
                clearable
                class="bg-zinc-100 border-0 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/30 transition-colors duration-150"
                @input="searchOpen = true"
                @keydown.down.prevent="searchOpen = true"
                @keydown.enter="openSearchResult(searchResults[0])"
                @keydown.esc="searchOpen = false"
                ><template #prefix
                  ><el-icon><Search /></el-icon></template
              ></el-input>
            </template>
            <p class="search-caption">页面与已加载任务</p>
            <div v-if="searchResults.length" class="search-results">
              <button
                v-for="item in searchResults"
                :key="item.key"
                class="rounded-lg font-medium text-sm transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
                @click="openSearchResult(item)"
              >
                <el-icon><component :is="item.icon" /></el-icon
                ><span>{{ item.label }}</span
                ><small>{{ item.kind }}</small>
              </button>
            </div>
            <p v-else class="empty-inline">没有找到匹配结果</p>
          </el-popover>
        </div>
        <div class="topbar-actions">
          <div class="mode-control" role="group" aria-label="数据模式">
            <button
              class="rounded-lg font-medium text-sm transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
              :class="{ active: !studio.demo }"
              :aria-pressed="!studio.demo"
              @click="changeMode(false)"
            >
              真实任务
            </button>
            <button
              class="rounded-lg font-medium text-sm transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
              :class="{ active: studio.demo }"
              :aria-pressed="studio.demo"
              @click="changeMode(true)"
            >
              示例预览
            </button>
          </div>
          <el-popover
            placement="bottom-end"
            :width="340"
            trigger="click"
            :hide-after="0"
            popper-class="studio-notification-popover"
            v-model:visible="notificationsOpen"
          >
            <template #reference
              ><button
                class="notification-button rounded-lg font-medium text-sm transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
                aria-label="查看任务通知"
              >
                <el-icon><Bell /></el-icon
                ><span v-if="activeTasks" class="notification-count">{{
                  activeTasks
                }}</span>
              </button></template
            >
            <div class="notification-heading">
              <h3>任务动态</h3>
              <span class="tiny muted">{{
                studio.demo ? "示例数据" : "已加载任务"
              }}</span>
            </div>
            <p v-if="studio.loading" class="empty-inline" role="status">
              正在加载任务…
            </p>
            <p v-else-if="studio.offline" class="empty-inline">
              暂时无法获取任务动态
            </p>
            <p v-else-if="!studio.jobs.length" class="empty-inline">
              暂无任务通知
            </p>
            <router-link
              v-for="job in studio.jobs.slice(0, 4)"
              v-else
              :key="job.id"
              class="notification-item"
              :to="{ path: '/batch-process', query: { jobId: job.id } }"
              ><el-icon><DocumentChecked /></el-icon>
              <div>
                <b>{{ job.name }}</b
                ><small>{{ job.time }}</small>
              </div>
              <span class="status" :class="job.status">{{
                statusLabel(job.status)
              }}</span></router-link
            >
          </el-popover>
          <div class="topbar-user" aria-label="当前用户信息">
            <span class="avatar">{{ AUTH_DISABLED ? "访" : "U" }}</span>
            <div>
              <b>{{ AUTH_DISABLED ? "本地访客" : "当前用户" }}</b
              ><small>{{ AUTH_DISABLED ? "免登录模式" : "已登录" }}</small>
            </div>
          </div>
        </div>
      </header>
      <main
        id="main-content"
        ref="content"
        class="studio-content"
        tabindex="-1"
      >
        <div
          v-if="!studio.demo && studio.offline"
          class="notice offline-notice"
          role="status"
        >
          <el-icon><Warning /></el-icon
          ><span>暂时无法连接任务服务，请确认后端和数据库已启动。</span
          ><button
            class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
            @click="setDemo(true)"
          >
            先看示例 →
          </button>
        </div>
        <div class="studio-page"><slot /></div>
        <footer class="studio-footer">
          <span>CDU-MED Studio</span
          ><span>模型建议仅供辅助参考，最终结果由专业人员确认。</span>
        </footer>
      </main>
    </div>
  </div>
</template>
<script setup>
import {
  computed,
  nextTick,
  onMounted,
  onBeforeUnmount,
  ref,
  watch,
} from "vue";
import { useRoute, useRouter } from "vue-router";
import { studio, loadJobs, setDemo, statusLabel } from "./store";
import { AUTH_DISABLED } from "./config";
const route = useRoute(),
  router = useRouter(),
  menuOpen = ref(false),
  content = ref(null),
  menuButton = ref(null);
const collapsed = ref(
  localStorage.getItem("studio.sidebarCollapsed") === "true",
);
const media = window.matchMedia("(max-width: 1023px)"),
  narrow = ref(media.matches);
const nav = [
  { path: "/", label: "首页", icon: "House" },
  { path: "/dashboard", label: "工作台", icon: "Odometer" },
  { path: "/batch-process", label: "批量质控", icon: "DocumentChecked" },
  { path: "/medllm", label: "知识对话", icon: "ChatDotRound" },
  { path: "/annotation", label: "报告标注", icon: "EditPen" },
];
const searchQuery = ref(""),
  searchOpen = ref(false),
  notificationsOpen = ref(false);
const activeTasks = computed(
  () =>
    studio.jobs.filter((job) => ["processing", "failed"].includes(job.status))
      .length,
);
const searchResults = computed(() => {
  const query = searchQuery.value.trim().toLowerCase();
  const pages = nav.map((item) => ({ ...item, key: item.path, kind: "页面" }));
  const jobs = studio.jobs.map((job) => ({
    key: job.id,
    label: job.name,
    icon: "Document",
    kind: `#${job.id}`,
    path: { path: "/batch-process", query: { jobId: job.id } },
  }));
  return [...pages, ...jobs]
    .filter(
      (item) =>
        !query ||
        item.label.toLowerCase().includes(query) ||
        item.kind.toLowerCase().includes(query),
    )
    .slice(0, 8);
});
function openSearchResult(item) {
  if (!item) return;
  router.push(item.path);
  searchOpen.value = false;
}
const title = computed(
  () => nav.find((n) => n.path === route.path)?.label || "报告质控",
);
function changeMode(value) {
  if (value !== studio.demo) setDemo(value);
}
function logout() {
  localStorage.removeItem("token");
  router.push("/auth");
}
function toggleSidebar() {
  collapsed.value = !collapsed.value;
  localStorage.setItem("studio.sidebarCollapsed", String(collapsed.value));
}
function closeMenu() {
  if (menuOpen.value) {
    menuOpen.value = false;
    nextTick(() => menuButton.value?.$el.focus());
  }
}
function openMenu() {
  menuOpen.value = true;
  nextTick(() => document.querySelector(".studio-nav a")?.focus());
}
function mediaChanged(event) {
  narrow.value = event.matches;
  menuOpen.value = false;
}
function keydown(event) {
  if (event.key === "Escape") {
    searchOpen.value = false;
    notificationsOpen.value = false;
  }
  if (!menuOpen.value) return;
  if (event.key === "Escape") {
    event.preventDefault();
    closeMenu();
  }
  if (event.key === "Tab") {
    const links = [
      ...document.querySelectorAll(".studio-sidebar a, .studio-sidebar button"),
    ].filter((e) => e.getClientRects().length);
    const first = links[0],
      last = links[links.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last?.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first?.focus();
    }
  }
}
watch(
  () => route.fullPath,
  () => {
    content.value?.scrollTo({ top: 0 });
    closeMenu();
    searchOpen.value = false;
    notificationsOpen.value = false;
  },
);
watch(menuOpen, (value) => {
  if (content.value) content.value.inert = value;
});
onMounted(() => {
  loadJobs();
  media.addEventListener("change", mediaChanged);
  window.addEventListener("keydown", keydown);
});
onBeforeUnmount(() => {
  media.removeEventListener("change", mediaChanged);
  window.removeEventListener("keydown", keydown);
});
</script>
