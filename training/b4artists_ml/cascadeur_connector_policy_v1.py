"""Receipt gate for the optional Cascadeur command connector.

The policy is deliberately independent of Cascadeur's embedded ``csc`` API.
It validates filtered evidence before an injected audit callable is allowed to
run.  A blocked receipt names only the failed evidence class; it never embeds
license, executable, or asset contents.
"""

from __future__ import annotations

from collections.abc import Mapping
import datetime as _dt
from dataclasses import dataclass
import re
from typing import Any, Callable, Optional


AUTHORIZED_PRODUCT = "B4Artists.ML"
REQUIRED_CAPABILITY = "import.audit.read_only"
# The digest is frozen for the currently audited Cascadeur installation.  A
# future installation update must deliberately update this release constant;
# an empty value is rejected by _check_executable and can never authorize.
EXPECTED_EXECUTABLE_SHA256 = (
    "195005351e8fca2ca0b1a05f94fa45e7fdd0ab43478e10b2bf01d50cddabac15"
)
ALLOWED_PROVENANCE_ORIGINS = frozenset({"b4artists.internal"})
SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")

REASON_MISSING = "missing_evidence"
REASON_INVALID = "invalid_evidence"
REASON_EXPIRED = "expired_license"
REASON_IDENTITY = "mismatched_executable_identity"
REASON_CAPABILITY = "missing_capability"
REASON_PROVENANCE = "invalid_frozen_asset_provenance"


@dataclass(frozen=True)
class ConnectorPolicy:
    """Immutable connector policy values."""

    authorized_product: str = AUTHORIZED_PRODUCT
    required_capability: str = REQUIRED_CAPABILITY
    expected_executable_sha256: str = EXPECTED_EXECUTABLE_SHA256
    allowed_provenance_origins: frozenset[str] = ALLOWED_PROVENANCE_ORIGINS


@dataclass(frozen=True)
class BlockedReceipt:
    """Bounded failure receipt that contains no underlying evidence."""

    reason: str
    evidence: str
    detail: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "reason": self.reason,
            "evidence": self.evidence,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class ConnectorOutcome:
    blocked: bool
    blocked_receipt: Optional[BlockedReceipt] = None
    audit_ran: bool = False
    result: Any = None


def _block(reason: str, evidence: str, detail: str = "") -> BlockedReceipt:
    return BlockedReceipt(reason=reason, evidence=evidence, detail=detail)


def _stamp(now: Optional[_dt.datetime]) -> _dt.datetime:
    value = now if now is not None else _dt.datetime.now(_dt.timezone.utc)
    if value.tzinfo is None:
        return value.replace(tzinfo=_dt.timezone.utc)
    return value.astimezone(_dt.timezone.utc)


def _check_license(
    policy: ConnectorPolicy, receipt: Any, now: _dt.datetime
) -> Optional[BlockedReceipt]:
    if receipt is None:
        return _block(REASON_MISSING, "license_receipt")
    if not isinstance(receipt, Mapping):
        return _block(REASON_INVALID, "license_receipt", "not a mapping")
    if receipt.get("product") != policy.authorized_product:
        return _block(REASON_INVALID, "license_receipt", "unexpected product")
    expires_raw = receipt.get("expires")
    if not isinstance(expires_raw, str) or not expires_raw.strip():
        return _block(REASON_INVALID, "license_receipt", "missing expiry")
    try:
        expires = _dt.datetime.fromisoformat(expires_raw)
    except ValueError:
        return _block(REASON_INVALID, "license_receipt", "unparsable expiry")
    expires = _stamp(expires)
    if expires < now:
        return _block(REASON_EXPIRED, "license_receipt")
    return None


def _check_executable(
    policy: ConnectorPolicy, receipt: Any
) -> Optional[BlockedReceipt]:
    if receipt is None:
        return _block(REASON_MISSING, "executable_id")
    if not isinstance(receipt, Mapping):
        return _block(REASON_INVALID, "executable_id", "not a mapping")
    digest = receipt.get("sha256")
    if not isinstance(digest, str) or not SHA256.fullmatch(digest):
        return _block(REASON_INVALID, "executable_id", "invalid digest")
    expected = policy.expected_executable_sha256
    if not isinstance(expected, str) or not SHA256.fullmatch(expected):
        return _block(REASON_IDENTITY, "executable_id", "release digest is not frozen")
    if digest.lower() != expected.lower():
        return _block(REASON_IDENTITY, "executable_id")
    return None


def _as_strings(value: Any) -> frozenset[str]:
    if not isinstance(value, (list, tuple, set, frozenset)):
        return frozenset()
    return frozenset(item for item in value if isinstance(item, str))


def _check_capability(
    policy: ConnectorPolicy, receipt: Any
) -> Optional[BlockedReceipt]:
    if receipt is None:
        return _block(REASON_MISSING, "capability_receipt")
    if not isinstance(receipt, Mapping):
        return _block(REASON_INVALID, "capability_receipt", "not a mapping")
    if policy.required_capability not in _as_strings(receipt.get("granted")):
        return _block(REASON_CAPABILITY, "capability_receipt")
    return None


def _check_provenance(
    policy: ConnectorPolicy, receipt: Any
) -> Optional[BlockedReceipt]:
    if receipt is None:
        return _block(REASON_MISSING, "frozen_assets")
    if not isinstance(receipt, Mapping):
        return _block(REASON_INVALID, "frozen_assets", "not a mapping")
    origin = receipt.get("origin")
    if not isinstance(origin, str) or origin not in policy.allowed_provenance_origins:
        return _block(REASON_PROVENANCE, "frozen_assets")
    return None


def run_connector(
    *,
    policy: ConnectorPolicy,
    license_receipt: Any,
    executable_id: Any,
    capability_receipt: Any,
    frozen_assets: Any,
    audit: Callable[[], Any],
    now: Optional[_dt.datetime] = None,
    receipt_writer: Optional[Callable[[BlockedReceipt], None]] = None,
) -> ConnectorOutcome:
    """Run ``audit`` only after all four evidence classes validate."""

    stamp = _stamp(now)
    checks = (
        _check_license(policy, license_receipt, stamp),
        _check_executable(policy, executable_id),
        _check_capability(policy, capability_receipt),
        _check_provenance(policy, frozen_assets),
    )
    for blocked in checks:
        if blocked is None:
            continue
        if receipt_writer is not None:
            receipt_writer(blocked)
        return ConnectorOutcome(blocked=True, blocked_receipt=blocked)
    if not callable(audit):
        blocked = _block(REASON_INVALID, "audit_callable", "not callable")
        if receipt_writer is not None:
            receipt_writer(blocked)
        return ConnectorOutcome(blocked=True, blocked_receipt=blocked)
    return ConnectorOutcome(blocked=False, audit_ran=True, result=audit())
