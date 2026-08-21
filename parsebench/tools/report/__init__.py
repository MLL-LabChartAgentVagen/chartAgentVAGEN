"""Rendering the answers into the files the contract names.

    tables.py   one markdown table per row-definition in `format.REPORTS`
    pages.py    `reports/pages/<page>.md` -- three models on one page, side by side
    models.py   `reports/<model>.md` -- one model's two reports and its numbers
    compare.py  `reports/compare.md` -- every number, no conclusions
    build.py    writes all of them

The program is the only author of a number here. A model's prose is printed as
written, and the table beside it is computed.
"""
