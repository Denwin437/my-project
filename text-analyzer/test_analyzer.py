import analyzer


def test_words_and_sentences():
    text = "Hello world. This is a test! Is it working?"
    assert len(analyzer.words(text)) == 9
    assert analyzer.sentence_count(text) == 3


def test_word_frequency_skips_stop_words():
    top = analyzer.word_frequency("the cat and the cat and the dog", top=2)
    assert top[0] == ("cat", 2)
    assert ("the", 3) not in top


def test_reading_time():
    assert analyzer.reading_time_minutes("word " * 400) == 2.0


def test_syllables():
    assert analyzer.count_syllables("the") == 1
    assert analyzer.count_syllables("make") == 1
    assert analyzer.count_syllables("table") == 2
    assert analyzer.count_syllables("hello") == 2


def test_flesch_simple_text_is_easy():
    assert analyzer.flesch_reading_ease("The cat sat. The dog ran.") > 80


def test_empty_text():
    assert analyzer.flesch_reading_ease("") == 0.0
    assert analyzer.analyze("")["words"] == 0


def test_cli_reads_file(tmp_path, capsys):
    f = tmp_path / "a.txt"
    f.write_text("Python is fun. Python is fast.", encoding="utf-8")
    assert analyzer.main([str(f), "--top", "1"]) == 0
    assert "python" in capsys.readouterr().out
