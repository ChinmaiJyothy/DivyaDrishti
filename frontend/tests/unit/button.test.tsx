import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { Button } from "@/components/ui/button";

describe("Button", () => {
  it("renders label and is clickable", () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    const button = screen.getByRole("button", { name: /Click me/i });
    expect(button).toBeInTheDocument();
    button.click();
    expect(handleClick).toHaveBeenCalled();
  });

  it("disables while loading", () => {
    render(<Button isLoading>Loading</Button>);
    const button = screen.getByRole("button", { name: /Loading/i });
    expect(button).toBeDisabled();
    expect(button).toHaveAttribute("aria-busy", "true");
  });
});
