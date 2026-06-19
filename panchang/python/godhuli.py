from datetime import timedelta


def compute_godhuli_muhurta(sunset_dt):

    if not sunset_dt:
        return None

    start = sunset_dt - timedelta(minutes=24)
    end = sunset_dt + timedelta(minutes=24)

    return {
        "start": start.strftime("%H:%M:%S"),
        "end": end.strftime("%H:%M:%S")
    }