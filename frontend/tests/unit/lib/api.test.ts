import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

import { apiRequest, ApiRequestError } from "@/lib/api";

function createMockResponse({
  ok,
  status,
  statusText,
  json,
}: {
  ok: boolean;
  status: number;
  statusText?: string;
  json: unknown;
}) {
  return {
    ok,
    status,
    statusText: statusText || "",
    json: () => Promise.resolve(json),
  } as Response;
}

describe("apiRequest", () => {
  beforeEach(() => {
    globalThis.fetch = vi.fn();
    localStorage.clear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("sends JSON body and returns parsed response", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      createMockResponse({ ok: true, status: 200, json: { id: 1, name: "Test" } })
    );

    const result = await apiRequest("POST", "/test", { name: "Test" });

    expect(result).toEqual({ id: 1, name: "Test" });
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/test"),
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({ "Content-Type": "application/json" }),
        body: JSON.stringify({ name: "Test" }),
      })
    );
  });

  it("sends FormData without JSON content-type", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      createMockResponse({ ok: true, status: 200, json: { ok: true } })
    );

    const formData = new FormData();
    formData.append("file", new Blob(["content"]));

    await apiRequest("POST", "/upload", formData);

    const call = vi.mocked(fetch).mock.calls[0];
    expect((call[1] as RequestInit).body).toBe(formData);
  });

  it("throws ApiRequestError on non-OK response", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      createMockResponse({ ok: false, status: 400, statusText: "Bad Request", json: { detail: "Bad request" } })
    );

    await expect(apiRequest("GET", "/fail")).rejects.toBeInstanceOf(ApiRequestError);
  });

  it("clears token and throws on 401", async () => {
    localStorage.setItem("access_token", "old-token");
    vi.mocked(fetch).mockResolvedValueOnce(
      createMockResponse({ ok: false, status: 401, json: { detail: "Unauthorized" } })
    );

    await expect(apiRequest("GET", "/me")).rejects.toBeInstanceOf(ApiRequestError);
    expect(localStorage.getItem("access_token")).toBeNull();
  });
});
