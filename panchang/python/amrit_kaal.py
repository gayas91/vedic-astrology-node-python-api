from datetime import timedelta

AMRIT_OFFSETS = {
    1: 18,  2: 36,  3: 30,  4: 24,  5: 30,
    6: 21,  7: 30,  8: 20,  9: 32,  10: 30,
    11: 20, 12: 18, 13: 21, 14: 20, 15: 14,
    16: 14, 17: 10, 18: 14, 19: 56, 20: 24,
    21: 20, 22: 10, 23: 10, 24: 18, 25: 16,
    26: 24, 27: 30
}


def compute_amrit_kaal(nak_no, nak_start_dt, nak_end_dt):

    if not nak_no or not nak_start_dt or not nak_end_dt:
        return []

    offset_ghati = AMRIT_OFFSETS.get(nak_no)

    if offset_ghati is None:
        return []

    offset_seconds = offset_ghati * 24 * 60

    # 4 ghati = 96 minutes
    amrit_duration = 4 * 24 * 60

    start = nak_start_dt + timedelta(seconds=offset_seconds)

    end = start + timedelta(seconds=amrit_duration)

    return [
        {
            "start": start.strftime("%H:%M:%S"),
            "end": end.strftime("%H:%M:%S")
        }
    ]