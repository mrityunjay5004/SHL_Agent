import json

def build_combined_text(item):
    return f"""
    Assessment Name: {item.get('name', '')}

    Description:
    {item.get('description', '')}

    Job Levels:
    {', '.join(item.get('job_levels', []))}

    Categories:
    {', '.join(item.get('keys', []))}

    Duration:
    {item.get('duration', '')}

    Adaptive:
    {item.get('adaptive', '')}

    Remote:
    {item.get('remote', '')}
    """

def preprocess_catalog(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    processed = []

    for item in data:
        item["combined_text"] = build_combined_text(item)
        processed.append(item)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(processed, f, indent=2)

    print("Processed catalog saved.")