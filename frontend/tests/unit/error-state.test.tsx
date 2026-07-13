import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ErrorState } from "@/components/ui/error-state";

describe("ErrorState", () => {
  it("renders title and description", () => {
    render(<ErrorState title="Oops" description="Something failed" />);
    expect(screen.getByText("Oops")).toBeInTheDocument();
    expect(screen.getByText("Something failed")).toBeInTheDocument();
  });

  it("calls onRetry when retry is clicked", () => {
    const retry = vi.fn();
    render(<ErrorState title="Error" onRetry={retry} />);
    const button = screen.getByRole("button", { name: /Try again/i });
    button.click();
    expect(retry).toHaveBeenCalled();
  });
});
