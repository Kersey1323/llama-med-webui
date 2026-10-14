import type { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

type BubbleProps = HTMLAttributes<HTMLDivElement> & {
  variant?: "default" | "muted";
};

export function Bubble({
  variant = "default",
  className,
  ...props
}: BubbleProps) {
  return (
    <div
      data-slot="bubble"
      data-variant={variant}
      className={cn(
        "min-w-0 rounded-xl text-sm",
        variant === "muted"
          ? "bg-muted text-zinc-900"
          : "bg-primary text-primary-foreground",
        className,
      )}
      {...props}
    />
  );
}

export function BubbleContent({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      data-slot="bubble-content"
      className={cn(
        "whitespace-pre-wrap break-words px-4 py-3 leading-7 [overflow-wrap:anywhere]",
        className,
      )}
      {...props}
    />
  );
}
