import { NextResponse } from "next/server";

export const runtime = "nodejs";

export async function POST(req: Request) {
  try {
    const formData = await req.formData();

    // Forward the request to the FastAPI backend
    const response = await fetch("http://localhost:8000/api/analyze", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: "Failed to analyze the audio file" },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error in API route:", error);
    return NextResponse.json(
      { error: "An error occurred while processing the request" },
      { status: 500 }
    );
  }
}