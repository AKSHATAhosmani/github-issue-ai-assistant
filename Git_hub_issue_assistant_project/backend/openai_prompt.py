from textwrap import dedent

EXAMPLE_INPUT = dedent("""
Title: "Login button not responding on mobile"
Body: "When I tap the login button on iOS, nothing happens. It works on desktop."
Comments: "Likely a mobile touch handler issue"
""")

EXAMPLE_OUTPUT = {
    "summary": "Login button on mobile devices is unresponsive.",
    "type": "bug",
    "priority_score": "4 - High impact on mobile login flow.",
    "suggested_labels": ["bug", "mobile", "login-flow"],
    "potential_impact": "Mobile users may be blocked from logging in."
}


def build_prompt(issue_text: str) -> str:
    """
    Build the prompt for the HuggingFace model.
    We show schema + example and force model to output ONLY JSON.
    """
    return dedent(f"""
    You are an assistant that analyzes GitHub issues and returns ONLY a JSON object.

    JSON schema:
    {{
      "summary": "A one-sentence summary of the user's problem or request.",
      "type": "bug | feature_request | documentation | question | other",
      "priority_score": "A score 1–5 plus a short justification.",
      "suggested_labels": ["2–3 short GitHub labels"],
      "potential_impact": "One sentence on user impact (if this is a bug)."
    }}

    Example input:
    {EXAMPLE_INPUT}

    Example output:
    {EXAMPLE_OUTPUT}

    IMPORTANT:
    - Return ONLY valid JSON.
    - Do NOT include any explanation outside JSON.
    - Keep sentences short and clear.

    Now analyze this issue:

    {issue_text}
    """)
