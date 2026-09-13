
from fastapi import FastAPI  # Import FastAPI
import subprocess             # Run Subfinder
import json                   # Create JSON file
import csv                    # Create CSV file


app = FastAPI()               # Create FastAPI application


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "Subdomain Finder API is running"
    }


# Multiple domain scan endpoint
@app.get("/scan")
def scan(domains: str):

    # Split comma-separated domains into a list
    domain_list = domains.split(",")

    # Store results for all domains
    all_results = []

    # Scan each domain one by one
    for domain in domain_list:

        # Remove extra spaces
        domain = domain.strip()

        # Skip empty domain values
        if not domain:
            continue

        # Run Subfinder
        result = subprocess.run(
            ["subfinder", "-d", domain],
            capture_output=True,
            text=True
        )

        # Handle Subfinder error
        if result.returncode != 0:
            all_results.append({
                "domain": domain,
                "error": result.stderr
            })
            continue

        # Get Subfinder output
        output = result.stdout

        # Convert output into a subdomain list
        subdomains = output.strip().splitlines()

        # Remove duplicate subdomains
        subdomains = list(set(subdomains))

        # Save domain results
        all_results.append({
            "domain": domain,
            "count": len(subdomains),
            "subdomains": subdomains
        })

    # Create final result
    final_result = {
        "total_domains": len(all_results),
        "results": all_results
    }

    # -------------------------
    # Save JSON file
    # -------------------------

    with open("data/results.json", "w", encoding="utf-8") as file:
        json.dump(final_result, file, indent=2)

    # -------------------------
    # Save CSV file
    # -------------------------

    with open(
        "data/results.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        # Create CSV writer
        writer = csv.writer(file)

        # Write CSV header
        writer.writerow(["domain", "subdomain"])

        # Process each domain result
        for item in all_results:

            # Write error to CSV if scan failed
            if "error" in item:
                writer.writerow([
                    item["domain"],
                    "ERROR"
                ])
                continue

            # Write each subdomain to CSV
            for subdomain in item["subdomains"]:
                writer.writerow([
                    item["domain"],
                    subdomain
                ])

    # Return results as JSON response
    return final_result

