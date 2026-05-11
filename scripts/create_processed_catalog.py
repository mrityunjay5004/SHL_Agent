import json


def build_combined_text(item):

    return f"""
    Assessment Name:
    {item.get('name', '')}

    Description:
    {item.get('description', '')}

    Job Levels:
    {', '.join(item.get('job_levels', []))}

    Categories:
    {', '.join(item.get('keys', []))}

    Duration:
    {item.get('duration', '')}

    Remote:
    {item.get('remote', '')}

    Adaptive:
    {item.get('adaptive', '')}
    """


# READ RAW FILE SAFELY
with open(
    "data/shl_catalog.json",
    "r",
    encoding="utf-8",
    errors="ignore"
) as f:

    raw_text = f.read()


# REMOVE BAD CONTROL CHARACTERS
clean_text = "".join(
    ch for ch in raw_text
    if ord(ch) >= 32 or ch in "\n\r\t"
)


catalog = json.loads(clean_text)

processed = []

for item in catalog:

    item["combined_text"] = (
        build_combined_text(item)
    )

    processed.append(item)


with open(
    "data/processed_catalog.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        processed,
        f,
        indent=2,
        ensure_ascii=False
    )

print("Processed catalog created successfully.")