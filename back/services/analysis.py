from fastapi import HTTPException
from utils.ollama import ollama_call
import json
import re

def analyze_transcription(transcription: str):
    """
    Performs two sequential calls to Ollama: 
    1. To generate the detailed summary report.
    2. To generate the tags list based on the summary report.
    """
    
    # --- STEP 1: GENERATE THE DETAILED SUMMARY REPORT (String output) ---
    print("Step 1: Generating detailed summary report...")
    
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
    
    summary_report = ollama_call(summary_prompt)
    if not summary_report or "Error" in summary_report:
        if "Service Unavailable" in summary_report:
            raise HTTPException(status_code=503, detail=summary_report)
        return {
            "summary_report": "Error: Failed to generate summary report.",
            "tags_list": ["Error: Summary generation failed"]
        }

    # --- STEP 2: GENERATE THE TAGS LIST (JSON output based on the summary) ---
    print("Step 2: Generating tags list based on summary...")
    
    tags_prompt = (
        "You are an expert call center analyst. Your task is to read the provided summary report and generate status tags for lead management. "
        "The tags must indicate the immediate status or outcome of the call. "
        "Your output MUST be a **single, valid JSON object** with exactly one top-level key: 'tags_list'. "
        "The value of 'tags_list' must be a JSON list of one or more relevant, precise tags. "
        "**CRITICAL EXAMPLES:** 'Client wants to buy', 'Wrong number', 'Needs follow-up', 'Voicemail', 'Qualified Lead', 'Pricing Inquiry', 'Demo Scheduled', 'Closed Lost'. "
        "**DO NOT** include any surrounding Markdown fences (```json) or commentary. **BEGIN** your response immediately with the opening curly brace '{'.\n\n"
        
        "**SUMMARY REPORT:**\n"
        f"---{summary_report}---"
    )
    
    raw_json_string = ollama_call(tags_prompt)
    
    try:
        match = re.search(r'(\{.*?\})', raw_json_string, re.DOTALL)
        if not match:
            print(f"[ERROR] LLM did not return any JSON object for tags.")
            tags_list = ["Error: Tag generation failed (no JSON object found)"]
        else:
            json_to_parse = match.group(1)
            parsed_data = json.loads(json_to_parse)
            tags_list = parsed_data.get("tags_list", ["Error: Tags list missing or invalid."])

    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse JSON for tags: {e}")
        print(f"Raw tag response: {raw_json_string[:500]}...")
        tags_list = [f"Error: JSON Decode Error for tags: {e}"]
        
    return {
        "summary_report": summary_report,
        "tags_list": tags_list
    }