import { PageContainer } from "@/components/layout/page-container";
import { EmptyState } from "@/components/ui/empty-state";

export default function HomePage() {
  return (
    <PageContainer>
      <EmptyState
        title="Frontend Foundation"
        description="The design system, theme engine, and layout shell are ready for future features."
      />
    </PageContainer>
  );
}
