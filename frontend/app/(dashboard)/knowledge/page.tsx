import { KnowledgeCard } from "@/components/dashboard/knowledge-card";

export default function KnowledgePage() {
  return (
    <div className="space-y-6 pb-20">
      <h1 className="text-2xl font-bold">Knowledge Library</h1>
      <KnowledgeCard />
    </div>
  );
}
