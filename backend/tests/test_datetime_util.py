from core.datetime_util import utc_now, utc_now_iso


def test_utc_now_is_naive_utc_wall_clock():
    t = utc_now()
    assert t.tzinfo is None


def test_utc_now_iso_ends_with_z():
    assert utc_now_iso().endswith("Z")
