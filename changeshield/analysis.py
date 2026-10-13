from collections import deque

from changeshield.models import ChangeRequest, Snapshot


def path_between(snapshot: Snapshot, source: str, destination: str) -> list[str] | None:
    if source not in snapshot.nodes or destination not in snapshot.nodes:
        return None
    graph = {node: [] for node in snapshot.nodes}
    for link in snapshot.links:
        if link.enabled:
            graph[link.source].append(link.target)
            graph[link.target].append(link.source)
    parents = {source: None}
    queue = deque([source])
    while queue:
        current = queue.popleft()
        if current == destination:
            path = [current]
            while parents[path[-1]] is not None:
                path.append(parents[path[-1]])
            return list(reversed(path))
        for neighbor in graph[current]:
            if neighbor not in parents:
                parents[neighbor] = current
                queue.append(neighbor)
    return None


def link_set(snapshot: Snapshot):
    return {
        (min(link.source, link.target), max(link.source, link.target), link.enabled): link
        for link in snapshot.links
    }


def analyze(request: ChangeRequest) -> dict:
    before_links = link_set(request.before)
    after_links = link_set(request.after)
    changed = []
    for key in sorted(set(before_links) | set(after_links)):
        old, new = before_links.get(key), after_links.get(key)
        if old != new:
            changed.append(
                {
                    "from": old.model_dump() if old else None,
                    "to": new.model_dump() if new else None,
                    "responsible_line": (new or old).config_line,
                }
            )
    unsupported = request.before.unsupported_lines + request.after.unsupported_lines
    confidence = max(0.2, 1 - 0.12 * len(unsupported))
    findings = []
    for intent in request.intents:
        old_path = path_between(request.before, intent.source, intent.destination)
        new_path = path_between(request.after, intent.source, intent.destination)
        failed = (intent.property == "reachable" and old_path is not None and new_path is None) or (
            intent.property == "isolated" and new_path is not None
        )
        findings.append(
            {
                "intent": intent.name,
                "property": intent.property,
                "critical": intent.critical,
                "before_path": old_path,
                "after_path": new_path,
                "violated": failed,
                "responsible_lines": [item["responsible_line"] for item in changed]
                if failed
                else [],
            }
        )
    has_violation = any(item["violated"] for item in findings)
    low_confidence = confidence < (0.5 if any(f["critical"] for f in findings) else 0.7)
    verdict = "NEEDS_REVIEW" if low_confidence else ("FAIL" if has_violation else "PASS")
    if has_violation and low_confidence:
        verdict = "NEEDS_REVIEW"
    recognized = len(request.before.links) + len(request.after.links)
    coverage = (
        recognized / (recognized + len(unsupported)) if recognized + len(unsupported) else 1.0
    )
    return {
        "verdict": verdict,
        "confidence": round(confidence, 3),
        "parser_coverage": round(coverage, 3),
        "changed_links": changed,
        "findings": findings,
        "unsupported_lines": [line.model_dump() for line in unsupported],
        "limitations": [
            "Analyzes only declared nodes and links; device configuration syntax is not parsed.",
            "No device writes, deployment, or automatic remediation are performed.",
        ],
    }
