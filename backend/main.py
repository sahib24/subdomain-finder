
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

import subprocess
import json
import csv
import time

from concurrent.futures import ThreadPoolExecutor

from backend.crtsh import crtsh_discovery
from backend.san_cn import san_cn_discovery
from backend.active_dns import active_dns_discovery
from backend.passive_dns import passive_dns_discovery
from backend.dns_wordlist import dns_wordlist_discovery
from backend.smart_wordlist import smart_wordlist_discovery
from backend.web_crawler import web_crawler_discovery
from backend.historical_dns import historical_dns_discovery
from backend.dns_records import get_dns_records
from backend.reverse_dns import reverse_dns_discovery
from backend.axfr_check import check_axfr
from backend.dns_validation import validate_dns
from backend.http_validation import validate_http_https


app = FastAPI()


# CORS
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


# Home
@app.get("/")
def home():

    return {
        "message": "Subdomain Finder API is running"
    }


# Subdomain Validation
def validate_subdomain(subdomain):

    validation_start = time.time()

    # DNS validation
    dns_start = time.time()

    dns_valid = validate_dns(
        subdomain
    )

    dns_time = time.time() - dns_start

    # DNS records
    records_start = time.time()

    dns_records = get_dns_records(
        subdomain
    )

    records_time = time.time() - records_start

    # Collect IP addresses
    ip_addresses = []

    ip_addresses.extend(
        dns_records.get(
            "A",
            []
        )
    )

    ip_addresses.extend(
        dns_records.get(
            "AAAA",
            []
        )
    )

    # Reverse DNS / PTR
    reverse_start = time.time()

    reverse_dns = reverse_dns_discovery(
        ip_addresses
    )

    reverse_time = time.time() - reverse_start

    # Default HTTP result
    http_result = {
        "http_valid": False,
        "url": None,
        "status_code": None
    }

    # HTTP/HTTPS validation
    http_time = 0

    if dns_valid:

        http_start = time.time()

        http_result = validate_http_https(
            subdomain
        )

        http_time = time.time() - http_start

    # Final live status
    live = (
        dns_valid
        and
        http_result["http_valid"]
    )

    total_validation_time = (
        time.time() - validation_start
    )

    print(
        f"[VALIDATION] {subdomain} | "
        f"DNS: {dns_time:.2f}s | "
        f"Records: {records_time:.2f}s | "
        f"Reverse: {reverse_time:.2f}s | "
        f"HTTP: {http_time:.2f}s | "
        f"Total: {total_validation_time:.2f}s"
    )

    return {

        "subdomain": subdomain,

        "dns_valid": dns_valid,

        "dns_records": dns_records,

        "reverse_dns": reverse_dns,

        "http_valid": http_result[
            "http_valid"
        ],

        "url": http_result[
            "url"
        ],

        "status_code": http_result[
            "status_code"
        ],

        "live": live
    }


