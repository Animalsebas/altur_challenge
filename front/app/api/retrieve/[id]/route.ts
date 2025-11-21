import { NextResponse } from "next/server";

export const runtime = "nodejs";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function POST(req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  try {
    const backendRes = await fetch(`${BACKEND_URL}/api/retrieve/${id}`, {
      method: "GET",
    });

    const data = await backendRes.json();
    return NextResponse.json(data);

  } catch (e: any) {
    console.error(e);
    return NextResponse.json({ error: true, message: e.message }, { status: 500 });
  }
}
