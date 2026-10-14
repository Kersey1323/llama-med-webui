# 知识对话消息组件

现有应用为 Vue 3 + Vite。消息区通过 `src/components/ChatMessages.vue` 挂载一个独立的 React root，表单、请求及会话状态仍由 Vue 管理。离开页面时卸载 React root；切换数据模式或离开页面会取消请求，过期响应不会写入新会话。

## 目录与配置

- `@/components/ui` 对应 `src/components/ui`，是本项目的 shadcn 组件目录。这里的 `/components/ui` 相对于源码根目录，而非文件系统根目录。统一目录能保持提供组件的导入路径、CLI 别名和类型解析一致，无需额外创建另一份根目录 components。
- `src/components/ui/c-message-3.tsx` 和 `demo.tsx` 保留提供的原始示例，英文示例仅用于组件演示，不出现在业务会话中。
- `src/components/ui/c-message-3-utils` 实现原代码缺失的 Bubble、Message 等基础组件；头部始终跟随内容起点，尾部跟随消息方向。
- `src/components/ui/medical-chat.tsx` 使用相同基础组件渲染医学报告消息，接收 `messages`、`pending`、`demo`，不依赖全局 Context。
- 每条消息包含 `id`、`role`（user / assistant / failed）、`text`、`createdAt`。时间来自实际创建时间。“已提交”仅表示请求已提交，不模拟已读回执。
- `src/styles/tailwind.css` 为 Tailwind 样式入口；仅引入 theme 和 utilities，避免 Preflight 重置现有 Vue / Element Plus 样式。`src/studio/studio.css` 继续管理应用布局。
- `components.json` 配置 shadcn 别名；`tsconfig.json` 启用 React JSX 和类型检查；`vite.config.mjs` 启用 Tailwind 插件与自动 JSX 转换。
- 消息不需要照片、外部图片、图标或额外 Provider。支持窄屏换行、长文本、内部滚动和屏幕阅读器的消息播报。

## 安装与运行

本次依赖和配置已完成，正常恢复环境使用：

```bash
cd /mnt/mydrive/project/llama_med_webui/frontend
export PATH=/home/dell/nodejs22/bin:$PATH
npm ci
npm run typecheck
npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
```

从集成前的版本手动补齐依赖时：

```bash
npm install react react-dom clsx tailwind-merge
npm install -D typescript @types/react @types/react-dom tailwindcss @tailwindcss/vite
```

同时保留本次的 tsconfig、components.json、Vite 和样式入口配置。不要在现有 Vue 项目运行创建新 React 工程的命令覆盖应用。以后需要添加 React 版 shadcn 组件，可在本目录运行 `npx shadcn@latest add button`，生成到上述 ui 目录，再由 React 消息区使用；Vue 页面不能直接渲染 React 组件。

## 验证与接口边界

`npm run typecheck` 检查新增 React/TypeScript 模块，`npm run build` 构建完整应用。真实模式继续 POST `/api/process`；服务失败显示明确的失败消息，示例模式明确标为示例结果。前端接入不等于已部署模型服务。
