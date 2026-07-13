import { Skeleton } from "@/components/ui/skeleton";
import { PageContainer } from "@/components/layout/page-container";

export default function LoadingPage() {
  return (
    <PageContainer>
      <div className="space-y-4">
        <Skeleton className="h-12 w-1/3" />
        <Skeleton className="h-4 w-1/2" />
        <Skeleton className="h-64 w-full" />
      </div>
    </PageContainer>
  );
}
