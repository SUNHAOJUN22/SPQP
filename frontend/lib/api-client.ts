const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  signal?: AbortSignal
): Promise<T> {
  const url = `${API_BASE}${path}`;
  const headers: HeadersInit = {};
  let bodyStr: BodyInit | undefined;

  if (body !== undefined && body !== null) {
    headers["Content-Type"] = "application/json";
    bodyStr = JSON.stringify(body);
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 30_000);
  const mergedSignal = signal ?? controller.signal;

  let lastError: Error | null = null;
  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      const res = await fetch(url, {
        method,
        headers,
        body: bodyStr,
        signal: mergedSignal,
      });
      clearTimeout(timeout);

      if (!res.ok) {
        const text = await res.text().catch(() => "");
        let msg = `请求失败 (${res.status})`;
        try {
          const json = JSON.parse(text);
          msg = json.detail ?? json.message ?? msg;
        } catch {
          if (text) msg = text;
        }
        throw new ApiError(msg, res.status);
      }

      return (await res.json()) as T;
    } catch (err) {
      clearTimeout(timeout);
      if (err instanceof ApiError) throw err;
      lastError = err instanceof Error ? err : new Error(String(err));
      if (attempt === 0 && !signal?.aborted) {
        await new Promise((r) => setTimeout(r, 500));
        continue;
      }
    }
  }

  throw lastError ?? new Error("网络请求失败，请检查后端是否已启动。");
}

export function apiGet<T>(path: string, signal?: AbortSignal): Promise<T> {
  return request<T>("GET", path, undefined, signal);
}

export function apiPost<T>(
  path: string,
  body?: unknown,
  signal?: AbortSignal
): Promise<T> {
  return request<T>("POST", path, body, signal);
}

export async function apiUpload<T>(
  path: string,
  file: File,
  signal?: AbortSignal
): Promise<T> {
  const url = `${API_BASE}${path}`;
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(url, { method: "POST", body: form, signal });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    let msg = `上传失败 (${res.status})`;
    try {
      const json = JSON.parse(text);
      msg = json.detail ?? json.message ?? msg;
    } catch {
      if (text) msg = text;
    }
    throw new ApiError(msg, res.status);
  }

  return (await res.json()) as T;
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`, {
      signal: AbortSignal.timeout(5000),
    });
    return res.ok;
  } catch {
    return false;
  }
}
