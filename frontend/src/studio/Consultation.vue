<template>
  <div class="conversation-grid">
    <section
      class="bg-white panel consult-form rounded-xl border border-zinc-200 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-150"
    >
      <div class="panel-head">
        <div>
          <h2>报告信息</h2>
          <p>完整输入描述和诊断，便于对照分析</p>
        </div>
        <span class="count-pill">报告助手</span>
      </div>
      <div class="panel-body">
        <div>
          <label for="image-description">影像描述</label
          ><el-input
            id="image-description"
            v-model="description"
            type="textarea"
            :rows="6"
            placeholder="请输入影像检查所见…"
            :disabled="pending"
            class="bg-zinc-100 border-0 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/30 transition-colors duration-150"
          />
        </div>
        <div>
          <label for="image-diagnosis">影像诊断</label
          ><el-input
            id="image-diagnosis"
            v-model="diagnosis"
            type="textarea"
            :rows="4"
            placeholder="请输入待核对的原始诊断…"
            :disabled="pending"
            class="bg-zinc-100 border-0 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/30 transition-colors duration-150"
          />
        </div>
        <div class="form-end">
          <el-button
            type="primary"
            :disabled="!description.trim() || !diagnosis.trim()"
            :loading="pending"
            @click="submit"
            class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
            ><el-icon v-if="!pending"><Position /></el-icon>&nbsp;{{
              studio.demo ? "查看示例分析" : "开始分析"
            }}</el-button
          ><el-button
            text
            :disabled="pending"
            @click="fillSample"
            class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
            >填入示例报告</el-button
          >
          <div class="sample-prompt">
            请勿输入患者姓名、身份证号等个人信息。分析结果需要专业人员复核。
          </div>
        </div>
      </div>
    </section>
    <section
      class="bg-white panel consult-history rounded-xl border border-zinc-200 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-150"
    >
      <div class="panel-head" style="border-bottom: 1px solid var(--border)">
        <div>
          <h2>报告核对助手</h2>
          <p>
            {{ studio.demo ? "示例预览 · 固定示例分析" : "提交报告后开始分析" }}
          </p>
        </div>
        <div class="panel-actions">
          <el-button
            :disabled="pending"
            @click="clear"
            class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
            ><el-icon><Plus /></el-icon>&nbsp;新建对话</el-button
          >
          <span class="count-pill">{{
            messages.length ? messages.length + " 条消息" : "新会话"
          }}</span>
        </div>
      </div>
      <div class="consult-messages" ref="chatBox">
        <div class="consult-welcome" v-if="!messages.length">
          <span class="welcome-icon"><ChatDotRound /></span>
          <h2>一起看清报告的每一处细节</h2>
          <p>
            在左侧输入影像描述与诊断，开始本次核对。<br />重点关注文字、方位以及描述与诊断的一致性。
          </p>
          <el-button
            plain
            style="margin-top: 25px"
            @click="fillSample"
            class="rounded-lg text-sm font-medium transition-colors px-4 py-2 md:px-6 md:py-3 duration-150 active:scale-95"
            >从一份示例报告开始 →</el-button
          >
        </div>
        <ChatMessages
          v-if="messages.length || pending"
          :messages="messages"
          :pending="pending"
          :demo="studio.demo"
          @rendered="scroll"
        />
      </div>
    </section>
  </div>
</template>
<script setup>
import { ref, watch, nextTick, onBeforeUnmount } from "vue";
import ChatMessages from "../components/ChatMessages.vue";
import api from "../utils/axios";
import { studio } from "./store";
const description = ref(""),
  diagnosis = ref(""),
  messages = ref([]),
  pending = ref(false),
  chatBox = ref(null);
let nextMessageId = 0,
  requestVersion = 0,
  controller;
function addMessage(role, text) {
  messages.value.push({
    id: ++nextMessageId,
    role,
    text,
    createdAt: new Date().toISOString(),
  });
}
const sampleDescription =
  "右肺上叶后段见一枚实性结节，大小约 6 mm × 5 mm，边缘较清晰。双肺其余未见明显异常密度影。";
const sampleDiagnosis = "左肺上叶小结节，建议随访。";
function fillSample() {
  if (pending.value) return;
  description.value = sampleDescription;
  diagnosis.value = sampleDiagnosis;
}
function clear() {
  requestVersion++;
  controller?.abort();
  pending.value = false;
  messages.value = [];
  description.value = "";
  diagnosis.value = "";
}
watch(() => studio.demo, clear);
onBeforeUnmount(() => {
  requestVersion++;
  controller?.abort();
});
function stringify(result) {
  return typeof result === "string" ? result : JSON.stringify(result, null, 2);
}
async function scroll() {
  await nextTick();
  if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight;
}
async function submit() {
  if (pending.value || !description.value.trim() || !diagnosis.value.trim())
    return;
  const version = ++requestVersion;
  controller = new AbortController();
  addMessage(
    "user",
    `影像描述：${description.value}\n\n影像诊断：${diagnosis.value}`,
  );
  pending.value = true;
  scroll();
  const demoAtStart = studio.demo;
  try {
    let response;
    if (studio.demo) {
      response =
        description.value === sampleDescription &&
        diagnosis.value === sampleDiagnosis
          ? "【固定示例分析】\n\n发现侧别不一致：影像描述为“右肺上叶”，原始诊断为“左肺上叶”。\n\n修改建议：核对原始影像与患者资料；如描述侧别无误，诊断可复核为“右肺上叶小结节，建议随访”。\n\n该示例用于展示界面，不代表真实模型结果。"
          : "【示例预览】\n当前模式仅提供固定示例的界面演示，未对你输入的报告进行模型分析。请点击“填入示例报告”体验，或切换“真实任务”连接模型服务。";
    } else {
      const { data } = await api.post(
        "/api/process",
        { desc: description.value, true_report: diagnosis.value },
        { timeout: 180000, signal: controller.signal },
      );
      if (data.status === "error" || data.error) throw new Error("分析失败");
      response = stringify(data.generated_report || data);
    }
    if (version === requestVersion && demoAtStart === studio.demo)
      addMessage("assistant", response);
  } catch {
    if (version === requestVersion && demoAtStart === studio.demo)
      addMessage(
        "failed",
        "分析未完成，暂时无法连接报告分析服务。输入内容已保留，请稍后重试。",
      );
  } finally {
    if (version === requestVersion) {
      pending.value = false;
      scroll();
    }
  }
}
</script>
