import re
import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import Dict, List, Any
import warnings
warnings.filterwarnings("ignore")

MAX_JS_BUNDLES_TO_FETCH = 12  # Fetch more bundles to catch packages in lazy-loaded chunks
JS_BUNDLE_MAX_BYTES = 800_000  # 800KB per bundle

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}


class TechnologyScanner:
    def __init__(self, timeout: int = 8):
        self.timeout = timeout

    async def fetch_page_data(self, domain: str) -> Dict[str, Any]:
        """
        Fetches a domain and extracts:
        - html: full raw HTML
        - headers: HTTP response headers
        - cookies: cookies from response
        - scripts: list of external script src URLs
        - inline_scripts: content of inline <script> tags (key fingerprint source)
        - meta: meta tag name->content
        - js_bundle_content: concatenated content from fetched JS bundles
        """
        base_result = {
            "html": "", "headers": {}, "cookies": {},
            "scripts": [], "inline_scripts": [], "meta": {},
            "js_bundle_content": "",
            "success": False, "error": None
        }

        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            verify=False,
            headers=BROWSER_HEADERS
        ) as client:
            # Try HTTPS first, fall back to HTTP
            for scheme in ["https", "http"]:
                url = f"{scheme}://{domain}"
                try:
                    response = await client.get(url)
                    html_content = response.text
                    resp_headers = dict(response.headers)
                    resp_cookies = dict(response.cookies)

                    soup = BeautifulSoup(html_content, "html.parser")

                    # External script URLs
                    script_srcs = []
                    for tag in soup.find_all("script"):
                        src = tag.get("src")
                        if src:
                            script_srcs.append(src)

                    # Also collect JS preload links (Next.js, Vite, etc.)
                    for tag in soup.find_all("link", rel=lambda v: v and "preload" in v):
                        href = tag.get("href", "")
                        if href.endswith(".js") or ".js?" in href:
                            if href not in script_srcs:
                                script_srcs.append(href)

                    # Inline script content — critical for modern frameworks
                    inline_scripts = []
                    for tag in soup.find_all("script"):
                        if not tag.get("src") and tag.string:
                            inline_scripts.append(tag.string)

                    # Meta tags
                    meta_tags = {}
                    for meta in soup.find_all("meta"):
                        name = meta.get("name") or meta.get("property")
                        content = meta.get("content")
                        if name and content:
                            meta_tags[name] = content

                    # Resolve relative script URLs and pick bundles to fetch
                    base_url = f"{scheme}://{domain}"
                    bundle_urls = self._pick_js_bundles(script_srcs, base_url)

                    # Fetch JS bundle contents concurrently
                    js_bundle_content = await self._fetch_js_bundles(client, bundle_urls)

                    return {
                        "html": html_content,
                        "headers": resp_headers,
                        "cookies": resp_cookies,
                        "scripts": script_srcs,
                        "inline_scripts": inline_scripts,
                        "meta": meta_tags,
                        "js_bundle_content": js_bundle_content,
                        "success": True,
                        "error": None,
                    }
                except Exception as e:
                    base_result["error"] = str(e)
                    continue  # try next scheme

        return base_result

    def _pick_js_bundles(self, script_srcs: List[str], base_url: str) -> List[str]:
        """
        Selects up to MAX_JS_BUNDLES_TO_FETCH script URLs to fetch and analyze.
        Prefer main/chunk bundles over vendor/polyfill files.
        """
        full_urls = []
        for src in script_srcs:
            if src.startswith("//"):
                src = "https:" + src
            elif src.startswith("/"):
                src = base_url + src
            elif not src.startswith("http"):
                src = base_url + "/" + src

            # Skip obviously external analytics/ads scripts
            skip_patterns = ["google-analytics", "googletagmanager", "facebook.net",
                             "hotjar", "clarity", "stripe", "intercom", "hubspot",
                             "twitter", "linkedin", "pinterest"]
            if any(p in src.lower() for p in skip_patterns):
                continue

            full_urls.append(src)

        # Prefer framework-specific paths
        priority = []
        rest = []
        for url in full_urls:
            if any(p in url for p in ["/_next/", "/_nuxt/", "/static/js/", "/assets/", "/build/"]):
                priority.append(url)
            else:
                rest.append(url)

        candidates = priority + rest
        return candidates[:MAX_JS_BUNDLES_TO_FETCH]

    async def _fetch_js_bundles(self, client: httpx.AsyncClient, urls: List[str]) -> str:
        """Fetch JS bundle contents concurrently, return concatenated text."""
        async def _fetch_one(url: str) -> str:
            try:
                r = await client.get(url, timeout=5)
                if r.status_code == 200:
                    # Limit size to avoid memory issues
                    return r.text[:JS_BUNDLE_MAX_BYTES]
            except Exception:
                pass
            return ""

        tasks = [_fetch_one(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return "\n".join(r for r in results if isinstance(r, str) and r)


scanner = TechnologyScanner()
