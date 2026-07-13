"use client";

import { useEffect } from "react";

import { Button } from "@/components/ui/button";

export default function GlobalErrorPage({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => {
    // eslint-disable-next-line no-console
    console.error(error);
  }, [error]);

  return (
    <html lang="en">
      <body>
        <div className="flex min-h-screen flex-col items-center justify-center gap-6 p-4 text-center">
          <h1 className="font-display text-8xl font-bold text-primary">500</h1>
          <h2 className="font-display text-2xl font-semibold">Internal Server Error</h2>
          <p className="max-w-md text-muted-foreground">
            Something went wrong on our end. Please try again.
          </p>
          <Button onClick={() => reset()}>Try again</Button>
        </div>
      </body>
    </html>
  );
}
