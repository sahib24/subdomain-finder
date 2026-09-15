
# import requests
# import re
# import urllib3
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin, urlparse

# # verify=False এর warning বন্ধ করে
# urllib3.disable_warnings(
#     urllib3.exceptions.InsecureRequestWarning
# )

# USER_AGENT = "SubdomainFinder/1.0"

# # প্রতিটি request সর্বোচ্চ 3 সেকেন্ড অপেক্ষা করবে
# REQUEST_TIMEOUT = 3

# # 512 KB এর বেশি JavaScript file process করবে না
# MAX_JS_SIZE = 512 * 1024


# def js_analysis_discovery(subdomains, domain):

#     discovered = set()

#     # একই JS URL একাধিকবার download করা বন্ধ করবে
#     checked_js_urls = set()

#     # একই connection reuse করার জন্য Session
#     session = requests.Session()

#     session.headers.update({
#         "User-Agent": USER_AGENT
#     })

#     for subdomain in subdomains:

#         # প্রথমে HTTPS, তারপর HTTP
#         urls = [
#             f"https://{subdomain}",
#             f"http://{subdomain}"
#         ]

#         https_success = False

#         for url in urls:

#             # HTTPS কাজ করলে HTTP আর check করবে না
#             if url.startswith("http://") and https_success:
#                 continue

#             try:
#                 # Web page download
#                 response = session.get(
#                     url,
#                     timeout=REQUEST_TIMEOUT,
#                     verify=False
#                 )

#                 # HTTPS সফল হলে flag সেট করবে
#                 if (
#                     url.startswith("https://")
#                     and response.status_code < 400
#                 ):
#                     https_success = True

#                 # Error response skip
#                 if response.status_code >= 400:
#                     continue

#                 # HTML page বেশি বড় হলে skip
#                 if len(response.content) > MAX_JS_SIZE:
#                     continue

#                 # HTML parse
#                 soup = BeautifulSoup(
#                     response.text,
#                     "html.parser"
#                 )

#                 # HTML থেকে JS files খুঁজবে
#                 for script in soup.find_all(
#                     "script",
#                     src=True
#                 ):

#                     js_src = script.get("src")

#                     if not js_src:
#                         continue

#                     # Relative JS URL → absolute URL
#                     js_url = urljoin(
#                         url,
#                         js_src
#                     )

#                     # Duplicate JS skip
#                     if js_url in checked_js_urls:
#                         continue

#                     checked_js_urls.add(js_url)

#                     try:
#                         # ------------------------------------------------
#                         # Optimization:
#                         # আগে HEAD request না করে সরাসরি GET করছি
#                         # ফলে প্রতিটি JS file-এর জন্য ১টি request কমে গেল
#                         # ------------------------------------------------
#                         js_response = session.get(
#                             js_url,
#                             timeout=REQUEST_TIMEOUT,
#                             verify=False,
#                             stream=True
#                         )

#                         # HTTP error হলে skip
#                         if js_response.status_code >= 400:
#                             js_response.close()
#                             continue

#                         # Content-Length থাকলে আগে size check
#                         content_length = js_response.headers.get(
#                             "Content-Length"
#                         )

#                         if content_length:

#                             try:
#                                 if int(content_length) > MAX_JS_SIZE:
#                                     js_response.close()
#                                     continue

#                             except ValueError:
#                                 pass

#                         # JavaScript content download
#                         js_content = js_response.content

#                         # Connection close
#                         js_response.close()

#                         # Final size protection
#                         if len(js_content) > MAX_JS_SIZE:
#                             continue

#                         # Bytes → text
#                         js_text = js_content.decode(
#                             "utf-8",
#                             errors="ignore"
#                         )

#                         # JavaScript-এর ভিতরের URLs খুঁজবে
#                         urls_found = re.findall(
#                             r'https?://[^\s\'"<>]+',
#                             js_text
#                         )

#                         for found_url in urls_found:

#                             parsed = urlparse(
#                                 found_url
#                             )

#                             hostname = parsed.hostname

#                             if not hostname:
#                                 continue

#                             hostname = hostname.lower()

#                             # শেষের dot remove
#                             hostname = hostname.rstrip(".")

#                             # শুধু target domain-এর hostname রাখবে
#                             if (
#                                 hostname == domain
#                                 or hostname.endswith(
#                                     "." + domain
#                                 )
#                             ):
#                                 discovered.add(
#                                     hostname
#                                 )

#                     except requests.RequestException:
#                         continue

#                     except Exception:
#                         continue

#             except requests.RequestException:
#                 continue

#             except Exception:
#                 continue

#     # Session বন্ধ করবে
#     session.close()

#     # Sorted result return
#     return sorted(discovered)

