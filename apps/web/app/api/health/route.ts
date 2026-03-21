import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET() {
  const serverUrl = process.env.INTERNAL_API_BASE_URL ?? process.env.API_BASE_URL;
  const publicUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
  const effectiveUrl = serverUrl ?? publicUrl;

  const result: Record<string, unknown> = {
    INTERNAL_API_BASE_URL: serverUrl ?? "(not set)",
    NEXT_PUBLIC_API_BASE_URL: publicUrl ?? "(not set)",
    effective_url: effectiveUrl ?? "(none)",
  };

  if (effectiveUrl) {
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 10_000);
      const start = Date.now();
      const res = await fetch(`${effectiveUrl}/dashboard/summary`, {
        cache: "no-store",
        signal: controller.signal,
      });
      clearTimeout(timeout);
      result.api_status = res.status;
      result.api_ok = res.ok;
      result.api_latency_ms = Date.now() - start;
      if (res.ok) {
        const body = await res.json();
        result.api_keys = Object.keys(body);
      } else {
        result.api_body = await res.text().catch(() => "(unreadable)");
      }
    } catch (err) {
      result.api_error = err instanceof Error ? err.message : String(err);
    }
  }

  return NextResponse.json(result);
}
