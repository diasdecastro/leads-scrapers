import re
from typing import Optional
from deutschland import bundesanzeiger
import json
import time

from utils.db import get_company_id_by_name, insert_enriched_company
import os


class BundesanzeigerScraper:
    @staticmethod
    def normalize_number(raw: str) -> float:
        """
        Konvertiert z. B. "695.263,86" → 695263.86
        """
        raw = raw.replace(".", "").replace(",", ".")
        return float(raw)

    @staticmethod
    def extract_bilanzsumme(text: str) -> Optional[float]:
        """
        Sucht nach der Bilanzsumme auf der Aktiv-/Passivseite
        """
        text = text.lower()

        patterns = [
            # 1. klassische Formulierungen
            r"summe\s+(aktiva|passiva)[^\d]{0,20}([\d\.,]+)",
            # 2. Kompakte Textform mit beiden Summen
            r"aktiva\s+[\d\.,]+\s+passiva\s+([\d\.,]+)",
            # 3. Nur "passiva" mit Wert
            r"passiva\s+([\d\.,]+)",
            # 4. neue: explizite AKTIVA-Zeile mit Zahl (z. B. "aktiva\n...48.670.387,13")
            r"aktiva[^\d]{0,20}([\d\.,]{6,})",
            # 5. neue: explizite PASSIVA-Zeile mit Zahl
            r"passiva[^\d]{0,20}([\d\.,]{6,})",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return BundesanzeigerScraper.normalize_number(
                        match.group(2 if len(match.groups()) > 1 else 1)
                    )
                except:
                    continue
        return None

    @staticmethod
    def extract_mitarbeiterzahl(text: str) -> str:
        patterns = [
            r"beschäftigten (?:Arbeitnehmer|Mitarbeiter)[^0-9]{0,40}?(\d+)",  # klassischer Fall mit "beschäftigten"
            r"beschäftigt(?:en)?[^0-9]{0,20}?(\d+)\s+(?:Mitarbeiter|Arbeitnehmer)",  # "beschäftigt 5 Mitarbeiter"
            r"im Berichtsjahr[^0-9]{0,40}?(\d+)\s+(?:Mitarbeiter|Arbeitnehmer)\s+beschäftigt",  # "im Berichtsjahr ... 5 Mitarbeiter beschäftigt"
            r"durchschnittlich(?:[^0-9]{0,15})?(\d+)\s+(?:Mitarbeiter|Arbeitnehmer)",  # "durchschnittlich 5 Mitarbeiter"
            r"keine\s+(?:Mitarbeiter|Arbeitnehmer)\s+beschäftigt",  # "keine Mitarbeiter beschäftigt"
            r"im (?:Geschäfts|Berichts)jahr(?:[^0-9]{0,30})?(\d+)\s+(?:Personen|Mitarbeiter|Arbeitnehmer)\s+(?:beschäftigt|tätig)",
            r"durchschnittlich(?:[^0-9]{0,20})?(\d+)\s+(?:Mitarbeiter|Arbeitnehmer|Personen)",
            r"die\s+durchschnittliche\s+(?:Zahl|Anzahl)[^0-9]{0,20}(\d+)",
            r"im\s+(?:Jahresmittel|Mittel)\s+(?:waren\s+)?(\d+)\s+(?:Mitarbeiter|Arbeitnehmer)\s+(?:beschäftigt|tätig)",
            r"(?:keine\s+(?:Mitarbeiter|Arbeitnehmer|Personen)\s+(?:beschäftigt|angestellt|tätig))",
            r"(?:Anzahl\s+)?(?:Beschäftigte|Mitarbeiter|Arbeitnehmer)[^0-9]{0,10}[:\-]?\s*(\d+)",
            r"Personalaufwand.*?\(\s*(\d+)\s*(?:Mitarbeiter|Arbeitnehmer)?\s*\)",
            r"[Ø∅]?-?\s*Mitarbeiter[^0-9]{0,10}(\d+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Wenn „keine Mitarbeiter beschäftigt“, gib 0 zurück
                if "keine" in match.group(0).lower():
                    return "0"
                return match.group(1)
        return ""

    def extract_fields_from_report(self, report_text: str) -> dict:
        bilanzsumme = self.extract_bilanzsumme(report_text)
        mitarbeiter = self.extract_mitarbeiterzahl(report_text)
        return {
            "bilanzsumme": bilanzsumme if bilanzsumme is not None else "",
            "mitarbeiter": mitarbeiter if mitarbeiter is not None else "",
        }

    def get_jahresabschluss_report(self, company_name: str):
        try:
            ba = bundesanzeiger.Bundesanzeiger()
            reports = ba.get_reports(company_name)
            if not reports or not isinstance(reports, dict):
                print("⚠️ Keine Reports gefunden oder falsches Format.")
                return None

            for report_id, report in reports.items():
                if "Jahresabschluss" in report.get("name", ""):
                    print(f"📄 Jahresabschluss-Report gefunden: {report.get('name')}")
                    return report
            return None
        except Exception as e:
            print(f"❌ Fehler beim Abrufen der Reports: {e}")
            return None

    def print_jahresabschluss_info(self, company_names):
        if isinstance(company_names, str):
            company_names = [company_names]
        for company_name in company_names:
            report = self.get_jahresabschluss_report(company_name)
            if report:
                print("📊 Report Properties:")
                for key, value in report.items():
                    if key == "report":
                        print(f"{key}")
                    else:
                        print(f"{key}")
                print("================ VALUES =================")
                print(f"Datum: {report.get('date')}")
                print(f"Name: {report.get('name')}")
                print(f"Company: {report.get('company')}")
                print(f"Inhalt: {report.get('report')}")
                print(
                    f"Mitarbeiter + Billanzsumme: {self.extract_fields_from_report(report.get('report', ''))}\n"
                )
            else:
                print(f"Kein Jahresabschluss-Report gefunden für {company_name}.")

    def save_jahresabschluss_to_file(self, company_names):
        if isinstance(company_names, str):
            company_names = [company_names]
        for company_name in company_names:
            try:
                # Add a delay to avoid rate limiting
                time.sleep(2)
                report = self.get_jahresabschluss_report(company_name)
                if report:
                    os.makedirs("files/bundesanzeiger_reports", exist_ok=True)
                    company_name_sanitized = (
                        str(report.get("company", ""))
                        .replace("/", "_")
                        .replace("\\", "_")
                    )
                    report_name_sanitized = (
                        str(report.get("name", "")).replace("/", "_").replace("\\", "_")
                    )
                    filename = f"files/bundesanzeiger_reports/{company_name_sanitized}_{report_name_sanitized}.json"
                    fields = self.extract_fields_from_report(report.get("report", ""))
                    stringified_fields = {
                        str(key): str(value) for key, value in fields.items()
                    }
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(
                            {
                                "company": str(report.get("company", "")),
                                "date": str(report.get("date", "")),
                                "name": str(report.get("name", "")),
                                "fields": stringified_fields,
                                "full_report": str(report.get("report", "")),
                                "raw_report": report.get("raw_report", ""),
                            },
                            f,
                            ensure_ascii=False,
                            indent=2,
                        )
                    print(f"Report saved to {filename}")
                else:
                    print(f"Kein Jahresabschluss-Report gefunden für {company_name}.")
            except Exception as e:
                print(f"Error saving report to file for {company_name}: {e}")

    def store_report_data_to_db(self, company_names):
        if isinstance(company_names, str):
            company_names = [company_names]
        for company_name in company_names:
            try:
                # Add a delay to avoid rate limiting
                report = self.get_jahresabschluss_report(company_name)
                # time.sleep(5)
                if report:
                    fields = self.extract_fields_from_report(report.get("report", ""))
                    data = {
                        "company_id": get_company_id_by_name(company_name),
                        "publikationsdatum": report.get("date"),
                        "bilanzsumme": fields.get("bilanzsumme"),
                        "mitarbeiter": (
                            int(fields.get("mitarbeiter"))
                            if fields.get("mitarbeiter")
                            and str(fields.get("mitarbeiter")).isdigit()
                            else -1
                        ),
                    }
                    insert_enriched_company(data)
                    print(f"✅ Daten für {company_name} erfolgreich gespeichert.")
                else:
                    print(f"⚠️ Kein Jahresabschluss-Report gefunden für {company_name}.")
                    continue
            except Exception as e:
                print(f"❌ Fehler beim Speichern der Daten für {company_name}: {e}")


# Example usage:
if __name__ == "__main__":
    scraper = BundesanzeigerScraper()
    # scraper.print_jahresabschluss_info("Deutsche Wohnen SE")
