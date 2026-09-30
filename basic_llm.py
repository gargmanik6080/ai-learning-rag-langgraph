import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OMNIROUTE_API_KEY")

client = OpenAI(
    api_key=api_key or "local-dev",
    base_url="http://127.0.0.1:20128/v1",
)

response = client.chat.completions.create(
    model="gc/grok-4.6",
    # messages=[
    #     {"role": "system", "content": "You are a helpful assistant."},
    #     {"role": "user", "content": "Explain the diff between readiness and startup probes in Kubernetes."},
    # ],
    messages=[
        {"role": "user", "content": "Explain the diff between readiness and startup probes in Kubernetes."},
    ],

    temperature=0.2,
)

print(response.choices[0].message.content)
