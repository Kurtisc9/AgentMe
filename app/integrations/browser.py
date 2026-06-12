from __future__ import annotations

from app.integrations.base import BaseIntegration, IntegrationResult


class BrowserIntegration(BaseIntegration):
    name = "browser"
    description = "Controlled browser automation through Playwright."
    actions = ("open_url", "capture_title")

    def execute(self, *, action: str, payload: dict[str, object]) -> IntegrationResult:
        if action not in self.actions:
            raise ValueError(f"Unsupported browser action: {action}")

        url = str(payload.get("url", "")).strip()
        if not url.startswith(("http://", "https://")):
            raise ValueError("A valid http or https URL is required.")

        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise RuntimeError("Playwright is required for browser automation.") from exc

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            output = page.title() if action == "capture_title" else page.url
            browser.close()

        return IntegrationResult(
            integration_name=self.name,
            action=action,
            success=True,
            output=output,
        )
