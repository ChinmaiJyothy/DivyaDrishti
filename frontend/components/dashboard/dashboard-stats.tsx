"use client";

import { BookOpen, FileText, MessageSquare, Users } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useBirthProfiles } from "@/hooks/use-birth-profiles";
import { useConversations } from "@/hooks/use-conversations";
import { useKnowledgeOverview } from "@/hooks/use-knowledge";
import { useReports } from "@/hooks/use-reports";
import { cn } from "@/lib/utils";

interface Stat {
  label: string;
  value: number;
  icon: typeof Users;
  className: string;
}

function StatCard({ stat, isLoading }: { stat: Stat; isLoading: boolean }) {
  return (
    <Card>
      <CardContent className="flex items-center gap-4 p-4">
        <div className={cn("rounded-lg p-3", stat.className)}>
          <stat.icon className="h-5 w-5" />
        </div>
        <div>
          <p className="text-sm text-muted-foreground">{stat.label}</p>
          {isLoading ? (
            <Skeleton className="mt-1 h-6 w-12" />
          ) : (
            <p className="text-2xl font-bold">{stat.value}</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export function DashboardStats() {
  const { data: profiles, isLoading: profilesLoading } = useBirthProfiles();
  const { data: conversations, isLoading: conversationsLoading } = useConversations();
  const { data: reports, isLoading: reportsLoading } = useReports();
  const { data: knowledge, isLoading: knowledgeLoading } = useKnowledgeOverview();

  const isLoading = profilesLoading || conversationsLoading || reportsLoading || knowledgeLoading;

  const stats: Stat[] = [
    {
      label: "Profiles",
      value: profiles?.length || 0,
      icon: Users,
      className: "bg-blue-500/10 text-blue-600",
    },
    {
      label: "Conversations",
      value: conversations?.length || 0,
      icon: MessageSquare,
      className: "bg-amber-500/10 text-amber-600",
    },
    {
      label: "Reports",
      value: reports?.length || 0,
      icon: FileText,
      className: "bg-purple-500/10 text-purple-600",
    },
    {
      label: "Knowledge",
      value: (knowledge?.books_count || 0) + (knowledge?.versions_count || 0),
      icon: BookOpen,
      className: "bg-emerald-500/10 text-emerald-600",
    },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat) => (
        <StatCard key={stat.label} stat={stat} isLoading={isLoading} />
      ))}
    </div>
  );
}
