"""The failure analysis: what the parser got wrong, and why the figure made it easy to.

    tables.py   the parser's output tables, matched the way the metric matches
    run.py      one parser run: its markdown per page, and the official verdicts
    forms.py    which form each failure took, computed over every failure
    stats.py    pass rates by one variable at a time, with intervals
    cases.py    the sample the models are asked about, and the text each case becomes
    attribute.py  the one call per model: every case attributed, and its report

The program says what happened; the model says why. `passed` is always the official
value from the run's own evaluation report and is never re-judged.
"""
