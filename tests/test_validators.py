"""Focused tests for shared validation contracts."""
import pytest
from shared.validators import validate_username,validate_password,validate_message,validate_group_title
from shared.errors import ValidationError

@pytest.mark.parametrize("value",["alice","bob_22","USER123","three_chars"])
def test_valid_username_examples(value):
    assert validate_username(value)==value

@pytest.mark.parametrize("value",["","ab","bad name","x-y","a"*33])
def test_invalid_username_examples(value):
    with pytest.raises(ValidationError): validate_username(value)

@pytest.mark.parametrize("value",["12345678","correct horse battery","P@ssword123"])
def test_password_minimum_examples(value):
    assert validate_password(value)==value

@pytest.mark.parametrize("value",["","short","x"*129])
def test_invalid_password_examples(value):
    with pytest.raises(ValidationError): validate_password(value)

def test_message_is_trimmed():
    assert validate_message(" hello ")=="hello"

def test_empty_message_is_rejected():
    with pytest.raises(ValidationError): validate_message("  ")

def test_group_title_is_trimmed():
    assert validate_group_title("  Team  ")=="Team"
