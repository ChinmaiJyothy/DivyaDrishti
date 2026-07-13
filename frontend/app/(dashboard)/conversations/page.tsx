import { RecentConversations } from "@/components/dashboard/recent-conversations";

export default function ConversationsPage() {
  return (
    <div className="space-y-6 pb-20">
      <h1 className="text-2xl font-bold">Conversations</h1>
      <RecentConversations />
    </div>
  );
}
