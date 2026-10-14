<template>
  <div class="home-page">
    <a class="home-skip" href="#home-main">跳到主要内容</a>
    <header class="home-header">
      <div class="home-container home-header-inner">
        <router-link to="/" class="home-brand" aria-label="CDU-MED Studio 首页">
          <span class="home-brand-icon"
            ><el-icon><FirstAidKit /></el-icon
          ></span>
          <span>CDU-MED <em>Studio</em></span>
        </router-link>
        <nav class="home-navigation" aria-label="首页导航">
          <a href="#capabilities">功能概览</a>
          <a href="#workflow">工作流程</a>
          <router-link to="/dashboard">工作台</router-link>
        </nav>
        <router-link
          class="home-button home-button-primary home-header-cta"
          to="/batch-process"
        >
          开始质控 <el-icon><ArrowRight /></el-icon>
        </router-link>
      </div>
    </header>

    <main id="home-main" class="home-container" tabindex="-1">
      <section class="home-hero" aria-labelledby="home-title">
        <div class="home-hero-copy">
          <span class="home-badge"
            ><el-icon><FirstAidKit /></el-icon>医学影像报告智能质控</span
          >
          <h1 id="home-title">读懂报告，<br />让<span>细节</span>更有把握。</h1>
          <p class="home-lead">
            从文字错误到描述与诊断的一致性，<br
              class="home-desktop-break"
            />把批量筛查、报告核对与人工标注，连成清晰的工作流程。
          </p>
          <div class="home-hero-actions">
            <router-link
              class="home-button home-button-primary"
              to="/batch-process"
            >
              开始报告质控 <el-icon><ArrowRight /></el-icon>
            </router-link>
            <router-link
              class="home-button home-button-secondary"
              to="/dashboard"
            >
              <el-icon><Odometer /></el-icon>进入工作台
            </router-link>
          </div>
          <div class="home-format-note">
            <el-icon><DocumentChecked /></el-icon>支持 Excel / CSV 报告导入
            <span aria-hidden="true">·</span> 保留人工复核环节
          </div>
        </div>

        <figure class="home-report-preview" aria-labelledby="preview-title">
          <div class="home-preview-top">
            <span class="home-preview-icon"
              ><el-icon><DocumentChecked /></el-icon
            ></span>
            <div>
              <h2 id="preview-title">报告一致性检查</h2>
              <p>演示报告 · 非真实患者数据</p>
            </div>
            <span class="home-preview-label">示例</span>
          </div>
          <dl class="home-report-lines">
            <div>
              <dt>
                <span class="home-field-dot home-dot-teal"></span>影像描述
              </dt>
              <dd>
                <mark class="home-mark-teal">右肺</mark
                >上叶后段见一枚实性结节，大小约 6 mm × 5 mm，边缘较清晰。
              </dd>
            </div>
            <div>
              <dt>
                <span class="home-field-dot home-dot-amber"></span>影像诊断
              </dt>
              <dd>
                <mark class="home-mark-amber">左肺</mark>上叶小结节，建议随访。
              </dd>
            </div>
          </dl>
          <div class="home-preview-finding">
            <span class="home-finding-icon"
              ><el-icon><Warning /></el-icon
            ></span>
            <div>
              <strong>发现侧别差异</strong>
              <p>描述与诊断中的左右侧别不一致</p>
            </div>
            <span class="home-review-label">待人工复核</span>
          </div>
          <figcaption>看见差异，再由专业人员核对确认。</figcaption>
        </figure>
      </section>

      <section
        id="capabilities"
        class="home-capabilities"
        aria-labelledby="capabilities-title"
      >
        <div class="home-section-heading">
          <div>
            <h2 id="capabilities-title">从筛查到复核，一处完成</h2>
            <p>让每一步操作，都有清晰的下一步。</p>
          </div>
          <router-link to="/dashboard" class="home-inline-link"
            >查看质控总览 <el-icon><ArrowRight /></el-icon
          ></router-link>
        </div>
        <div class="home-feature-grid">
          <router-link
            v-for="feature in features"
            :key="feature.path"
            :to="feature.path"
            class="home-feature"
            :class="feature.tone"
          >
            <span class="home-feature-icon"
              ><el-icon><component :is="feature.icon" /></el-icon
            ></span>
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
            <span class="home-feature-link"
              >{{ feature.action }} <el-icon><ArrowRight /></el-icon
            ></span>
          </router-link>
        </div>
      </section>

      <section
        id="workflow"
        class="home-workflow"
        aria-labelledby="workflow-title"
      >
        <div class="home-section-heading">
          <div>
            <h2 id="workflow-title">三步，让质控有迹可循</h2>
            <p>机器辅助识别，专业判断始终在场。</p>
          </div>
        </div>
        <ol class="home-steps">
          <li v-for="(step, index) in steps" :key="step.title">
            <span class="home-step-number">0{{ index + 1 }}</span>
            <div>
              <h3>{{ step.title }}</h3>
              <p>{{ step.description }}</p>
            </div>
          </li>
        </ol>
      </section>

      <section class="home-start" aria-labelledby="start-title">
        <div>
          <h2 id="start-title">从一份报告，开始更细致的质控。</h2>
          <p>导入报告，定位差异，再完成复核与标注。</p>
        </div>
        <router-link to="/batch-process" class="home-button home-button-primary"
          >进入批量质控 <el-icon><ArrowRight /></el-icon
        ></router-link>
      </section>
    </main>

    <footer class="home-footer home-container">
      <span
        >CDU-MED Studio
        <span class="home-footer-divider">/</span> 医学影像报告质控平台</span
      ><span>模型建议仅供辅助参考，最终结果由专业人员确认。</span>
    </footer>
  </div>
</template>

<script setup>
import "./home.css";

const features = [
  {
    path: "/batch-process",
    title: "批量质控",
    icon: "DocumentChecked",
    tone: "home-tone-violet",
    description: "导入报告文件，集中查看异常记录，逐条复核并导出结果。",
    action: "上传报告",
  },
  {
    path: "/medllm",
    title: "知识对话",
    icon: "ChatDotRound",
    tone: "home-tone-teal",
    description: "对照影像描述与诊断，在对话中辅助核对报告内容。",
    action: "开始核对",
  },
  {
    path: "/annotation",
    title: "报告标注",
    icon: "EditPen",
    tone: "home-tone-rose",
    description: "关联描述与诊断片段，将人工判断沉淀为结构化标注。",
    action: "进入标注",
  },
  {
    path: "/dashboard",
    title: "质控工作台",
    icon: "DataAnalysis",
    tone: "home-tone-blue",
    description: "查看报告数量、异常分布与任务进度，掌握质控情况。",
    action: "查看总览",
  },
];
const steps = [
  {
    title: "导入报告",
    description: "上传包含影像描述与诊断的 Excel 或 CSV 文件。",
  },
  {
    title: "筛查差异",
    description: "查看文字、方位以及描述与诊断的一致性问题。",
  },
  {
    title: "复核与留存",
    description: "确认或修正异常，完成关联标注并导出结果。",
  },
];
</script>
