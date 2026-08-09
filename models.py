"""
Thin wrapper around the Qwen3-VL and Qwen3-Omni models used by
KopiCheck.

Both models are open source and can be called either through Alibaba
Cloud's DashScope API, or self hosted through any OpenAI compatible
inference server (for example vLLM). This wrapper targets the
DashScope API for the prototype, since it requires no GPU on the
developer's machine, but the interface is written so that swapping in
a self hosted endpoint later only means changing the base_url and key.
"""

import base64
import json
import os

from openai import OpenAI

DASHSCOPE_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

VL_MODEL = "qwen3-vl-plus"
OMNI_MODEL = "qwen3-omni-flash"


def _client() -> OpenAI:
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "DASHSCOPE_API_KEY is not set. Copy .env.example to .env "
            "and add your key before running the pipeline."
        )
    return OpenAI(api_key=api_key, base_url=DASHSCOPE_BASE_URL)


def _encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def classify_frame(image_path: str, prompt: str) -> dict:
    """
    Send a single sampled frame to Qwen3-VL for classification against
    the NEA checklist categories. Returns the parsed JSON response, or
    a "none" result if the model output could not be parsed.
    """
    client = _client()
    b64_image = _encode_image(image_path)

    response = client.chat.completions.create(
        model=VL_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"},
                    },
                ],
            }
        ],
        response_format={"type": "json_object"},
    )

    return _safe_parse(response.choices[0].message.content)


def fuse_audio_and_frame(audio_transcript: str, visual_description: str, prompt_template: str) -> dict:
    """
    Send a resolved audio transcript alongside a visual description to
    Qwen3-Omni, for cases where the frame classifier's confidence was
    too low to log automatically. Returns the parsed JSON response.
    """
    client = _client()
    prompt = prompt_template.format(
        visual_description=visual_description,
        audio_transcript=audio_transcript,
    )

    response = client.chat.completions.create(
        model=OMNI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )

    return _safe_parse(response.choices[0].message.content)


def _safe_parse(raw: str) -> dict:
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {
            "category": "none",
            "description": "Could not parse model output.",
            "confidence": 0.0,
            "reading": None,
            "flagged": False,
        }
