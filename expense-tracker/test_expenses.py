import pytest

import expenses


def test_add_and_read_back(tmp_path):
    f = tmp_path / "e.csv"
    expenses.add_expense(f, 12.5, "Food", "lunch", "2026-01-10")
    expenses.add_expense(f, 30, "travel", on="2026-01-11")
    rows = expenses.read_expenses(f)
    assert len(rows) == 2
    assert rows[0]["category"] == "food"
    assert rows[1]["amount"] == 30.0


def test_validation(tmp_path):
    f = tmp_path / "e.csv"
    with pytest.raises(ValueError):
        expenses.add_expense(f, 0, "food")
    with pytest.raises(ValueError):
        expenses.add_expense(f, 5, "  ")
    with pytest.raises(ValueError):
        expenses.add_expense(f, 5, "food", on="10-01-2026")


def test_summaries(tmp_path):
    f = tmp_path / "e.csv"
    expenses.add_expense(f, 10, "food", on="2026-01-05")
    expenses.add_expense(f, 15, "food", on="2026-02-05")
    expenses.add_expense(f, 40, "rent", on="2026-02-06")
    rows = expenses.read_expenses(f)
    by_cat = expenses.summarize_by_category(rows)
    assert list(by_cat) == ["rent", "food"]
    assert by_cat["food"] == 25.0
    assert expenses.summarize_by_month(rows) == {"2026-01": 10.0, "2026-02": 55.0}


def test_cli(tmp_path, capsys):
    f = tmp_path / "e.csv"
    assert expenses.main(["--file", str(f), "add", "9.99", "coffee", "-d", "2026-03-01"]) == 0
    assert expenses.main(["--file", str(f), "categories"]) == 0
    out = capsys.readouterr().out
    assert "coffee" in out and "9.99" in out
    assert expenses.main(["--file", str(f), "add", "-5", "bad"]) == 1


def test_accepts_plain_string_paths(tmp_path):
    f = str(tmp_path / "e.csv")
    expenses.add_expense(f, 5, "tea", on="2026-01-01")
    assert expenses.read_expenses(f)[0]["category"] == "tea"
