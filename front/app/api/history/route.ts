import { NextResponse } from "next/server";

export const runtime = "nodejs";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "https://altur-backend.fly.dev";

export async function GET() {
  try {
    const resp = await fetch(`${BACKEND_URL}/api/history`, { cache: "no-store" });
    const data = await resp.json();
    return NextResponse.json(data, { status: resp.status });
  } catch (err) {
    console.error("basic_history proxy error:", err);
    return NextResponse.json({ error: "Failed to fetch history" }, { status: 500 });
  }
}