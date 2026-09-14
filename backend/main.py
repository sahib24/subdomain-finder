
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

import subprocess
import json
import csv
from concurrent.futures import ThreadPoolExecutor

from active_dns import active_dns_discovery
from dns_validation import validate_dns
from http_validation import validate_http_https


app = FastAPI()


# --------------------------------
# CORS
# --------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------
# Home endpoint
# --------------------------------

@app.get("/")
def home():
    return {
        "message": "Subdomain Finder API is running"
    }


# --------------------------------
# Validate one subdomain
# --------------------------------

def validate_subdomain(subdomain):

    # DNS validation
    dns_valid = validate_dns(subdomain)

    # Default HTTP result
    http_result = {
        "http_valid": False,
        "url": None,
        "status_code": None
    }

    # DNS valid হলে HTTP/HTTPS check করবে
    if dns_valid:
        http_result = validate_http_https(subdomain)

    # Final live status
    live = (
        dns_valid
        and
        http_result["http_valid"]
    )

    return {
        "subdomain": subdomain,
        "dns_valid": dns_valid,
        "http_valid": http_result["http_valid"],
        "url": http_result["url"],
        "status_code": http_result["status_code"],
        "live": live
    }


# --------------------------------
# Scan endpoint
# --------------------------------

@app.get("/scan")
def scan(domains: str):

    domain_list = domains.split(",")

    all_results = []


    for domain in domain_list:

        domain = domain.strip()

        if not domain:
            continue


        # --------------------------------
        # Run Subfinder
        # --------------------------------

        result = subprocess.run(
            ["subfinder", "-d", domain],
            capture_output=True,
            text=True
        )


        # --------------------------------
        # Subfinder error
        # --------------------------------

        if result.returncode != 0:

            all_results.append({
                "domain": domain,
                "error": result.stderr
            })

            continue


        # --------------------------------
        # Passive subdomains
        # --------------------------------

        output = result.stdout

        passive_subdomains = output.strip().splitlines()

        passive_subdomains = list(
            set(passive_subdomains)
        )


        # --------------------------------
        # Active DNS discovery
        # --------------------------------

        active_subdomains = active_dns_discovery(domain)


        # --------------------------------
        # Merge passive + active
        # --------------------------------

        all_subdomains = list(
            set(
                passive_subdomains +
                active_subdomains
            )
        )


        # --------------------------------
        # PARALLEL VALIDATION
        # --------------------------------

        validated_results = []

        with ThreadPoolExecutor(max_workers=10) as executor:

            results = executor.map(
                validate_subdomain,
                all_subdomains
            )

            validated_results = list(results)


        # --------------------------------
        # Save domain result
        # --------------------------------

        all_results.append({
            "domain": domain,
            "count": len(validated_results),
            "subdomains": validated_results
        })


    # --------------------------------
    # Final result
    # --------------------------------

    final_result = {
        "total_domains": len(all_results),
        "results": all_results
    }


    # --------------------------------
    # JSON output
    # --------------------------------

    with open(
        "data/results.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            final_result,
            file,
            indent=2
        )


    # --------------------------------
    # CSV output
    # --------------------------------

    with open(
        "data/results.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)


        writer.writerow([
            "domain",
            "subdomain",
            "dns_valid",
            "http_valid",
            "url",
            "status_code",
            "live"
        ])


        for item in all_results:

            # Subfinder error
            if "error" in item:

                writer.writerow([
                    item["domain"],
                    "ERROR",
                    False,
                    False,
                    "",
                    "",
                    False
                ])

                continue


            # Normal results
            for result in item["subdomains"]:

                writer.writerow([
                    item["domain"],
                    result["subdomain"],
                    result["dns_valid"],
                    result["http_valid"],
                    result["url"] or "",
                    result["status_code"] or "",
                    result["live"]
                ])


    return final_result


# --------------------------------
# JSON Download
# --------------------------------

@app.get("/download/json")
def download_json():

    return FileResponse(
        "data/results.json",
        media_type="application/json",
        filename="results.json"
    )


# --------------------------------
# CSV Download
# --------------------------------

@app.get("/download/csv")
def download_csv():

    return FileResponse(
        "data/results.csv",
        media_type="text/csv",
        filename="results.csv"
    )
