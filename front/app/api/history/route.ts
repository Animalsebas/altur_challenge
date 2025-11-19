import { NextResponse } from "next/server";

export const runtime = "nodejs";

export async function GET() {
  try {
    const resp = await fetch("http://localhost:8000/api/history", { cache: "no-store" });
    const data = await resp.json();
    return NextResponse.json(data, { status: resp.status });
  } catch (err) {
    console.error("basic_history proxy error:", err);
    return NextResponse.json({ error: "Failed to fetch history" }, { status: 500 });
  }
}