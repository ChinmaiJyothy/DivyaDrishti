"use client";

import { Check, Copy } from "lucide-react";
import { useState } from "react";
import ReactMarkdown, { type Components, type ExtraProps } from "react-markdown";
import remarkGfm from "remark-gfm";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { useToast } from "@/hooks/use-toast";
import type { Message } from "@/types";

interface MessageBubbleProps extends React.HTMLAttributes<HTMLDivElement> {
  message: Message;
}

function CodeBlock({
  node: _node,
  inline,
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLElement> & ExtraProps & { inline?: boolean }) {
  const { success, error } = useToast();
  const [copied, setCopied] = useState(false);

  const handleCopy = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation();
    const code = String(children).replace(/\n$/, "");
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      success("Copied to clipboard");
      setTimeout(() => setCopied(false), 2000);
    } catch {
      error("Failed to copy");
    }
  };

  if (inline) {
    return (
      <code
        className={cn("rounded bg-background px-1 py-0.5 font-mono text-sm", className)}
        {...props}
      >
        {children}
      </code>
    );
  }

  const language = /language-(\w+)/.exec(className || "")?.[1];

  return (
    <div className="group relative my-2">
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className="absolute right-2 top-2 h-7 w-7 opacity-0 transition-opacity group-hover:opacity-100"
        aria-label="Copy code"
        onClick={handleCopy}
      >
        {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
      </Button>
      {language && (
        <span className="absolute left-3 top-2 text-xs font-medium text-muted-foreground">
          {language}
        </span>
      )}
      <pre
        className={cn(
          "overflow-x-auto rounded-md bg-background p-4 pt-8 font-mono text-sm",
          className
        )}
      >
        <code className={cn("font-mono text-sm", className)} {...props}>
          {children}
        </code>
      </pre>
    </div>
  );
}

function Pre({
  node: _node,
  children,
}: React.HTMLAttributes<HTMLPreElement> & ExtraProps) {
  return <>{children}</>;
}

function Paragraph({
  node: _node,
  children,
  className,
  ...props
}: React.HTMLAttributes<HTMLParagraphElement> & ExtraProps) {
  return (
    <p className={cn("mb-2 last:mb-0", className)} {...props}>
      {children}
    </p>
  );
}

function Link({
  node: _node,
  children,
  className,
  href,
  target,
  ...props
}: React.AnchorHTMLAttributes<HTMLAnchorElement> & ExtraProps) {
  return (
    <a
      className={cn("text-inherit underline hover:opacity-80", className)}
      href={href}
      target={target ?? "_blank"}
      rel="noopener noreferrer"
      {...props}
    >
      {children}
    </a>
  );
}

function UnorderedList({
  node: _node,
  children,
  className,
  ...props
}: React.HTMLAttributes<HTMLUListElement> & ExtraProps) {
  return (
    <ul className={cn("mb-2 list-disc pl-5 last:mb-0", className)} {...props}>
      {children}
    </ul>
  );
}

function OrderedList({
  node: _node,
  children,
  className,
  ...props
}: React.HTMLAttributes<HTMLOListElement> & ExtraProps) {
  return (
    <ol className={cn("mb-2 list-decimal pl-5 last:mb-0", className)} {...props}>
      {children}
    </ol>
  );
}

function ListItem({
  node: _node,
  children,
  className,
  ...props
}: React.LiHTMLAttributes<HTMLLIElement> & ExtraProps) {
  return (
    <li className={cn("mb-1", className)} {...props}>
      {children}
    </li>
  );
}

function Heading1({
  node: _node,
  children,
  className,
  ...props
}: React.HTMLAttributes<HTMLHeadingElement> & ExtraProps) {
  return (
    <h1 className={cn("mb-2 text-lg font-semibold", className)} {...props}>
      {children}
    </h1>
  );
}

function Heading2({
  node: _node,
  children,
  className,
  ...props
}: React.HTMLAttributes<HTMLHeadingElement> & ExtraProps) {
  return (
    <h2 className={cn("mb-2 text-base font-semibold", className)} {...props}>
      {children}
    </h2>
  );
}

function Heading3({
  node: _node,
  children,
  className,
  ...props
}: React.HTMLAttributes<HTMLHeadingElement> & ExtraProps) {
  return (
    <h3 className={cn("mb-1 text-sm font-semibold", className)} {...props}>
      {children}
    </h3>
  );
}

function MarkdownTable({
  node: _node,
  children,
  className,
  ...props
}: React.TableHTMLAttributes<HTMLTableElement> & ExtraProps) {
  return (
    <div className="my-2 overflow-x-auto">
      <table className={cn("w-full border-collapse text-sm", className)} {...props}>
        {children}
      </table>
    </div>
  );
}

function TableHeader({
  node: _node,
  children,
  className,
  ...props
}: React.ThHTMLAttributes<HTMLTableHeaderCellElement> & ExtraProps) {
  return (
    <th className={cn("border bg-muted px-2 py-1 text-left font-semibold", className)} {...props}>
      {children}
    </th>
  );
}

function TableCell({
  node: _node,
  children,
  className,
  ...props
}: React.TdHTMLAttributes<HTMLTableDataCellElement> & ExtraProps) {
  return (
    <td className={cn("border px-2 py-1", className)} {...props}>
      {children}
    </td>
  );
}

const markdownComponents: Components = {
  code: CodeBlock,
  pre: Pre,
  p: Paragraph,
  a: Link,
  ul: UnorderedList,
  ol: OrderedList,
  li: ListItem,
  h1: Heading1,
  h2: Heading2,
  h3: Heading3,
  table: MarkdownTable,
  th: TableHeader,
  td: TableCell,
};

export function MessageBubble({ message, className, ...props }: MessageBubbleProps) {
  return (
    <Card
      className={cn(
        "w-fit max-w-full px-4 py-3",
        message.role === "user" &&
          "self-end bg-primary text-primary-foreground",
        message.role === "assistant" &&
          "self-start bg-muted text-foreground",
        className
      )}
      {...props}
    >
      {message.role === "user" ? (
        <p className="whitespace-pre-wrap text-sm">{message.content}</p>
      ) : (
        <div className="text-sm leading-relaxed">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={markdownComponents}
          >
            {message.content}
          </ReactMarkdown>
        </div>
      )}
    </Card>
  );
}
