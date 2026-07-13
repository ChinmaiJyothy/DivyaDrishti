import { Construction } from "lucide-react";

import { PageContainer } from "@/components/layout/page-container";

export default function MaintenancePage() {
  return (
    <PageContainer>
      <div className="flex flex-col items-center justify-center gap-6 text-center">
        <Construction className="h-16 w-16 text-saffron-500" aria-hidden="true" />
        <h1 className="font-display text-3xl font-semibold">Under maintenance</h1>
        <p className="max-w-md text-muted-foreground">
          We are improving the experience. Please check back soon.
        </p>
      </div>
    </PageContainer>
  );
}
