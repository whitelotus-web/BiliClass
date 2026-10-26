"""Stable saved rate identities shared by preview, lessons and portable audio."""

SPEEDS = {-6: .60, -5: .70, -4: .75, -3: .82, -2: .88, -1: .94,
          0: 1., 1: 1.06, 2: 1.12, 3: 1.18}


def valid_rate(rate):
    return type(rate) is int and rate in SPEEDS


def speed_for(rate):
    if not valid_rate(rate):
        raise ValueError('Tốc độ giọng đọc không hợp lệ.')
    return SPEEDS[rate]


def rate_choices():
    return [dict(rate=rate, percent=round(speed * 100), label=f'{round(speed * 100)}%')
            for rate, speed in SPEEDS.items()]


def rate_for(values, language):
    return values.get(language + '_rate', values.get('rate', 0))


def valid_rates(values):
    return all(valid_rate(rate_for(values, language)) for language in ('vi', 'en'))


def rates_label(values, mode='both'):
    vi, en = (round(speed_for(rate_for(values, lang)) * 100) for lang in ('vi', 'en'))
    if mode == 'both' and vi != en:
        return f'Việt {vi}% · Anh {en}%'
    return f'{en if mode == "en" else vi}%'
