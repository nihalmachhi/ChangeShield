from changeshield.analysis import analyze
from changeshield.models import ChangeRequest


def request(after_links, unsupported=None):
    return ChangeRequest.model_validate(
        {
            "name": "test change",
            "before": {
                "nodes": ["client", "service", "db"],
                "links": [
                    {"source": "client", "target": "service", "config_line": "router-a:12"},
                    {"source": "service", "target": "db", "config_line": "router-b:24"},
                ],
            },
            "after": {
                "nodes": ["client", "service", "db"],
                "links": after_links,
                "unsupported_lines": unsupported or [],
            },
            "intents": [
                {
                    "name": "client reaches database",
                    "source": "client",
                    "destination": "db",
                    "critical": True,
                }
            ],
        }
    )


def test_blocking_required_path_fails_with_provenance():
    result = analyze(
        request([{"source": "client", "target": "service", "config_line": "router-a:12"}])
    )
    assert result["verdict"] == "FAIL"
    assert result["findings"][0]["before_path"] == ["client", "service", "db"]
    assert result["findings"][0]["after_path"] is None
    assert result["findings"][0]["responsible_lines"]


def test_unchanged_connectivity_passes():
    result = analyze(
        request([{"source": "client", "target": "service"}, {"source": "service", "target": "db"}])
    )
    assert result["verdict"] == "PASS"


def test_unsupported_configuration_reduces_confidence():
    unsupported = [
        {"device": "router-a", "line_number": n, "text": "vendor-specific directive"}
        for n in range(1, 6)
    ]
    result = analyze(request([{"source": "client", "target": "service"}], unsupported))
    assert result["verdict"] == "NEEDS_REVIEW"
    assert result["confidence"] < 0.5
    assert result["parser_coverage"] < 1
