import os

import anthropic
from dotenv import load_dotenv

load_dotenv()

if not os.environ.get("ANTHROPIC_API_KEY"):
    raise SystemExit("No ANTHROPIC_API_KEY found. Check that your .env file contains a line starting with ANTHROPIC_API_KEY=")

client = anthropic.Anthropic()

response = client.beta.messages.create(
    model="claude-opus-5-5",
    max_tokens=1024,
    betas=["server-side-fallback-2026-07-01"],
    fallbacks="default",
    messages=[{"role": "user", "content": "Say hello in one short sentence."}],
)

for block in response.content:
    if block.type == "text":
        print(block.text)
