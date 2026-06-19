from datetime import datetime, timedelta

# weekday:
# 0 Monday
# 1 Tuesday
# 2 Wednesday
# 3 Thursday
# 4 Friday
# 5 Saturday
# 6 Sunday

DURMUHURTA_RULES = {
    0: [(8, 9)],          # Monday
    1: [(4, 5)],          # Tuesday
    2: [(5, 6)],          # Wednesday
    3: [(6, 7)],          # Thursday
    4: [(4, 5), (9,10)], # Friday
    5: [(2, 3)],          # Saturday
    6: [(7, 8)]           # Sunday
}


def compute_durmuhurta(sunrise_dt, sunset_dt):

    weekday = sunrise_dt.weekday()

    periods = DURMUHURTA_RULES.get(
        weekday,
        []
    )

    day_duration = (
        sunset_dt - sunrise_dt
    ).total_seconds()

    muhurta_duration = (
        day_duration / 15
    )

    result = []

    for start_no, end_no in periods:

        start_time = (
            sunrise_dt
            +
            timedelta(
                seconds=
                muhurta_duration * start_no
            )
        )

        end_time = (
            sunrise_dt
            +
            timedelta(
                seconds=
                muhurta_duration * end_no
            )
        )

        result.append({
            "start":
                start_time.strftime(
                    "%H:%M:%S"
                ),

            "end":
                end_time.strftime(
                    "%H:%M:%S"
                )
        })

    return result