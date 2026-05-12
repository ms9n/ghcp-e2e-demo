import os
import sys


class Config:
    PORT: int = int(os.environ.get("PORT", "8080"))
    GITHUB_REPO: str = os.environ.get("GITHUB_REPO", "")
    GITHUB_TOKEN: str = os.environ.get("GITHUB_TOKEN", "")
    COPILOT_GITHUB_TOKEN: str = os.environ.get("COPILOT_GITHUB_TOKEN", "")

    @property
    def error_reporting_enabled(self) -> bool:
        return bool(self.GITHUB_REPO and self.GITHUB_TOKEN)

    def print_status(self) -> None:
        print(f"[config] PORT={self.PORT}")
        print(f"[config] GITHUB_REPO={'set' if self.GITHUB_REPO else 'NOT SET'}")
        print(f"[config] GITHUB_TOKEN={'set' if self.GITHUB_TOKEN else 'NOT SET'}")
        print(f"[config] COPILOT_GITHUB_TOKEN={'set' if self.COPILOT_GITHUB_TOKEN else 'NOT SET'}")
        if not self.error_reporting_enabled:
            print("[config] Error reporting DISABLED (set GITHUB_REPO + GITHUB_TOKEN to enable)")
        else:
            print(f"[config] Error reporting ENABLED -> {self.GITHUB_REPO}")


config = Config()
