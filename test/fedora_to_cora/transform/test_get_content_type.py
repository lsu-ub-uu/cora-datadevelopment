import pytest
from fedora_to_cora.transform.get_content_type import get_content_type

class TestGetContentType:
    @pytest.mark.parametrize(
        "input_code,expected_output",
        [
            ("refereed", "ref"),
            ("science", "vet"),
            ("other", "pop"),
            ("refereedArtisticOutput", "ref"),
            ("unrefereedArtisticOutput", "vet"),
        ],
    )
    def test_get_content_type_returns_correct_content_type(self, input_code, expected_output):
        assert get_content_type(input_code) == expected_output

    def test_get_content_type_raises_key_error_on_invalid_code(self):
        with pytest.raises(KeyError):
            get_content_type("fel")
