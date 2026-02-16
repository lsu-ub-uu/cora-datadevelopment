from freezegun import freeze_time
from common.date_utils import is_before_now


@freeze_time("2026-01-01T00:00:00Z")
def test_is_before_now_true():
    assert is_before_now("2025-12-31T23:59:59Z") == True


@freeze_time("2026-01-01T00:00:00Z")
def test_is_before_now_false():
    assert is_before_now("2026-01-01T00:00:01Z") == False


@freeze_time("2026-01-01T01:00:00Z")
def test_is_before_now_true_with_timezone():
    assert is_before_now("2026-01-01T00:00:00.000+02:00") == True


@freeze_time("2026-01-01T01:00:00Z")
def test_is_before_now_false_with_timezone():
    assert is_before_now("2026-01-01T00:00:00.000-02:00") == False


@freeze_time("2026-01-01T00:00:00.000-02:00")
def test_is_before_now_is_now():
    assert is_before_now("2026-01-01T00:00:00.000-02:00") == False
