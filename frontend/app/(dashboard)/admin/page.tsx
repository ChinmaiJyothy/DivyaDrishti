"use client";

import { Shield } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { KnowledgeCard } from "@/components/dashboard/knowledge-card";
import { useKnowledgeVersions } from "@/hooks/use-knowledge";
import { useAuth } from "@/providers/auth-provider";

export default function AdminPage() {
  const { user, isLoading } = useAuth();
  const { data: versions, isLoading: versionsLoading } = useKnowledgeVersions();

  const isAdmin = user?.is_superuser || user?.role === "admin" || user?.role === "super_admin";

  if (isLoading) {
    return (
      <div className="space-y-6 pb-20">
        <h1 className="text-2xl font-bold">Admin</h1>
        <Skeleton className="h-40 w-full" />
      </div>
    );
  }

  if (!isAdmin) {
    return (
      <div className="pb-20">
        <EmptyState icon={Shield} title="Admin only" description="You do not have access to this page." />
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-20">
      <h1 className="text-2xl font-bold">Admin</h1>
      <KnowledgeCard />
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Knowledge Versions</CardTitle>
        </CardHeader>
        <CardContent>
          {versionsLoading ? (
            <Skeleton className="h-32 w-full" />
          ) : !versions || versions.length === 0 ? (
            <p className="text-sm text-muted-foreground">No knowledge versions available.</p>
          ) : (
            <div className="space-y-2">
              {versions.map((version) => (
                <div key={version.id} className="rounded-lg border p-3 text-sm">
                  <p className="font-medium">{version.rule_id} v{version.version}</p>
                  <p className="text-muted-foreground">{version.approval_status} • {version.deprecated ? "Deprecated" : "Active"}</p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
