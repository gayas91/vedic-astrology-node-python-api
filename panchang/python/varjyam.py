from datetime import timedelta

VARJYAM_OFFSETS = {
    1: 50,  2: 24,  3: 30,  4: 40,  5: 14,
    6: 21,  7: 30,  8: 20,  9: 32,  10: 30,
    11: 20, 12: 18, 13: 21, 14: 20, 15: 14,
    16: 14, 17: 10, 18: 14, 19: 56, 20: 24,
    21: 20, 22: 10, 23: 10, 24: 18, 25: 16,
    26: 24, 27: 30
}


def compute_varjyam(nak_no, nak_start_dt, nak_end_dt):

    if not nak_no or not nak_start_dt or not nak_end_dt:
        return []

    nak_duration = (nak_end_dt - nak_start_dt).total_seconds()

    offset_ghati = VARJYAM_OFFSETS.get(nak_no)

    if offset_ghati is None:
        return []

    # 1 ghati = 24 minutes
    offset_seconds = offset_ghati * 24 * 60

    # Varjyam duration commonly taken as 4 ghati = 96 minutes
    varjyam_duration = 4 * 24 * 60

    start = nak_start_dt + timedelta(seconds=offset_seconds)

    end = start + timedelta(seconds=varjyam_duration)

    # If calculated varjyam falls outside current nakshatra window,
    # still return it because Panchang often reports next-day varjyam.
    return [
        {
            "start": start.strftime("%H:%M:%S"),
            "end": end.strftime("%H:%M:%S")
        }
    ]