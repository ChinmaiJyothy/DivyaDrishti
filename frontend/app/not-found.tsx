import Link from "next/link";

import { Button } from "@/components/ui/button";
import { PageContainer } from "@/components/layout/page-container";

export default function NotFoundPage() {
  return (
    <PageContainer>
      <div className="flex flex-col items-center justify-center gap-6 text-center">
        <h1 className="font-display text-8xl font-bold text-primary">404</h1>
        <h2 className="font-display text-2xl font-semibold">Page not found</h2>
        <p className="max-w-md text-muted-foreground">
          The page you are looking for does not exist or has been moved.
        </p>
        <Button asChild>
          <Link href="/">Go home</Link>
        </Button>
      </div>
    </PageContainer>
  );
}
