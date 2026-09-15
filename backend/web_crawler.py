import requests
import urllib3

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

REQUEST_TIMEOUT = 3
MAX_HTML_SIZE = 2 * 1024 * 1024  # 2 MB

USER_AGENT = "SubdomainFinder/1.0"

# একসাথে সর্বোচ্চ 10টি subdomain crawl করবে
MAX_WORKERS = 10


def crawl_single_subdomain(subdomain, domain):
    """
    একটি subdomain-এর HTTPS/HTTP page crawl করে
    target domain-এর নতুন subdomain খুঁজে বের করে।
    """

    discovered = set()

    session = requests.Session()

    session.headers.update({
        "User-Agent": USER_AGENT
    })

    urls = [
        f"https://{subdomain}",
        f"http://{subdomain}"
    ]

    for url in urls:

        try:
            response = session.get(
                url,
                timeout=REQUEST_TIMEOUT,
                verify=False
            )

            # Failed response হলে পরের URL try করব
            if response.status_code >= 400:
                continue

            # Content-Length দেখে বড় page আগে থেকেই বাদ দিচ্ছি
            content_length = response.headers.get(
                "Content-Length"
            )

            if content_length:
                try:
                    if int(content_length) > MAX_HTML_SIZE:
                        continue
                except ValueError:
                    pass

            # Extra safety check
            if len(response.content) > MAX_HTML_SIZE:
                continue

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            # Page-এর সব link বের করা
            for link in soup.find_all("a", href=True):

                href = link.get("href")

                absolute_url = urljoin(
                    url,
                    href
                )

                parsed = urlparse(
                    absolute_url
                )

                hostname = parsed.hostname

                if not hostname:
                    continue

                hostname = hostname.lower()

                # শুধু target domain-এর subdomain রাখব
                if (
                    hostname == domain
                    or hostname.endswith("." + domain)
                ):
                    discovered.add(hostname)

            # HTTPS/HTTP যেটা প্রথম successful,
            # সেটার page crawl করেই পরের subdomain-এ যাব।
            break

        except requests.RequestException:
            continue

        except Exception:
            continue

    session.close()

    return discovered


def web_crawler_discovery(subdomains, domain):
    """
    সব subdomain parallelভাবে crawl করে
    নতুন subdomain discover করে।
    """

    discovered = set()

    # সর্বোচ্চ 10টি subdomain একসাথে process হবে
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

        futures = [
            executor.submit(
                crawl_single_subdomain,
                subdomain,
                domain
            )
            for subdomain in subdomains
        ]

        # প্রতিটি worker-এর result সংগ্রহ
        for future in futures:

            try:
                results = future.result()

                for hostname in results:
                    discovered.add(hostname)

            except Exception:
                continue

    return sorted(discovered)