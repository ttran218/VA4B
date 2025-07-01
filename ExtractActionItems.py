from openai import AzureOpenAI

def extract_action_items(content, deployment_name, endpoint, open_ai_api_key, api_version):

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_version=api_version,
        api_key=open_ai_api_key,
    )
    
    prompt = (
        "Extract all action items from the following text. "
        "Return them as a numbered list:\n\n"
        f"{content}\n\nAction Items:"
    )

    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {"role": "system", "content": "You are an assistant that extracts action items from meeting notes."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=512
    )

    action_items_text = response.choices[0].message.content
    # Split into list by lines, remove empty lines and numbering
    action_items = [
        line.lstrip("0123456789. ").strip()
        for line in action_items_text.strip().split('\n')
        if line.strip()
    ]
    return action_items