import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// Must mock fetch before importing api-client
const mockFetch = vi.fn();
vi.stubGlobal("fetch", mockFetch);

describe("api-client", () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("apiGet makes GET request and returns JSON", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: "ok" }),
    });

    const { apiGet } = await import("@/lib/api-client");
    const result = await apiGet<{ status: string }>("/health");
    expect(result).toEqual({ status: "ok" });
    expect(mockFetch).toHaveBeenCalledTimes(1);
  });

  it("apiGet throws on non-ok response", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({ detail: "server error" }),
    });

    const { apiGet } = await import("@/lib/api-client");
    await expect(apiGet("/fail")).rejects.toThrow();
  });

  it("apiPost sends body as JSON", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 1 }),
    });

    const { apiPost } = await import("@/lib/api-client");
    await apiPost("/items", { name: "test" });

    const [, options] = mockFetch.mock.calls[0];
    expect(options.method).toBe("POST");
    expect(options.body).toContain("test");
  });

  it("checkHealth returns true on success", async () => {
    mockFetch.mockResolvedValueOnce({ ok: true });

    const { checkHealth } = await import("@/lib/api-client");
    const result = await checkHealth();
    expect(result).toBe(true);
  });

  it("checkHealth returns false on failure", async () => {
    mockFetch.mockRejectedValueOnce(new Error("network error"));

    const { checkHealth } = await import("@/lib/api-client");
    const result = await checkHealth();
    expect(result).toBe(false);
  });
});
