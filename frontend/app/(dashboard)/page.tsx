import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { DashboardStats } from "@/components/dashboard/dashboard-stats";
import { QuickActions } from "@/components/dashboard/quick-actions";
import { RecentConversations } from "@/components/dashboard/recent-conversations";
import { RecentReports } from "@/components/dashboard/recent-reports";
import { KnowledgeCard } from "@/components/dashboard/knowledge-card";
import { PlanetaryOverview } from "@/components/dashboard/planetary-overview";

export default function DashboardPage() {
  return (
    <div className="space-y-6 pb-20">
      <DashboardHeader />
      <DashboardStats />
      <QuickActions />
      <div className="grid gap-6 lg:grid-cols-2">
        <RecentConversations />
        <RecentReports />
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <KnowledgeCard />
        <PlanetaryOverview />
      </div>
    </div>
  );
}
