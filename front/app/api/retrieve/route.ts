import { NextResponse } from "next/server";

export const runtime = "nodejs";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function POST(req: Request) {
  try {
    const { tags, order } = await req.json();
    const params = new URLSearchParams();

    if (tags && Array.isArray(tags)) {
      tags.forEach(t => params.append("tags", t));
    }
    
    if (order) params.append("order", order);

    const backendRes = await fetch(
      `${BACKEND_URL}/api/retrieve?${params.toString()}`,
      { method: "GET" }
    );

    const data = await backendRes.json();
    return NextResponse.json(data);

  } catch (e: any) {
    console.error(e);
    return NextResponse.json({ error: true, message: e.message }, { status: 500 });
  }
}
