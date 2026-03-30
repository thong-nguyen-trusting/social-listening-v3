from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ActionSpec:
    action_type: str
    read_or_write: str
    risk_level: str
    description: str


_ACTION_SPECS = (
    ActionSpec(
        action_type="SEARCH_GROUPS",
        read_or_write="READ",
        risk_level="LOW",
        description="Search Facebook groups matching a keyword cluster and identify public or private targets.",
    ),
    ActionSpec(
        action_type="CRAWL_FEED",
        read_or_write="READ",
        risk_level="LOW",
        description="Enter an accessible group and crawl feed posts for downstream theme analysis.",
    ),
    ActionSpec(
        action_type="JOIN_GROUP",
        read_or_write="WRITE",
        risk_level="HIGH",
        description="Send a join request to a private or closed group that looks relevant.",
    ),
    ActionSpec(
        action_type="CHECK_JOIN_STATUS",
        read_or_write="READ",
        risk_level="LOW",
        description="Check whether previously requested private-group memberships were approved before crawling.",
    ),
    ActionSpec(
        action_type="SEARCH_POSTS",
        read_or_write="READ",
        risk_level="LOW",
        description="Search Facebook for public posts matching a keyword with Recent filter, extract posts and discover source groups.",
    ),
    ActionSpec(
        action_type="CRAWL_COMMENTS",
        read_or_write="READ",
        risk_level="LOW",
        description="Navigate to discovered posts and expand/collect comments and replies.",
    ),
    ActionSpec(
        action_type="SEARCH_IN_GROUP",
        read_or_write="READ",
        risk_level="LOW",
        description="Search within a specific Facebook group for posts matching a keyword query.",
    ),
)

ACTION_REGISTRY: dict[str, ActionSpec] = {spec.action_type: spec for spec in _ACTION_SPECS}
SUPPORTED_ACTION_TYPES: tuple[str, ...] = tuple(spec.action_type for spec in _ACTION_SPECS)


def normalize_action_type(value: str) -> str:
    return value.strip().upper()


def get_action_spec(action_type: str) -> ActionSpec | None:
    return ACTION_REGISTRY.get(normalize_action_type(action_type))


def is_supported_action(action_type: str) -> bool:
    return get_action_spec(action_type) is not None


def render_action_registry_for_prompt() -> str:
    lines = [
        "SUPPORTED_ACTION_REGISTRY",
        "",
        "Use only the action_type values from this registry. Do not invent new actions.",
        "",
        "| Action | read_or_write | risk | Description |",
        "|---|---|---|---|",
    ]
    for spec in _ACTION_SPECS:
        lines.append(
            f"| {spec.action_type} | {spec.read_or_write} | {spec.risk_level} | {spec.description} |"
        )
    lines.extend(
        [
            "",
            f"Allowed action_type values: {', '.join(SUPPORTED_ACTION_TYPES)}",
        ]
    )
    return "\n".join(lines)


def plan_step_action_check_constraint_sql() -> str:
    allowed = ",".join(f"'{action_type}'" for action_type in SUPPORTED_ACTION_TYPES)
    return f"action_type IN ({allowed})"
