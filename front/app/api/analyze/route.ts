import { NextResponse } from "next/server";

export const runtime = "nodejs";
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function POST(req: Request) {
  try {
    const formData = await req.formData();

    const backendEndpoint = `${BACKEND_URL}/api/analyze`;

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 600000); // 10 minutes

    const response = await fetch(backendEndpoint, {
      method: "POST",
      body: formData,
      signal: controller.signal,
    });

    clearTimeout(timeout);

    if (!response.ok) {
      const errBody = await response.text().catch(() => null);
      return NextResponse.json(
        { error: "Failed to analyze the audio file", details: errBody },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("Error in API route:", error);
    if ((error as any).name === "AbortError") {
      return NextResponse.json({ error: "Request timed out (Next.js)" }, { status: 504 });
    }
    return NextResponse.json(
      { error: "An error occurred while processing the request" },
      { status: 500 }
    );
  }
}