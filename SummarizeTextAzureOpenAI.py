from openai import AzureOpenAI

def summarize_text_azure_openai(text, deployment_name, endpoint, open_ai_api_key, api_version):
    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_version=api_version,
        api_key=open_ai_api_key,
    )

    prompt = f"Summarize the following text, limit the respone to 150 words:\n\n{text}"

    response = client.chat.completions.create(
        model=deployment_name,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0.5,
    )

    summary = response.choices[0].message.content.strip()
    return summary
