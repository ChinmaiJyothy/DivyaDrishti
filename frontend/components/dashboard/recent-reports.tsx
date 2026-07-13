"use client";

import { FileText, Trash2, Download, Loader2 } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { useDeleteReport, useReports } from "@/hooks/use-reports";
import { useToast } from "@/hooks/use-toast";
import type { Report } from "@/types";

function statusColor(status: string) {
  switch (status) {
    case "ready":
      return "bg-green-500/10 text-green-600";
    case "failed":
      return "bg-red-500/10 text-red-600";
    default:
      return "bg-amber-500/10 text-amber-600";
  }
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  });
}

export function RecentReports() {
  const { data: reports, isLoading } = useReports();
  const deleteReport = useDeleteReport();
  const toast = useToast();

  const handleDelete = async (id: string) => {
    await deleteReport.mutateAsync(id);
    toast.success("Report deleted");
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-5 w-32" />
        </CardHeader>
        <CardContent className="space-y-3">
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (!reports || reports.length === 0) {
    return (
      <Card>
        <CardContent className="py-6">
          <EmptyState
            icon={FileText}
            title="No reports yet"
            description="Generate a report from Quick Actions to see it here."
          />
        </CardContent>
      </Card>
    );
  }

  const recent = reports.slice(0, 5);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Recent Reports</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {recent.map((report) => (
          <div
            key={report.id}
            className="flex flex-col gap-2 rounded-lg border p-3 transition-colors hover:bg-muted/50 sm:flex-row sm:items-center sm:justify-between"
          >
            <div className="min-w-0">
              <p className="truncate font-medium">{report.title}</p>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <span>{formatDate(report.created_at)}</span>
                <Badge variant="secondary" className={statusColor(report.status)}>
                  {report.status}
                </Badge>
                <span>{report.file_format.toUpperCase()}</span>
              </div>
            </div>
            <div className="flex items-center gap-1">
              {report.file_url && (
                <Button variant="ghost" size="icon" asChild>
                  <a href={report.file_url} download aria-label="Download report">
                    <Download className="h-4 w-4" />
                  </a>
                </Button>
              )}
              <Button
                variant="ghost"
                size="icon"
                onClick={() => handleDelete(report.id)}
                disabled={deleteReport.isPending}
                aria-label="Delete report"
              >
                {deleteReport.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Trash2 className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