# Scan
@app.get("/scan")
def scan(domains: str):

    scan_start = time.time()

    # Multiple domains support
    domain_list = domains.split(",")

    all_results = []

    # Process each domain
    for domain in domain_list:

        domain = domain.strip()

        if not domain:
            continue

        print()
        print("=" * 60)
        print(f"SCAN STARTED: {domain}")
        print("=" * 60)

        # Step 13 # Subfinder
        start = time.time()

        result = subprocess.run(
            [
                "subfinder",
                "-d",
                domain
            ],
            capture_output=True,
            text=True
        )

        subfinder_time = time.time() - start

        print(
            f"[TIME] Subfinder: "
            f"{subfinder_time:.2f}s"
        )

        # Subfinder error
        if result.returncode != 0:

            all_results.append({

                "domain": domain,

                "error": result.stderr

            })

            continue

        # Subfinder output
        output = result.stdout

        passive_subdomains = (
            output
            .strip()
            .splitlines()
        )

        # Remove duplicates
        passive_subdomains = list(
            set(
                passive_subdomains
            )
        )

        print(
            f"[INFO] Subfinder found: "
            f"{len(passive_subdomains)}"
        )

        # Step 28 # Active DNS Discovery
        start = time.time()

        active_subdomains = (
            active_dns_discovery(
                domain
            )
        )

        active_time = time.time() - start

        print(
            f"[TIME] Active DNS: "
            f"{active_time:.2f}s | "
            f"Found: {len(active_subdomains)}"
        )

        # Step 34 # crt.sh
        start = time.time()

        crt_subdomains = (
            crtsh_discovery(
                domain
            )
        )

        crt_time = time.time() - start

        print(
            f"[TIME] crt.sh: "
            f"{crt_time:.2f}s | "
            f"Found: {len(crt_subdomains)}"
        )

        # Step 35 # SAN / CN
        start = time.time()

        san_cn_subdomains = (
            san_cn_discovery(
                domain
            )
        )

        san_cn_time = time.time() - start

        print(
            f"[TIME] SAN/CN: "
            f"{san_cn_time:.2f}s | "
            f"Found: {len(san_cn_subdomains)}"
        )

        # Step 36 # Passive DNS
        start = time.time()

        passive_dns_subdomains = (
            passive_dns_discovery(
                domain
            )
        )

        passive_dns_time = time.time() - start

        print(
            f"[TIME] Passive DNS: "
            f"{passive_dns_time:.2f}s | "
            f"Found: {len(passive_dns_subdomains)}"
        )

        # Step 37 # DNS Wordlist
        start = time.time()

        wordlist_subdomains = (
            dns_wordlist_discovery(
                domain
            )
        )

        wordlist_time = time.time() - start

        print(
            f"[TIME] DNS Wordlist: "
            f"{wordlist_time:.2f}s | "
            f"Found: {len(wordlist_subdomains)}"
        )

        # Merge initial discoveries
        all_subdomains = list(
            set(
                passive_subdomains
                +
                active_subdomains
                +
                crt_subdomains
                +
                san_cn_subdomains
                +
                passive_dns_subdomains
                +
                wordlist_subdomains
            )
        )

        print(
            f"[INFO] After initial discovery: "
            f"{len(all_subdomains)} subdomains"
        )

        # Step 38 # Smart Wordlist
        start = time.time()

        smart_subdomains = (
            smart_wordlist_discovery(
                all_subdomains,
                domain
            )
        )

        smart_time = time.time() - start

        all_subdomains = list(
            set(
                all_subdomains
                +
                smart_subdomains
            )
        )

        print(
            f"[TIME] Smart Wordlist: "
            f"{smart_time:.2f}s | "
            f"Found: {len(smart_subdomains)} | "
            f"Total: {len(all_subdomains)}"
        )

        # Step 39 # Web Crawler
        start = time.time()

        crawler_subdomains = (
            web_crawler_discovery(
                all_subdomains,
                domain
            )
        )

        crawler_time = time.time() - start

        all_subdomains = list(
            set(
                all_subdomains
                +
                crawler_subdomains
            )
        )

        print(
            f"[TIME] Web Crawler: "
            f"{crawler_time:.2f}s | "
            f"Found: {len(crawler_subdomains)} | "
            f"Total: {len(all_subdomains)}"
        )

       
        # Step 41 # Historical DNS
        start = time.time()

        historical_subdomains = (
            historical_dns_discovery(
                domain
            )
        )

        historical_time = time.time() - start

        all_subdomains = list(
            set(
                all_subdomains
                +
                historical_subdomains
            )
        )

        print(
            f"[TIME] Historical DNS: "
            f"{historical_time:.2f}s | "
            f"Found: {len(historical_subdomains)} | "
            f"Total: {len(all_subdomains)}"
        )

        # Step 44 # DNS Zone Transfer / AXFR
        start = time.time()

        axfr_results = (
            check_axfr(
                domain
            )
        )

        axfr_time = time.time() - start

        print(
            f"[TIME] AXFR: "
            f"{axfr_time:.2f}s"
        )

        print(
            f"[INFO] Final subdomains to validate: "
            f"{len(all_subdomains)}"
        )

        # Validate discovered subdomains
        validation_start = time.time()

        validated_results = []

        with ThreadPoolExecutor(
            max_workers=10
        ) as executor:

            results = executor.map(
                validate_subdomain,
                all_subdomains
            )

            validated_results = list(
                results
            )

        validation_time = (
            time.time() - validation_start
        )

        print(
            f"[TIME] All Validation: "
            f"{validation_time:.2f}s"
        )

        # Domain result
        all_results.append({

            "domain": domain,

            "count": len(
                validated_results
            ),

            "subdomains": validated_results,

            "axfr": axfr_results

        })

        print(
            f"[TIME] Domain total: "
            f"{time.time() - scan_start:.2f}s"
        )

    # Final JSON result
    final_result = {

        "total_domains": len(
            all_results
        ),

        "results": all_results

    }

    # Save JSON
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

    # Save CSV
    with open(
        "data/results.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(
            file
        )

        writer.writerow([
            "domain",
            "subdomain",
            "dns_valid",
            "A",
            "AAAA",
            "CNAME",
            "MX",
            "NS",
            "TXT",
            "reverse_dns",
            "http_valid",
            "url",
            "status_code",
            "live"
        ])

        # Write results
        for item in all_results:

            # Error result
            if "error" in item:

                writer.writerow([
                    item["domain"],
                    "ERROR",
                    False,
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    False,
                    "",
                    "",
                    False
                ])

                continue

            # Normal subdomain results
            for result in item[
                "subdomains"
            ]:

                dns_records = result.get(
                    "dns_records",
                    {}
                )

                reverse_dns_results = (
                    result.get(
                        "reverse_dns",
                        []
                    )
                )

                writer.writerow([

                    item["domain"],

                    result["subdomain"],

                    result["dns_valid"],

                    "; ".join(
                        dns_records.get(
                            "A",
                            []
                        )
                    ),

                    "; ".join(
                        dns_records.get(
                            "AAAA",
                            []
                        )
                    ),

                    "; ".join(
                        dns_records.get(
                            "CNAME",
                            []
                        )
                    ),

                    "; ".join(
                        dns_records.get(
                            "MX",
                            []
                        )
                    ),

                    "; ".join(
                        dns_records.get(
                            "NS",
                            []
                        )
                    ),

                    "; ".join(
                        dns_records.get(
                            "TXT",
                            []
                        )
                    ),

                    "; ".join(
                        reverse_dns_results
                    ),

                    result[
                        "http_valid"
                    ],

                    result[
                        "url"
                    ] or "",

                    result[
                        "status_code"
                    ] or "",

                    result[
                        "live"
                    ]

                ])

    total_scan_time = (
        time.time() - scan_start
    )

    print()
    print("=" * 60)
    print(
        f"TOTAL SCAN TIME: "
        f"{total_scan_time:.2f}s"
    )
    print("=" * 60)
    print()

    # Return API result
    return final_result


# Download JSON
@app.get("/download/json")
def download_json():

    return FileResponse(

        "data/results.json",

        media_type="application/json",

        filename="results.json"

    )


# Download CSV
@app.get("/download/csv")
def download_csv():

    return FileResponse(

        "data/results.csv",

        media_type="text/csv",

        filename="results.csv"

    )

