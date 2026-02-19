import json, csv

def save_json(data, filename="osint_report.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def save_csv(data, filename="osint_report.csv"):
    keys = ["url", "status", "title", "server", "emails"]
    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for row in data:
            row_copy = row.copy()
            row_copy["emails"] = ";".join(row_copy.get("emails") or [])
            writer.writerow(row_copy)
