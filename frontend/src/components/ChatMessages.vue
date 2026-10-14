<template><div ref="container" class="chat-message-mount" /></template>

<script setup>
import { onMounted, onBeforeUnmount, ref, watch } from "vue";
import { createElement } from "react";
import { createRoot } from "react-dom/client";
import { MedicalChat } from "./ui/medical-chat";

const props = defineProps({
  messages: { type: Array, default: () => [] },
  pending: { type: Boolean, default: false },
  demo: { type: Boolean, default: false },
});
const emit = defineEmits(["rendered"]);
const onRendered = () => emit("rendered");
const container = ref(null);
let root;
function render() {
  // Copy Vue proxies into plain props at the framework boundary.
  root?.render(
    createElement(MedicalChat, {
      messages: props.messages.map((message) => ({ ...message })),
      pending: props.pending,
      demo: props.demo,
      onRendered,
    }),
  );
}
onMounted(() => {
  root = createRoot(container.value);
  render();
});
watch(() => [props.messages, props.pending, props.demo], render, {
  deep: true,
});
onBeforeUnmount(() => root?.unmount());
</script>
