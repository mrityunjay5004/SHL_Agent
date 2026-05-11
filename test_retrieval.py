from app.retriever import retrieve

query = (
    "Hiring a Java backend developer "
    "with communication skills"
)

results = retrieve(query)

print("\nTop Recommendations:\n")

for idx, item in enumerate(results[:5], start=1):

    print(f"{idx}. {item['name']}")