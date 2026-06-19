from datetime import timedelta

def compute_nishita_kaal(sunset_dt, next_sunrise_dt=None):

    if not sunset_dt:
        return None

    # temporary V1: midnight centered 48 min window
    midnight = sunset_dt.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    ) + timedelta(days=1)

    start = midnight - timedelta(minutes=24)
    end = midnight + timedelta(minutes=24)

    return {
        "start": start.strftime("%H:%M:%S"),
        "end": end.strftime("%H:%M:%S")
    }