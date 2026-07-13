"use client";

import { useEffect } from "react";

import { Button } from "@/components/ui/button";
import { ErrorState } from "@/components/ui/error-state";
import { PageContainer } from "@/components/layout/page-container";

export default function ErrorPage({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    // eslint-disable-next-line no-console
    console.error(error);
  }, [error]);

  return (
    <PageContainer>
      <ErrorState
        title="Something went wrong"
        description="An unexpected error occurred. Please try again."
        onRetry={reset}
      />
    </PageContainer>
  );
}
