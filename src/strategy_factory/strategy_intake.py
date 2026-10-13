from __future__ import annotations

"""Source-agnostic intake records for externally discovered strategy ideas.

This layer records provenance and extracted claims. It does not scrape the web,
execute external code, decide whether a claim is true, define canonical rules,
or authorize backtests/Forward execution.
"""

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from enum import Enum
import json
import re
from urllib.parse import urlparse


class StrategyIntakeError(ValueError):
    """Raised when a strategy-source intake record is incomplete or unsafe."""


class StrategySourcePlatform(str, Enum):
    GITHUB = "GITHUB"
    YOUTUBE = "YOUTUBE"


_ALLOWED_HOSTS = {
    StrategySourcePlatform.GITHUB: {"github.com", "www.github.com"},
    StrategySourcePlatform.YOUTUBE: {
        "youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"
    },
}
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _canonical_payload(value: dict[str, object]) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")


@dataclass(frozen=True)
class StrategySourceIntake:
    """Immutable, source-agnostic record for one captured external strategy idea.

    snapshot_uri identifies the preserved local artifact; snapshot_sha256 binds
    the exact captured bytes. source_revision is provenance metadata, not a
    guarantee that an upstream URL/ref is immutable. Extracted claims and
    unresolved questions are separate so interpretation cannot silently become
    a source-confirmed rule.
    """

    intake_id: str
    platform: StrategySourcePlatform
    source_url: str
    source_title: str
    publisher: str
    source_revision: str
    captured_at_utc: str
    snapshot_uri: str
    snapshot_sha256: str
    strategy_claims: tuple[str, ...]
    unresolved_questions: tuple[str, ...] = ()
    extraction_notes: str = ""

    def validate(self) -> None:
        required = (
            self.intake_id, self.source_url, self.source_title, self.publisher,
            self.source_revision, self.captured_at_utc, self.snapshot_uri,
        )
        if not all(isinstance(value, str) and value.strip() for value in required):
            raise StrategyIntakeError("source intake identity and snapshot provenance are required")
        if not isinstance(self.platform, StrategySourcePlatform):
            raise StrategyIntakeError("platform must be an explicit supported source platform")

        parsed = urlparse(self.source_url)
        if parsed.scheme != "https" or not parsed.hostname:
            raise StrategyIntakeError("source_url must be an HTTPS URL")
        if parsed.hostname.lower() not in _ALLOWED_HOSTS[self.platform]:
            raise StrategyIntakeError("source_url host does not match the declared platform")
        if not parsed.path or parsed.path == "/":
            raise StrategyIntakeError("source_url must identify a specific source")

        if not isinstance(self.snapshot_sha256, str) or not _SHA256_RE.fullmatch(
            self.snapshot_sha256
        ):
            raise StrategyIntakeError("snapshot_sha256 must be 64 lowercase hexadecimal characters")

        try:
            captured = datetime.fromisoformat(self.captured_at_utc.replace("Z", "+00:00"))
        except (TypeError, ValueError) as exc:
            raise StrategyIntakeError("captured_at_utc must be an ISO-8601 UTC timestamp") from exc
        if captured.tzinfo is None or captured.utcoffset() is None or captured.utcoffset().total_seconds() != 0:
            raise StrategyIntakeError("captured_at_utc must use UTC offset +00:00 or Z")

        if not isinstance(self.strategy_claims, tuple) or not self.strategy_claims:
            raise StrategyIntakeError("at least one extracted strategy claim is required")
        if any(not isinstance(item, str) or not item.strip() for item in self.strategy_claims):
            raise StrategyIntakeError("strategy claims must be non-empty strings")
        if len(set(self.strategy_claims)) != len(self.strategy_claims):
            raise StrategyIntakeError("duplicate strategy claims are not allowed")
        if not isinstance(self.unresolved_questions, tuple):
            raise StrategyIntakeError("unresolved_questions must be a tuple")
        if any(not isinstance(item, str) or not item.strip() for item in self.unresolved_questions):
            raise StrategyIntakeError("unresolved questions must be non-empty strings")
        if len(set(self.unresolved_questions)) != len(self.unresolved_questions):
            raise StrategyIntakeError("duplicate unresolved questions are not allowed")
        if not isinstance(self.extraction_notes, str):
            raise StrategyIntakeError("extraction_notes must be a string")

    @property
    def fingerprint(self) -> str:
        self.validate()
        payload = {
            "intake_id": self.intake_id,
            "platform": self.platform.value,
            "source_url": self.source_url,
            "source_title": self.source_title,
            "publisher": self.publisher,
            "source_revision": self.source_revision,
            "captured_at_utc": self.captured_at_utc,
            "snapshot_uri": self.snapshot_uri,
            "snapshot_sha256": self.snapshot_sha256,
            "strategy_claims": list(self.strategy_claims),
            "unresolved_questions": list(self.unresolved_questions),
            "extraction_notes": self.extraction_notes,
        }
        return sha256(_canonical_payload(payload)).hexdigest()

    @property
    def candidate_intake_ready(self) -> bool:
        """Enough recorded material to draft a research candidate only."""
        self.validate()
        return bool(self.strategy_claims)

    @property
    def unresolved_count(self) -> int:
        self.validate()
        return len(self.unresolved_questions)

    def as_dict(self) -> dict[str, object]:
        self.validate()
        return {
            "intake_id": self.intake_id,
            "platform": self.platform.value,
            "source_url": self.source_url,
            "source_title": self.source_title,
            "publisher": self.publisher,
            "source_revision": self.source_revision,
            "captured_at_utc": self.captured_at_utc,
            "snapshot_uri": self.snapshot_uri,
            "snapshot_sha256": self.snapshot_sha256,
            "strategy_claims": list(self.strategy_claims),
            "unresolved_questions": list(self.unresolved_questions),
            "extraction_notes": self.extraction_notes,
            "fingerprint": self.fingerprint,
            "candidate_intake_ready": self.candidate_intake_ready,
            "unresolved_count": self.unresolved_count,
            "allowed_use": "RESEARCH_CANDIDATE_DRAFT_ONLY",
            "canonical": False,
            "backtest_approved": False,
            "forward_approved": False,
            "production_eligible": False,
        }
