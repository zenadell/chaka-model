from groq import Groq

client = Groq(api_key="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")
models = client.models.list()
for model in models.data:
    print(f"ID: {model.id} | Created: {model.created}")
