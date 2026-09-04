from app.schemas.lookup import TechnologyDetection, TechnologyInfo
from app.services.technology.scanner import scanner
from app.services.technology.detectors import analyze_all


class TechnologyService:
    async def scan_domain(self, domain: str) -> TechnologyInfo:
        """
        Scans a domain for technologies using HTML, headers, cookies,
        inline scripts, JS bundle content, and script URLs.
        Returns a TechnologyInfo object with all detected technologies.
        """
        page_data = await scanner.fetch_page_data(domain)

        if not page_data["success"]:
            return TechnologyInfo()

        results = analyze_all(
            html=page_data["html"],
            headers=page_data["headers"],
            cookies=page_data["cookies"],
            scripts=page_data["scripts"],
            meta=page_data["meta"],
            inline_scripts=page_data.get("inline_scripts", []),
            js_bundle_content=page_data.get("js_bundle_content", ""),
        )

        # Sort each category by confidence descending
        for category in results:
            results[category] = sorted(results[category], key=lambda x: x.confidence, reverse=True)

        return TechnologyInfo(
            frontend=results.get("frontend", []),
            packages=results.get("packages", []),
            backend=results.get("backend", []),
            infrastructure=results.get("infrastructure", []),
            cdn=results.get("cdn", []),
            analytics=results.get("analytics", []),
        )


technology_service = TechnologyService()
