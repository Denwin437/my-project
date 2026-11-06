import pytest

import tasks


def test_add_assigns_incrementing_ids():
    items = []
    a = tasks.add_task(items, "First")
    b = tasks.add_task(items, "Second", "high")
    assert (a["id"], b["id"]) == (1, 2)
    assert b["priority"] == "high"


def test_add_rejects_empty_title_and_bad_priority():
    with pytest.raises(ValueError):
        tasks.add_task([], "   ")
    with pytest.raises(ValueError):
        tasks.add_task([], "Task", "urgent")


def test_complete_and_remove():
    items = []
    tasks.add_task(items, "Write tests")
    assert tasks.complete_task(items, 1)["done"] is True
    assert tasks.remove_task(items, 1)["title"] == "Write tests"
    assert items == []


def test_unknown_id_raises():
    with pytest.raises(KeyError):
        tasks.complete_task([], 99)


def test_format_sorts_by_status_then_priority():
    items = []
    tasks.add_task(items, "low one", "low")
    tasks.add_task(items, "high one", "high")
    tasks.add_task(items, "done one", "high")
    tasks.complete_task(items, 3)
    lines = tasks.format_tasks(items).splitlines()
    assert "high one" in lines[0]
    assert "low one" in lines[1]
    assert "done one" in lines[2]


def test_cli_round_trip(tmp_path, capsys):
    db = tmp_path / "db.json"
    assert tasks.main(["--db", str(db), "add", "Ship it", "-p", "high"]) == 0
    assert tasks.main(["--db", str(db), "done", "1"]) == 0
    assert tasks.main(["--db", str(db), "list", "--pending"]) == 0
    assert "No tasks." in capsys.readouterr().out
    assert tasks.main(["--db", str(db), "done", "42"]) == 1
