"""A non-CLI interface to the `timeit` module's main method."""
from time import perf_counter
from timeit import Timer


def timeit(
    stmt='pass',  # Can be str or callable.
    *,
    setup='pass',  # Can be str or callable.
    globals=None,
    repeat=5,
    number=None,  # Default: auto-determine via Timer.autorange().
    verbose=False,
    timer=perf_counter,
    time_unit=None,
    units={"nsec": 1e-9, "usec": 1e-6, "msec": 1e-3, "sec": 1.0},
    precision=3,
):
    """Adapted (mostly pasted) from `timeit.main`."""
    if globals is None:
        import sys
        globals = sys._getframe(1).f_globals

    t = Timer(stmt, setup, timer, globals)
    if number is None:
        # determine number so that 0.2 <= total time < 2.0
        callback = None
        if verbose:
            def callback(number, time_taken):
                msg = "{num} loop{s} -> {secs:.{prec}g} secs"
                plural = (number != 1)
                print(msg.format(num=number, s='s' if plural else '',
                                 secs=time_taken, prec=precision))
        number, _ = t.autorange(callback)

        if verbose:
            print()

    raw_timings = t.repeat(repeat, number)

    def format_time(dt):
        unit = time_unit

        if unit is not None:
            scale = units[unit]
        else:
            scales = [(scale, unit) for unit, scale in units.items()]
            scales.sort(reverse=True)
            for scale, unit in scales:
                if dt >= scale:
                    break

        return "%.*g %s" % (precision, dt / scale, unit)

    if verbose:
        print("raw times: %s" % ", ".join(map(format_time, raw_timings)))
        print()
    timings = [dt / number for dt in raw_timings]

    best = min(timings)
    print("%d loop%s, best of %d: %s per loop"
          % (number, 's' if number != 1 else '',
             repeat, format_time(best)))

    best = min(timings)
    worst = max(timings)
    if worst >= best * 4:
        import warnings
        warnings.warn_explicit("The test results are likely unreliable. "
                               "The worst time (%s) was more than four times "
                               "slower than the best time (%s)."
                               % (format_time(worst), format_time(best)),
                               UserWarning, '', 0)
