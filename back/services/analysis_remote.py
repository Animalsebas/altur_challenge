import os
import json
import re
from openai import OpenAI
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4o-mini" 

def _chat(prompt: str) -> str:
    """
    Wrapper to send a prompt to OpenAI and return clean text.
    """
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        raise RuntimeError(f"OpenAI request failed: {str(e)}")


def analyze_transcription_remote(transcription: str):
    """
    Mirrors analyze_transcription() but using OpenAI instead of Ollama.
    Output format is exactly the same.
    """

    # --- STEP 1: SUMMARY ---
    print("Remote Step 1: Generating detailed summary...")

    summary_prompt = (
        "You are an expert call center analyst. Your task is to provide a detailed, contextual summary of the sales or service call transcript provided below, which involves a conversation between two persons. "
        "This transcript can be in any language, and you must always translate the analysis to English. "
        "Your output MUST contain exactly two sections: a Narrative Summary and a Key Facts Extracted list. "
        "DO NOT include any introductory text, closing remarks, or commentary outside of the requested structure.\n\n"
        
        "### 1. Narrative Summary\n"
        "**Objective:** [State the primary purpose of the call, identifying the seller/agent and the client/customer.]\n"
        "**Client Pain Points/Request:** [Detail the specific issues, challenges, or requests the customer is currently facing, including any mentioned numerical or operational details.]\n"
        "**Resolution/Proposal:** [Explain the specific action taken, the solution provided by the agent, or the offer/proposal made by the seller.] \n"
        "**Next Steps:** [Clearly state the agreed-upon next action, follow-up date, or final commitment.]\n\n"
        
        "### 2. Key Facts Extracted\n"
        "GENERATE a list of exactly this four bullet points using only quantifiable facts and specific names/dates found in the transcript. Each bullet point MUST start with the metric name in bold, followed by a colon and the extracted detail.\n"
        "* **Client Name and Role:** [Name and Role]\n"
        "* **Sales Caller Name and Role:** [Name and Role]\n"
        "* **Final Action Date/Time:** [The full date and time of the next scheduled meeting or follow-up]\n"
        "* **Associated Product/Service:** [The product, service, or issue at the center of the call]\n\n"
        
        "**TRANSCRIPT:**\n"
        f"---{transcription}---"
    )

    summary_report = _chat(summary_prompt)

    if not summary_report:
        return {
            "summary_report": "Error: Failed to generate summary report.",
            "tags_list": ["Error: Summary generation failed"]
        }

    # --- STEP 2: TAGS ---
    print("Remote Step 2: Generating tags...")

    tags_prompt = (
        "You are an expert call center analyst. Your task is to read the provided summary report and generate status tags for lead management. "
        "The tags must indicate the immediate status or outcome of the call. "
        "Your output MUST be a **single, valid JSON object** with exactly one top-level key: 'tags_list'. "
        "The value of 'tags_list' must be a JSON list of maximum 3 relevant minumum 1, precise tags. "
        "**CRITICAL EXAMPLES:** 'Client wants to buy', 'Wrong number', 'Needs follow-up', 'Voicemail', 'Qualified Lead', 'Pricing Inquiry', 'Demo Scheduled', 'Closed Lost'. "
        "**DO NOT** include any surrounding Markdown fences (```json) or commentary. **BEGIN** your response immediately with the opening curly brace '{'.\n\n"
        
        "**SUMMARY REPORT:**\n"
        f"---{summary_report}---"
    )

    raw = _chat(tags_prompt)

    try:
        match = re.search(r'(\{.*?\})', raw, re.DOTALL)
        if not match:
            tags_list = ["Error: Tag generation failed (no JSON found)"]
        else:
            tags_json = json.loads(match.group(1))
            tags_list = tags_json.get("tags_list", ["Error: Invalid tags_list"])
    except Exception:
        tags_list = ["Error: JSON parsing failure"]

    return {
        "summary_report": summary_report,
        "tags_list": tags_list
    }
