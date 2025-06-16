import re
from deutschland import bundesanzeiger
from rapidfuzz.fuzz import ratio
from utils.db import get_all_raw_companies, insert_enriched_company
from datetime import datetime


class BundesanzeigerEnricher:
    def __init__(self):
        self.ba = bundesanzeiger.Bundesanzeiger()

    def is_relevant_report(self, entry):
        title = entry.get("name", "")
        if not title:
            return False

        title_lower = title.lower()
        relevant_keywords = [
            "jahresabschluss",
            "konzernabschluss",
            "lagebericht",
            "bilanz zum",
            "abschluss zum",
            "gewinn- und verlustrechnung",
            "jahresabschluss zum geschäftsjahr",
        ]

        return any(keyword in title_lower for keyword in relevant_keywords)

    def generate_search_variants(self, name: str) -> list[str]:
        clean = name.lower()
        for pattern in [
            r"\b(gmbh & co\. kg|gesellschaft mit beschränkter haftung|gmbh|ag|kg|mbh)\b",
            r"[,|\(].*",
        ]:
            clean = re.sub(pattern, "", clean)
        clean = re.sub(r"\s+", " ", clean).strip()
        variants = list(
            set(
                [
                    name.strip(),
                    clean.title(),
                    clean.upper(),
                    clean.replace(" ", ""),
                    clean.split()[0],
                ]
            )
        )
        return variants

    def find_best_report_entry(self, company_name: str) -> dict | None:
        search_variants = self.generate_search_variants(company_name)
        best_entry = None
        best_score = 0

        for variant in search_variants:
            try:
                reports = self.ba.get_reports(variant)
            except Exception as e:
                print(f"Fehler bei get_reports('{variant}'): {e}")
                continue

            if not isinstance(reports, dict):
                print(f"⚠️ Keine gültigen Reports für '{variant}'")
                continue

            for _, entry in reports.items():
                if not self.is_relevant_report(entry):
                    continue
                title = entry.get("name", "")
                company_in_report = entry.get("company", "")
                score_title = ratio(company_name.lower(), title.lower())
                score_company = ratio(company_name.lower(), company_in_report.lower())
                score = max(score_title, score_company)

                print(f"→ Kandidat: {title} ({company_in_report}) | Score: {score}")

                if score > best_score:
                    best_score = score
                    best_entry = entry

        return best_entry if best_score >= 75 else None

    def extract_financial_data(self, text: str):
        text = text.lower()
        umsatz = None
        mitarbeiter = None

        umsatz_patterns = [
            r"umsatz[^0-9]{0,20}([\d\.,]+)\s*(mio|millionen|mrd|milliarden)?",
            r"gesamterlöse[^0-9]{0,20}([\d\.,]+)\s*(mio|millionen|mrd|milliarden)?",
        ]
        for pattern in umsatz_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    num = float(match.group(1).replace(".", "").replace(",", "."))
                    factor = match.group(2)
                    if factor and "mrd" in factor:
                        num *= 1000
                    umsatz = num
                    break
                except:
                    pass

        mitarbeiter_patterns = [
            r"(\d{1,4})\s+(mitarbeiter|beschäftigte|angestellte|personen)",
            r"es waren\s+(\d{1,4})\s+(mitarbeiter|angestellte)",
        ]
        for pattern in mitarbeiter_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    mitarbeiter = int(match.group(1))
                    break
                except:
                    pass

        return umsatz, mitarbeiter

    def enrich_company(self, raw_company: dict):
        name = raw_company["name"]
        print(f"\n--- Enriching: {name} ---")
        entry = self.find_best_report_entry(name)
        if not entry:
            print("⚠️ Kein relevanter Report gefunden.")
            return None

        text = entry.get("report", "")
        publ_date = entry.get("date")

        umsatz, mitarbeiter = self.extract_financial_data(text)

        result = {
            "company_id": raw_company["id"],
            "source": "bundesanzeiger",
            "url": raw_company.get("url", ""),
            "umsatz_mio": umsatz,
            "mitarbeiter_min": mitarbeiter,
            "bilanzsumme_mio": None,
            "rechtsform": "",
            "publikationsdatum": publ_date.strftime("%Y-%m-%d") if publ_date else "",
            "sitz": "",
            "branche": "",
            "wz_code": "",
            "geschaeftsfuehrer": "",
            "eigentuemer": "",
            "confidence_score": 66.7,
        }
        print("✅ Enriched:", result)
        return result

    def run_enrichment(self, limit=50):
        companies = get_all_raw_companies()[:limit]
        enriched_count = 0
        for c in companies:
            enriched = self.enrich_company(c)
            if enriched:
                insert_enriched_company(enriched)
                enriched_count += 1
        print(f"\n🏁 {enriched_count}/{len(companies)} erfolgreich angereichert.")

    def test_enrich_deutsche_bahn(self):
        print("\n=== TEST: Deutsche Wohnen SE ===")
        test_company = {
            "id": 99999,
            "name": "Deutsche Wohnen SE",
            "url": "https://www.deutschebahn.com",
        }
        enriched = self.enrich_company(test_company)
        if enriched:
            print("✅ Test erfolgreich.")
        else:
            print("❌ Test fehlgeschlagen.")


# für main.py
def run_enrichment(limit=50):
    enricher = BundesanzeigerEnricher()
    enricher.run_enrichment(limit=limit)


def test_enrich_deutsche_bahn():
    enricher = BundesanzeigerEnricher()
    enricher.test_enrich_deutsche_bahn()
