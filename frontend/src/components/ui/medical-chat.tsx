import { Bubble, BubbleContent } from "./c-message-3-utils/bubble";
import { useLayoutEffect } from "react";
import {
  Message,
  MessageContent,
  MessageFooter,
  MessageHeader,
} from "./c-message-3-utils/message";

export type ChatMessage = {
  id: number;
  role: "user" | "assistant" | "failed";
  text: string;
  createdAt: string;
};

export type MedicalChatProps = {
  messages: ChatMessage[];
  pending: boolean;
  demo: boolean;
  onRendered?: () => void;
};

function timeLabel(value: string) {
  return new Date(value).toLocaleTimeString("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}

export function MedicalChat({
  messages,
  pending,
  demo,
  onRendered,
}: MedicalChatProps) {
  useLayoutEffect(() => {
    onRendered?.();
  }, [messages, pending, onRendered]);
  return (
    <div
      className="medical-chat mx-auto flex w-full min-w-0 max-w-4xl flex-col gap-7"
      role="log"
      aria-label="报告核对消息"
      aria-live="polite"
      aria-relevant="additions text"
    >
      {messages.map((message) => (
        <Message
          key={message.id}
          align={message.role === "user" ? "end" : "start"}
          data-role={message.role}
        >
          <MessageContent>
            <MessageHeader className="gap-1.5">
              <span>{message.role === "user" ? "我" : "报告核对助手"}</span>
              <span
                aria-hidden="true"
                className="size-1 shrink-0 rounded-lg bg-muted-foreground/40"
              />
              <time dateTime={message.createdAt}>
                {timeLabel(message.createdAt)}
              </time>
            </MessageHeader>
            <Bubble variant={message.role === "user" ? "default" : "muted"}>
              <BubbleContent>{message.text}</BubbleContent>
            </Bubble>
            <MessageFooter
              className={message.role === "failed" ? "text-red-700" : undefined}
            >
              {message.role === "failed"
                ? "分析失败 · 请稍后重试"
                : message.role === "user"
                  ? "已提交"
                  : demo
                    ? "示例结果"
                    : "分析结果 · 待人工复核"}
            </MessageFooter>
          </MessageContent>
        </Message>
      ))}
      {pending && (
        <Message data-role="pending">
          <MessageContent>
            <MessageHeader>报告核对助手</MessageHeader>
            <Bubble variant="muted">
              <BubbleContent>正在分析影像描述与诊断，请稍候…</BubbleContent>
            </Bubble>
          </MessageContent>
        </Message>
      )}
    </div>
  );
}
