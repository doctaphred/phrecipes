# Dr. Phred's Phamous Phrecipes™ 🐍👨‍🍳🥘🤢

_"Oh good, he named it after himself..."_

This repository is my personal collection of Python recipes: small units of code with few dependencies which I've repeatedly found useful throughout my career (interspersed with a few exploratory ideas which should probably never see the light of production<a id="text1" href="#note1"><sup>[1]</sup></a>).

These recipes are meant to be minimal and self-contained, and so they are not pip-installable: just copy/paste them into your project's utilities module.

All tests are currently implemented via [doctest]()<a id="text2" href="#note2"><sup>[2]</sup></a>: run them with `python3 -m doctest -o ELLIPSIS <paths>`; add `--verbose` to confirm which tests are run. (The `-o ELLIPSIS` option is required, to avoid repeating `# doctest: +ELLIPSIS` ad nauseam in the tests themselves.) Consider pytest's [doctest integration]() to include them in a production test suite.

[doctest]: https://docs.python.org/3/library/doctest.html
[doctest integration]: https://docs.pytest.org/en/stable/doctest.html

---

<a id="note1" href="#text1">[1]</a>: Distinguishing between the two is left as an exercise for the reader.

<a id="note2" href="#text2">[2]</a>: IMO the most underrated module in the Python standard library.
