"""
finAG — LLM Tool
Supports Anthropic (Claude), OpenAI (GPT), Google (Gemini), and Groq (Llama).
"""

from loguru import logger
from config import settings

client = None

if settings.llm_provider == "anthropic":
    from anthropic import Anthropic
    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

elif settings.llm_provider == "openai":
    from openai import OpenAI
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

elif settings.llm_provider == "gemini":
    import google.generativeai as genai
    genai.configure(api_key=settings.GEMINI_API_KEY)
    client = genai.GenerativeModel(settings.LLM_MODEL)

elif settings.llm_provider == "groq":
    from groq import Groq
    client = Groq(api_key=settings.GROQ_API_KEY)


def ask_llm(prompt: str, system_prompt: str = "", max_tokens: int = 2000) -> str:
    """
    Send a prompt to the configured LLM and get a text response.
    Works with Claude, GPT, Gemini, or Groq.
    """
    logger.debug(f"LLM request ({settings.llm_provider}): {prompt[:100]}...")

    if client is None:
        raise RuntimeError("No LLM configured. Set an API key in .env")

    try:
        if settings.llm_provider == "anthropic":
            message = client.messages.create(
                model=settings.LLM_MODEL,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )
            response_text = message.content[0].text

        elif settings.llm_provider == "openai":
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=settings.LLM_MODEL,
                max_tokens=max_tokens,
                messages=messages,
            )
            response_text = response.choices[0].message.content

        elif settings.llm_provider == "gemini":
            full_prompt = ""
            if system_prompt:
                full_prompt = f"Instructions: {system_prompt}\n\n"
            full_prompt += prompt

            response = client.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                ),
            )
            response_text = response.text

        elif settings.llm_provider == "groq":
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=settings.LLM_MODEL,
                max_tokens=max_tokens,
                messages=messages,
            )
            response_text = response.choices[0].message.content

        logger.debug(f"LLM response: {response_text[:100]}...")
        return response_text

    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise RuntimeError(f"Failed to get LLM response: {str(e)}") from e


def ask_llm_json(prompt: str, system_prompt: str = "", max_tokens: int = 2000) -> str:
    json_system = system_prompt + "\n\nIMPORTANT: Respond ONLY with valid JSON. No markdown, no explanation, no backticks."
    return ask_llm(prompt, system_prompt=json_system, max_tokens=max_tokens)