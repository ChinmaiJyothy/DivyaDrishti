"use client";

import type { LucideIcon } from "lucide-react";
import {
  Briefcase,
  FileText,
  HeartPulse,
  Heart,
  Landmark,
  Loader2,
  MessageCircleQuestion,
  Upload,
} from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useCreateConversation } from "@/hooks/use-conversations";
import { useCreateReport } from "@/hooks/use-reports";
import { useUploadBook } from "@/hooks/use-knowledge";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";
import { useAuth } from "@/providers/auth-provider";

interface Action {
  label: string;
  description: string;
  icon: LucideIcon;
  color: string;
  admin?: boolean;
  onClick: () => void;
}

function AskQuestionDialog({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const createConversation = useCreateConversation();
  const [title, setTitle] = useState("");
  const [domain, setDomain] = useState("general");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await createConversation.mutateAsync({ title, domain });
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Ask a Question</DialogTitle>
          <DialogDescription>Start a new conversation with DivyaDrishti.</DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="title">Question</Label>
            <Input
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="What would you like to know?"
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="domain">Category</Label>
            <Select value={domain} onValueChange={setDomain}>
              <SelectTrigger id="domain">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="general">General</SelectItem>
                <SelectItem value="career">Career</SelectItem>
                <SelectItem value="marriage">Marriage</SelectItem>
                <SelectItem value="finance">Finance</SelectItem>
                <SelectItem value="health">Health</SelectItem>
                <SelectItem value="compatibility">Compatibility</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <Button type="submit" disabled={createConversation.isPending}>
            {createConversation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Start Conversation
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function UploadBookDialog({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const upload = useUploadBook();
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    await upload.mutateAsync({ file, title });
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Upload Knowledge Book</DialogTitle>
          <DialogDescription>Upload a Vedic astrology text to the knowledge base.</DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="book-title">Title</Label>
            <Input id="book-title" value={title} onChange={(e) => setTitle(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="book-file">File</Label>
            <Input
              id="book-file"
              type="file"
              accept=".pdf,.epub,.txt"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />
          </div>
          <Button type="submit" disabled={upload.isPending || !file}>
            {upload.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Upload
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export function QuickActions() {
  const toast = useToast();
  const { user } = useAuth();
  const createConversation = useCreateConversation();
  const createReport = useCreateReport();
  const [askOpen, setAskOpen] = useState(false);
  const [uploadOpen, setUploadOpen] = useState(false);

  const isAdmin = user?.is_superuser || user?.role === "admin" || user?.role === "super_admin";

  const createConversationByDomain = async (domain: string) => {
    await createConversation.mutateAsync({ title: `${domain} reading`, domain });
    toast.success("Conversation started");
  };

  const generateReport = async (title: string, category: string) => {
    await createReport.mutateAsync({ title, category });
    toast.success("Report requested");
  };

  const actions: Action[] = [
    {
      label: "Ask a Question",
      description: "Start a conversation",
      icon: MessageCircleQuestion,
      color: "bg-blue-500/10 text-blue-600",
      onClick: () => setAskOpen(true),
    },
    {
      label: "Generate Horoscope",
      description: "Full horoscope report",
      icon: FileText,
      color: "bg-purple-500/10 text-purple-600",
      onClick: () => generateReport("Full Horoscope", "full_horoscope"),
    },
    {
      label: "Career Reading",
      description: "Professional guidance",
      icon: Briefcase,
      color: "bg-amber-500/10 text-amber-600",
      onClick: () => createConversationByDomain("career"),
    },
    {
      label: "Marriage Reading",
      description: "Relationship insights",
      icon: Heart,
      color: "bg-rose-500/10 text-rose-600",
      onClick: () => createConversationByDomain("marriage"),
    },
    {
      label: "Finance Reading",
      description: "Wealth analysis",
      icon: Landmark,
      color: "bg-emerald-500/10 text-emerald-600",
      onClick: () => createConversationByDomain("finance"),
    },
    {
      label: "Health Reading",
      description: "Wellness guidance",
      icon: HeartPulse,
      color: "bg-red-500/10 text-red-600",
      onClick: () => createConversationByDomain("health"),
    },
    {
      label: "Compatibility",
      description: "Match analysis",
      icon: Heart,
      color: "bg-pink-500/10 text-pink-600",
      onClick: () => createConversationByDomain("compatibility"),
    },
    {
      label: "Upload Knowledge Book",
      description: "Admin only",
      icon: Upload,
      color: "bg-slate-500/10 text-slate-600",
      admin: true,
      onClick: () => setUploadOpen(true),
    },
  ];

  const visibleActions = actions.filter((a) => !a.admin || isAdmin);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Quick Actions</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
          {visibleActions.map((action) => (
            <button
              key={action.label}
              onClick={action.onClick}
              className="flex flex-col items-start rounded-xl border bg-card p-4 text-left transition-all hover:-translate-y-1 hover:shadow-sm focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <div className={cn("mb-3 rounded-lg p-2", action.color)}>
                <action.icon className="h-5 w-5" />
              </div>
              <span className="font-medium">{action.label}</span>
              <span className="text-xs text-muted-foreground">{action.description}</span>
            </button>
          ))}
        </div>
      </CardContent>
      <AskQuestionDialog open={askOpen} onOpenChange={setAskOpen} />
      <UploadBookDialog open={uploadOpen} onOpenChange={setUploadOpen} />
    </Card>
  );
}
