import { NextResponse } from "next/server";

export const runtime = "nodejs";

export async function GET(req: Request, { params }: { params: { id: string } }) {
  const { id } = params;
  try {
    const resp = await fetch(`http://localhost:8000/api/history/${encodeURIComponent(id)}`, {
      cache: "no-store",
    });
    const data = await resp.json();
    return NextResponse.json(data, { status: resp.status });
  } catch (err) {
    console.error("analysis_details/[id] proxy error:", err);
    return NextResponse.json({ error: "Failed to fetch history item" }, { status: 500 });
  }
}