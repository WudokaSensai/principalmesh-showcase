import json
import subprocess
import sys


def test_demo_is_deterministic_and_reports_real_decisions():
    outputs = [subprocess.run(
        [sys.executable, "-m", "showcase.demo"], capture_output=True,
        text=True, check=True, timeout=5).stdout for _ in range(2)]
    assert outputs[0] == outputs[1]
    report = json.loads(outputs[0])
    assert report["mode"] == "offline-simulation"
    assert report["crossed_pair"] == "denied"
    assert report["primary"]["attempts"] == 1
    assert report["quota_fallback"]["attempts"] == 2
    assert report["quota_fallback"]["route"] == "synthetic-backup"
    assert report["foreign_owner"] == "denied-before-provider-call"
