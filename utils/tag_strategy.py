from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True, slots=True)
class TagProfile:
    """Recommended tag mix, not a claim about a platform's hard limits."""

    limit: int
    quotas: Mapping[str, int]


TAG_TIERS = ("exact", "category", "identity", "broad")

PLATFORM_TAG_PROFILES: dict[str, TagProfile] = {
    "douyin": TagProfile(5, {"exact": 2, "category": 1, "identity": 1, "broad": 1}),
    "xiaohongshu": TagProfile(5, {"exact": 2, "category": 1, "identity": 1, "broad": 1}),
    "bilibili": TagProfile(5, {"exact": 2, "category": 2, "identity": 1, "broad": 0}),
    "tiktok": TagProfile(5, {"exact": 2, "category": 1, "identity": 1, "broad": 1}),
    "instagram": TagProfile(5, {"exact": 2, "category": 1, "identity": 1, "broad": 1}),
}


def normalize_tags(tags: Iterable[str]) -> list[str]:
    """Strip hash prefixes and de-duplicate tags while preserving their order."""
    result: list[str] = []
    seen: set[str] = set()
    for raw_tag in tags:
        tag = raw_tag.strip().lstrip("#").strip()
        key = tag.casefold()
        if tag and key not in seen:
            result.append(tag)
            seen.add(key)
    return result


def refine_tags(
    platform: str,
    *,
    exact: Iterable[str] = (),
    category: Iterable[str] = (),
    identity: Iterable[str] = (),
    broad: Iterable[str] = (),
    limit: int | None = None,
) -> list[str]:
    """Build a balanced, platform-aware tag list from user-supplied candidates."""
    if platform not in PLATFORM_TAG_PROFILES:
        supported = ", ".join(PLATFORM_TAG_PROFILES)
        raise ValueError(f"Unsupported tag platform: {platform}. Choose from: {supported}")

    profile = PLATFORM_TAG_PROFILES[platform]
    selected_limit = profile.limit if limit is None else limit
    if not 1 <= selected_limit <= 30:
        raise ValueError("Tag limit must be between 1 and 30")

    pools = {
        "exact": normalize_tags(exact),
        "category": normalize_tags(category),
        "identity": normalize_tags(identity),
        "broad": normalize_tags(broad),
    }
    selected: list[str] = []

    def add(tag: str) -> None:
        if tag.casefold() not in {item.casefold() for item in selected}:
            selected.append(tag)

    # First honor the recommended mix for the platform.
    for tier in TAG_TIERS:
        for tag in pools[tier][: profile.quotas[tier]]:
            if len(selected) < selected_limit:
                add(tag)

    # Then fill unused slots with remaining precise-to-broad candidates.
    for tier in TAG_TIERS:
        for tag in pools[tier]:
            if len(selected) >= selected_limit:
                return selected
            add(tag)
    return selected
