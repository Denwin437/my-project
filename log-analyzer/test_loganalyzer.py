from pathlib import Path

import loganalyzer

GOOD = '1.2.3.4 - - [05/Nov/2026:10:00:01 +0530] "GET /a HTTP/1.1" 200 100'


def test_parse_valid_line():
    entry = loganalyzer.parse_line(GOOD)
    assert entry["ip"] == "1.2.3.4"
    assert entry["method"] == "GET"
    assert entry["path"] == "/a"
    assert entry["status"] == 200
    assert entry["size"] == 100


def test_dash_size_is_zero():
    line = '1.2.3.4 - - [05/Nov/2026:10:00:01 +0530] "GET /a HTTP/1.1" 304 -'
    assert loganalyzer.parse_line(line)["size"] == 0


def test_malformed_returns_none():
    assert loganalyzer.parse_line("garbage") is None
    assert loganalyzer.parse_line("") is None


def test_analyze_counts():
    lines = [
        GOOD,
        GOOD.replace("200", "500"),
        GOOD.replace("1.2.3.4", "5.6.7.8").replace("200", "404"),
        "bad line",
        "",
    ]
    result = loganalyzer.analyze(lines)
    assert result["requests"] == 3
    assert result["malformed"] == 1
    assert result["status_classes"] == {"2xx": 1, "4xx": 1, "5xx": 1}
    assert result["error_rate"] == 33.3
    assert result["top_ips"][0] == ("1.2.3.4", 2)


def test_empty_input():
    result = loganalyzer.analyze([])
    assert result["requests"] == 0 and result["error_rate"] == 0.0


def test_sample_file(capsys):
    sample = Path(__file__).parent / "sample.log"
    assert loganalyzer.main([str(sample), "--top", "2"]) == 0
    out = capsys.readouterr().out
    assert "Requests:     7 (1 malformed" in out
    assert "/index.html" in out
