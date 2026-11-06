import string

import pytest

import passwords


def test_length_and_character_classes():
    for _ in range(50):
        pw = passwords.generate_password(12)
        assert len(pw) == 12
        assert any(c in string.ascii_lowercase for c in pw)
        assert any(c in string.ascii_uppercase for c in pw)
        assert any(c in string.digits for c in pw)
        assert any(c in passwords.SYMBOLS for c in pw)


def test_options_disable_classes():
    pw = passwords.generate_password(30, upper=False, digits=False, symbols=False)
    assert pw.islower() and pw.isalpha()


def test_too_short_rejected():
    with pytest.raises(ValueError):
        passwords.generate_password(3)


def test_passphrase():
    phrase = passwords.generate_passphrase(5, "+")
    assert len(phrase.split("+")) == 5
    with pytest.raises(ValueError):
        passwords.generate_passphrase(1)


def test_passwords_are_not_repeated():
    assert len({passwords.generate_password(16) for _ in range(100)}) == 100


def test_strength_labels():
    assert passwords.check_strength("password")["label"] == "very weak"
    assert passwords.check_strength("abc")["label"] == "weak"
    assert passwords.check_strength("Tr0ub4dor&3xK9!mQ")["label"] in ("strong", "excellent")
    assert passwords.check_strength("")["label"] == "empty"


def test_tips_are_given_for_weak_passwords():
    tips = passwords.check_strength("abcdefgh")["tips"]
    assert "Add digits" in tips and "Use at least 12 characters" in tips


def test_cli(capsys):
    assert passwords.main(["generate", "-l", "20"]) == 0
    assert len(capsys.readouterr().out.strip()) == 20
    assert passwords.main(["check", "password"]) == 0
    assert "very weak" in capsys.readouterr().out
    assert passwords.main(["generate", "-l", "2"]) == 1
