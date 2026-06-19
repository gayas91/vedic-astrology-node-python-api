import json
import re
from groq import Groq


#  Reduce payload for better performance (8B model friendly)
def compress_planets(planets):
    return [
        {
            "name": p.get("name"),
            "sign": p.get("sign"),
            "house": p.get("house"),
            "nakshatra": p.get("nakshatra")
        }
        for p in planets
    ]


#  Main function (Single API call)
def generate_all_explanations(groq_api_key, planets_chunk):
    client = Groq(api_key=groq_api_key)

    compact_data = compress_planets(planets_chunk)

    # Optimized prompt (stable + longer output)
    prompt = f"""
Return ONLY valid JSON.

You are a highly experienced Vedic astrologer.

Give Mahadasha explanation for each planet.

STYLE:
- Talk directly to user ("you")
- Use simple English
- Natural and human tone

CONTENT RULE:
- Each planet must have 60–80 words
- Keep explanation short but meaningful
- Write in 2 paragraphs
- Cover career, relationships, mindset, growth
- Add real-life meaning

STRICT RULES:
- Do NOT use line breaks inside JSON values
- Do NOT break JSON format
- No extra text outside JSON
- Do NOT use quotes inside text
- Do NOT use special characters
- Keep sentences simple
- Avoid long paragraphs

FORMAT:
{{
  "planets": [
    {{
      "planet": "Sun",
      "text": "Sun Mahadasha explanation..."
    }}
  ]
}}

DATA:
{json.dumps(compact_data)}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=1500  # important for longer output
        )
    except Exception as e:
        return [{
            "planet": "Error",
            "text": f"API Error: {str(e)}"
        }]

    #  Extract raw text safely
    text = ""
    if response.choices and response.choices[0].message:
        text = response.choices[0].message.content or ""

    text = text.strip()

    #  Remove markdown wrappers
    text = text.replace("```json", "").replace("```", "").strip()

    # Remove control characters (main fix)
    text = re.sub(r'[\x00-\x1F\x7F]', ' ', text)

    # Remove line breaks
    text = text.replace('\n', ' ').replace('\r', ' ')

    # Extract JSON block safely
    match = re.search(r'\{.*\}', text, re.DOTALL)

    if not match:
        return [{
            "planet": "Error",
            "text": text[:300]
        }]

    json_text = match.group(0)

    #  Final parsing
    try:
        parsed = json.loads(json_text)
        return parsed.get("planets", [])
    except Exception as e:
        return [{
            "planet": "Error",
            "text": f"JSON Error: {str(e)}"
        }]