def generate_astro_explanation(groq_api_key, planets_detailed, focus_planet_name=None):
    import json
    from groq import Groq

    client = Groq(api_key=groq_api_key)

    try:
        #  If no planet passed → default first planet
        if not focus_planet_name:
            focus_planet_name = planets_detailed[0]["name"]

        #  Find that planet from table
        focus_planet = next(
            (p for p in planets_detailed if p["name"].lower() == focus_planet_name.lower()),
            None
        )

        # fallback safety
        if not focus_planet:
            focus_planet = planets_detailed[0]

        dasha_name = f"{focus_planet['name']} Mahadasha"

        prompt = f"""
You are a highly experienced Vedic astrologer using Brighu-Naadi system.

Your goal is to give a deeply personal and accurate reading.

STYLE:
- Talk like a real astrologer
- Speak directly using "you"
- Keep tone simple and natural

LANGUAGE RULE:
- Use very simple English
- Keep sentences short

OUTPUT FORMAT:
{{
  "text": "One continuous explanation in 2–4 paragraphs"
}}

IMPORTANT:
- Focus mainly on this planet: {focus_planet['name']}
- Use its house, sign and nakshatra strongly

DASHA:
{dasha_name}

FOCUS PLANET DATA:
{json.dumps(focus_planet)}

FULL CHART DATA:
{json.dumps(planets_detailed)}
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        text = response.choices[0].message.content
        text = text.replace("```json", "").replace("```", "").strip()

        try:
            return json.loads(text)
        except:
            return {"text": text}

    except Exception as e:
        return {
            "text": "Unable to generate explanation.",
            "error": str(e)
        }