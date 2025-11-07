import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import time
import os
from config.browser import BrowserManager
from utils.db import get_all_raw_companies, update_official_name_for_company
import ollama  # Für lokale LLM-Nutzung

IMPRINT_KEYWORDS = ["impressum", "imprint", "legal", "kontakt"]
IMPRINT_NOT_FOUND_LOG = "imprint_not_found.txt"


class OfficialNameExtractor:
    def __init__(self, llm_model="deepseek-r1:8b"):
        self.llm_model = llm_model

    def find_imprint_url(self, base_url):
        try:
            resp = requests.get(base_url, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"].lower()
                if any(kw in href for kw in IMPRINT_KEYWORDS):
                    return urljoin(base_url, a["href"])
            for kw in IMPRINT_KEYWORDS:
                test_url = urljoin(base_url, "/" + kw)
                try:
                    r = requests.get(test_url, timeout=5)
                    if r.status_code == 200 and "html" in r.headers.get(
                        "content-type", ""
                    ):
                        return test_url
                except Exception:
                    continue
        except Exception:
            pass
        return None

    def extract_with_regex(self, html):
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n")
        lines = text.splitlines()

        start_idx = next(
            (
                i
                for i, l in enumerate(lines)
                if "impressum" in l.lower() or "kontakt" in l.lower()
            ),
            0,
        )
        scoped_lines = lines[start_idx : start_idx + 40]
        address_pattern = re.compile(r"\d{4,5}\s+[A-ZÄÖÜa-zäöüß \-]+")
        company_pattern = re.compile(
            r"^(.*?\b(?:GmbH & Co KG|GmbH|UG|AG|OHG|e\.K\.|GbR|KG|mbH|Stiftung|Verein)\b.*)$",
            re.IGNORECASE,
        )

        candidates = []
        for i, line in enumerate(scoped_lines):
            m = company_pattern.match(line.strip())
            if m:
                candidates.append((i, m.group(1).strip()))

        for idx, name in candidates:
            nearby = "\n".join(scoped_lines[max(0, idx - 3) : idx + 4])
            if address_pattern.search(nearby):
                if not any(
                    bad in name.lower() for bad in ["host", "cookie", "provider"]
                ):
                    return name

        for idx, name in candidates:
            if not any(bad in name.lower() for bad in ["host", "cookie", "provider"]):
                return name

        return ""

    def extract_with_llm(self, html):
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n")
        prompt = f"""
            The following is text from a company's contact or imprint page:

            {text}

            Your task:
            Extract the official full company name including the legal form (e.g. GmbH, UG, AG, OHG, e.K., GmbH & Co. KG).

            Rules:
            - Output the company name only, nothing else.
            - Do not add any explanation, reasoning, or formatting.
            - Do not include any tags like <think> or notes.

            Examples:
            Input: Foo AG
            Output: Foo AG

            Input: Bar GmbH & Co. KG
            Output: Bar GmbH & Co. KG

            Input: Baz UG (haftungsbeschränkt)
            Output: Baz UG (haftungsbeschränkt)

            Now extract from this text:
        """

        try:
            response = ollama.chat(
                model=self.llm_model,
                messages=[{"role": "user", "content": prompt + text}],
            )
            result = response["message"]["content"].strip().splitlines()[0]
            return result
        except Exception as e:
            print(f"❌ LLM extraction failed: {e}")
            return ""

    def run_enrichment(self, delay=1, method="regex"):
        companies = get_all_raw_companies()
        enriched_count = 0
        os.makedirs("imprint_debug", exist_ok=True)

        with BrowserManager() as browser:
            for company in companies:
                url = company.get("url")
                if not url:
                    continue

                page = browser.get_page()
                print(f"Processing: {company['name']} ({url})")

                try:
                    page.goto(url, timeout=10000, wait_until="domcontentloaded")

                    imprint_url = None
                    links = page.query_selector_all("a[href]")
                    for link in links:
                        href_attr = link.get_attribute("href")
                        if href_attr and any(
                            kw in href_attr.lower() for kw in IMPRINT_KEYWORDS
                        ):
                            imprint_url = urljoin(url, href_attr)
                            break

                    if not imprint_url:
                        for kw in IMPRINT_KEYWORDS:
                            test_url = urljoin(url, "/" + kw)
                            try:
                                resp = page.goto(test_url, timeout=5000)
                                if resp and resp.ok:
                                    imprint_url = test_url
                                    break
                            except Exception:
                                continue

                    if not imprint_url:
                        print("  ❌ Imprint page not found.")
                        with open(IMPRINT_NOT_FOUND_LOG, "a", encoding="utf-8") as f:
                            f.write(f"{url}\n")
                        continue

                    page.goto(imprint_url, timeout=10000)
                    html = page.content()

                    if method == "regex":
                        official_name = self.extract_with_regex(html)
                    elif method == "llm":
                        official_name = self.extract_with_llm(html)
                    else:
                        print(f"❌ Unknown method: {method}")
                        continue

                    if official_name:
                        print(
                            f"  📝 Debug - Official name to save: '{official_name}' (length: {len(official_name)})"
                        )
                        update_official_name_for_company(company["id"], official_name)
                        print(f"  ✅ Official name found ({method}): {official_name}")
                        enriched_count += 1
                    else:
                        print(f"  ⚠️ Could not extract official name ({method}).")
                        print(f"  📝 Debug - Imprint URL: {imprint_url}")

                        # Extract a snippet of the text for debugging
                        soup = BeautifulSoup(html, "html.parser")
                        text_snippet = soup.get_text(separator="\n")[:500]
                        print(f"  📝 Debug - Text snippet: {text_snippet}...")

                        screenshot_path = (
                            f"imprint_debug/failed_extract_{company['id']}.png"
                        )
                        page.screenshot(path=screenshot_path)
                        print(f"  📸 Screenshot saved to {screenshot_path}")

                except Exception as e:
                    print(f"  ❌ Error: {e}")
                    screenshot_path = f"imprint_debug/failed_fetch_{company['id']}.png"
                    try:
                        page.screenshot(path=screenshot_path)
                        print(f"  📸 Screenshot saved to {screenshot_path}")
                    except Exception as se:
                        print(f"  ❌ Could not take screenshot: {se}")

                time.sleep(delay)

        print(f"Done. {enriched_count} companies enriched with official names.")


if __name__ == "__main__":
    extractor = OfficialNameExtractor(llm_model="deepseek-r1:8b")
    extractor.run_enrichment(method="llm")
