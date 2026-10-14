import type { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

type MessageProps = HTMLAttributes<HTMLDivElement> & {
  align?: "start" | "end";
};

export function Message({
  align = "start",
  className,
  ...props
}: MessageProps) {
  return (
    <div
      data-slot="message"
      data-align={align}
      className={cn(
        "group/message flex w-full min-w-0",
        align === "end" ? "justify-end" : "justify-start",
        className,
      )}
      {...props}
    />
  );
}

export function MessageContent({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      data-slot="message-content"
      className={cn(
        "flex min-w-0 max-w-full flex-col gap-2 sm:max-w-[88%]",
        className,
      )}
      {...props}
    />
  );
}

export function MessageHeader({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      data-slot="message-header"
      className={cn(
        "flex items-center self-start px-4 text-xs text-muted-foreground",
        className,
      )}
      {...props}
    />
  );
}

export function MessageFooter({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      data-slot="message-footer"
      className={cn(
        "flex items-center self-start px-4 text-xs text-muted-foreground group-data-[align=end]/message:self-end",
        className,
      )}
      {...props}
    />
  );
}
