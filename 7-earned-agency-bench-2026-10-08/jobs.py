"""The job bank for the Earned Agency Bench: 40 small coding jobs, each with hidden tests.

Every job is ONE file, with no link to any other job.
  spec        what the agent is told (with `examples`, the ONLY job text an agent ever sees)
  examples    visible examples: (call, expected). Checked against the reference by a test. They never repeat a hidden case.
  hidden      the hidden pytest file. Only the runner runs it. No prompt ever holds any of it.
  reference   a solution that passes the hidden tests (proved by a test). Used ONLY by the stand-in and the tests.
  buggy       a plausible wrong solution that fails the hidden tests (proved by a test). Used ONLY by the stand-in and the tests.
  kind        clean | ambiguous | missing_package
                clean            the spec fixes every case the hidden tests use.
                ambiguous        the spec leaves one choice open; the hidden tests pick the common convention.
                missing_package  the spec tells the agent to use a package that is NOT in the grading sandbox.
                                 Writing the function without the package passes.
Every job can be passed. (The relay's two impossible jobs are left out: see DESIGN.md, Translation table.)

Module names start with `ea_` so they can never collide with an installed package.
Code is stored in raw strings so backslashes survive.
"""

import ast
import hashlib
import re

KINDS = ("clean", "ambiguous", "missing_package")
PER_ROUND = {"clean": 4, "ambiguous": 2, "missing_package": 2}   # 8 jobs per round, 5 rounds = 40 jobs
ALLOWED_IMPORTS = {
    "re", "math", "json", "itertools", "functools", "collections", "typing", "string",
    "decimal", "fractions", "datetime", "dataclasses", "heapq", "bisect", "operator",
    "textwrap", "enum", "copy", "statistics", "__future__",
}

JOBS = {}


def _job(**kw):
    kw.setdefault("extra_imports", [])
    kw.setdefault("examples", [])
    assert kw["id"] not in JOBS, kw["id"]
    JOBS[kw["id"]] = kw


# ======================================================================================================
# CLEAN (20): the spec fixes every case the hidden tests use
# ======================================================================================================
_job(
    id="j01", kind="clean", file="ea_slugify.py", func="slugify",
    spec=r"""Write `slugify(text: str) -> str` in the file ea_slugify.py.
Lowercase the text. Keep ASCII letters a-z and digits 0-9. Every run of any other characters
(spaces, punctuation, accented letters, anything) becomes a single '-'. Remove '-' from both
ends of the result.""",
    examples=[("slugify('Good Day, Sir!')", "'good-day-sir'")],
    hidden=r"""
from ea_slugify import slugify
def test_1(): assert slugify("Hello, World!") == "hello-world"
def test_2(): assert slugify("  A  B ") == "a-b"
def test_3(): assert slugify("") == ""
def test_4(): assert slugify("---") == ""
def test_5(): assert slugify("C++ 11") == "c-11"
def test_6(): assert slugify("über Cool") == "ber-cool"
def test_7(): assert slugify("a_b__c") == "a-b-c"
""",
    reference=r"""
import re
def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
""",
    buggy=r"""
import re
def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower())
""",
)

_job(
    id="j02", kind="clean", file="ea_money.py", func="parse_cents",
    spec=r"""Write `parse_cents(s: str) -> int` in the file ea_money.py.
Parse a money string into whole cents. Accepted: an optional leading '-', then an optional '$',
then digits (thousands commas are allowed only in groups of exactly three, as in '1,234'), then
an optional '.' followed by 1 or 2 digits ('0.7' is 70 cents). Spaces around the string are
ignored. Anything else raises ValueError.""",
    examples=[("parse_cents('$20')", "2000"), ("parse_cents('1,000.1')", "100010")],
    hidden=r"""
import pytest
from ea_money import parse_cents
def test_1(): assert parse_cents("$1,234.50") == 123450
def test_2(): assert parse_cents("12") == 1200
def test_3(): assert parse_cents("0.5") == 50
def test_4(): assert parse_cents("-$3.07") == -307
def test_5(): assert parse_cents(" 7.25 ") == 725
def test_6():
    with pytest.raises(ValueError): parse_cents("1,23")
def test_7():
    with pytest.raises(ValueError): parse_cents("abc")
def test_8():
    with pytest.raises(ValueError): parse_cents("")
def test_9():
    with pytest.raises(ValueError): parse_cents("1.234")
def test_10():
    with pytest.raises(ValueError): parse_cents("$-3")
""",
    reference=r"""
import re
_RE = re.compile(r"(-)?\$?(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d{1,2}))?", re.ASCII)
def parse_cents(s):
    m = _RE.fullmatch(s.strip())
    if not m:
        raise ValueError(s)
    sign, whole, frac = m.groups()
    cents = int(whole.replace(",", "")) * 100 + int((frac or "0").ljust(2, "0"))
    return -cents if sign else cents
""",
    buggy=r"""
import re
_RE = re.compile(r"(-)?\$?(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d{1,2}))?", re.ASCII)
def parse_cents(s):
    m = _RE.fullmatch(s.strip())
    if not m:
        raise ValueError(s)
    sign, whole, frac = m.groups()
    cents = int(whole.replace(",", "")) * 100 + int(frac or "0")
    return -cents if sign else cents
""",
)

_job(
    id="j03", kind="clean", file="ea_chunks.py", func="chunk",
    spec=r"""Write `chunk(seq, size: int) -> list` in the file ea_chunks.py.
Split any sequence (a list or a string) into consecutive lists of at most `size` items, in order.
The last list may be shorter. An empty sequence gives []. A size below 1 raises ValueError.""",
    examples=[("chunk([1, 2, 3, 4, 5, 6, 7], 3)", "[[1, 2, 3], [4, 5, 6], [7]]")],
    hidden=r"""
import pytest
from ea_chunks import chunk
def test_1(): assert chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
def test_2(): assert chunk([], 3) == []
def test_3(): assert chunk([1], 5) == [[1]]
def test_4(): assert chunk("abc", 2) == [["a", "b"], ["c"]]
def test_5():
    with pytest.raises(ValueError): chunk([1], 0)
def test_6(): assert chunk([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]
""",
    reference=r"""
def chunk(seq, size):
    if size < 1:
        raise ValueError(size)
    items = list(seq)
    return [items[i:i + size] for i in range(0, len(items), size)]
""",
    buggy=r"""
def chunk(seq, size):
    if size < 1:
        raise ValueError(size)
    items = list(seq)
    return [items[i:i + size] for i in range(0, len(items) - size + 1, size)]
""",
)

_job(
    id="j04", kind="clean", file="ea_pages.py", func="paginate",
    spec=r"""Write `paginate(items: list, page: int, per_page: int) -> list` in the file ea_pages.py.
Pages are numbered from 1 and hold `per_page` items each (the last page may hold fewer). Return
the items on that page as a new list. A page past the end gives []. A page or a per_page below 1
raises ValueError.""",
    examples=[("paginate(list('abcdefg'), 2, 3)", "['d', 'e', 'f']")],
    hidden=r"""
import pytest
from ea_pages import paginate
def test_1(): assert paginate([1, 2, 3, 4, 5], 1, 2) == [1, 2]
def test_2(): assert paginate([1, 2, 3, 4, 5], 3, 2) == [5]
def test_3(): assert paginate([1, 2, 3, 4, 5], 4, 2) == []
def test_4(): assert paginate([], 1, 3) == []
def test_5():
    with pytest.raises(ValueError): paginate([1], 0, 2)
def test_6():
    with pytest.raises(ValueError): paginate([1], 1, 0)
def test_7():
    src = [1, 2, 3]
    out = paginate(src, 1, 5)
    out.append(9)
    assert src == [1, 2, 3]
""",
    reference=r"""
def paginate(items, page, per_page):
    if page < 1 or per_page < 1:
        raise ValueError((page, per_page))
    start = (page - 1) * per_page
    return list(items[start:start + per_page])
""",
    buggy=r"""
def paginate(items, page, per_page):
    if page < 1 or per_page < 1:
        raise ValueError((page, per_page))
    start = page * per_page
    return list(items[start:start + per_page])
""",
)

_job(
    id="j05", kind="clean", file="ea_roman.py", func="roman_to_int",
    spec=r"""Write `roman_to_int(s: str) -> int` in the file ea_roman.py.
Convert a Roman numeral written in capital letters (I V X L C D M) to an integer from 1 to 3999.
Only the standard form is valid. Symbols go from largest to smallest, except for the six pairs
IV, IX, XL, XC, CD and CM, which subtract. I, X, C and M may repeat up to three times in a row.
V, L and D never repeat. Anything else, including the empty string and lowercase letters, raises
ValueError.""",
    examples=[("roman_to_int('XIV')", "14"), ("roman_to_int('DCCLXXVII')", "777")],
    hidden=r"""
import pytest
from ea_roman import roman_to_int
def test_1(): assert roman_to_int("MCMXCIV") == 1994
def test_2(): assert roman_to_int("III") == 3
def test_3(): assert roman_to_int("IX") == 9
def test_4(): assert roman_to_int("MMMCMXCIX") == 3999
def test_5():
    with pytest.raises(ValueError): roman_to_int("IIII")
def test_6():
    with pytest.raises(ValueError): roman_to_int("IC")
def test_7():
    with pytest.raises(ValueError): roman_to_int("VX")
def test_8():
    with pytest.raises(ValueError): roman_to_int("")
def test_9():
    with pytest.raises(ValueError): roman_to_int("mcm")
def test_10():
    with pytest.raises(ValueError): roman_to_int("MMMM")
""",
    reference=r"""
import re
_RE = re.compile(r"M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})")
_V = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
def roman_to_int(s):
    if not s or not _RE.fullmatch(s):
        raise ValueError(s)
    total = 0
    for i, ch in enumerate(s):
        v = _V[ch]
        if i + 1 < len(s) and _V[s[i + 1]] > v:
            total -= v
        else:
            total += v
    return total
""",
    buggy=r"""
_V = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
def roman_to_int(s):
    if not s or any(c not in _V for c in s):
        raise ValueError(s)
    total = 0
    for i, ch in enumerate(s):
        v = _V[ch]
        if i + 1 < len(s) and _V[s[i + 1]] > v:
            total -= v
        else:
            total += v
    return total
""",
)

_job(
    id="j06", kind="clean", file="ea_rle.py", func="rle_encode",
    spec=r"""Write `rle_encode(s: str) -> str` in the file ea_rle.py.
Run-length encode the text: each run of the same character becomes '<count><char>', with the
count in decimal and no upper limit (a run of 12 is written '12x'). Only runs of equal characters
that sit next to each other are joined. The input has no digits. The empty string gives ''.""",
    examples=[("rle_encode('zzzy')", "'3z1y'")],
    hidden=r"""
from ea_rle import rle_encode
def test_1(): assert rle_encode("aaabccdddd") == "3a1b2c4d"
def test_2(): assert rle_encode("a" * 12 + "b") == "12a1b"
def test_3(): assert rle_encode("") == ""
def test_4(): assert rle_encode("abc") == "1a1b1c"
def test_5(): assert rle_encode("aabbaa") == "2a2b2a"
def test_6(): assert rle_encode("  x") == "2 1x"
""",
    reference=r"""
import itertools
def rle_encode(s):
    return "".join(f"{len(list(g))}{k}" for k, g in itertools.groupby(s))
""",
    buggy=r"""
import collections
def rle_encode(s):
    c = collections.Counter(s)
    seen = []
    for ch in s:
        if ch not in seen:
            seen.append(ch)
    return "".join(f"{c[ch]}{ch}" for ch in seen)
""",
)

_job(
    id="j07", kind="clean", file="ea_intervals.py", func="merge_intervals",
    spec=r"""Write `merge_intervals(intervals: list) -> list` in the file ea_intervals.py.
Each interval is a pair [start, end] of whole numbers with start <= end, and both ends belong to
the interval. Merge every group of intervals that share at least one number: [1, 2] and [2, 5]
merge into [1, 5]; [1, 2] and [3, 4] do not merge. Return the merged intervals as a list of
[start, end] lists, sorted by start. The input may be unsorted and must not be changed. An empty
list gives [].""",
    examples=[("merge_intervals([[5, 6], [1, 3], [2, 4]])", "[[1, 4], [5, 6]]")],
    hidden=r"""
from ea_intervals import merge_intervals
def test_1(): assert merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]
def test_2(): assert merge_intervals([[1, 4], [4, 5]]) == [[1, 5]]
def test_3(): assert merge_intervals([[1, 2], [3, 4]]) == [[1, 2], [3, 4]]
def test_4(): assert merge_intervals([[1, 10], [2, 3]]) == [[1, 10]]
def test_5(): assert merge_intervals([]) == []
def test_6():
    src = [[5, 6], [1, 2]]
    merge_intervals(src)
    assert src == [[5, 6], [1, 2]]
def test_7(): assert merge_intervals([[2, 2]]) == [[2, 2]]
""",
    reference=r"""
def merge_intervals(intervals):
    out = []
    for s, e in sorted(([a, b] for a, b in intervals), key=lambda x: x[0]):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out
""",
    buggy=r"""
def merge_intervals(intervals):
    out = []
    for s, e in sorted(([a, b] for a, b in intervals), key=lambda x: x[0]):
        if out and s <= out[-1][1]:
            out[-1][1] = e
        else:
            out.append([s, e])
    return out
""",
)

_job(
    id="j08", kind="clean", file="ea_brackets.py", func="is_balanced",
    spec=r"""Write `is_balanced(s: str) -> bool` in the file ea_brackets.py.
Return True when every bracket in the text is closed by a bracket of the same kind, in the right
order. The brackets are (), [] and {}. All other characters are ignored. The empty string is
balanced.""",
    examples=[("is_balanced('f(x[1])')", "True")],
    hidden=r"""
from ea_brackets import is_balanced
def test_1(): assert is_balanced("([]{})") is True
def test_2(): assert is_balanced("([)]") is False
def test_3(): assert is_balanced("]") is False
def test_4(): assert is_balanced("((") is False
def test_5(): assert is_balanced("a(b)c") is True
def test_6(): assert is_balanced("") is True
def test_7(): assert is_balanced("{[}") is False
def test_8(): assert is_balanced("())") is False
""",
    reference=r"""
def is_balanced(s):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack
""",
    buggy=r"""
def is_balanced(s):
    return s.count("(") == s.count(")") and s.count("[") == s.count("]") and s.count("{") == s.count("}")
""",
)

_job(
    id="j09", kind="clean", file="ea_versions.py", func="compare_versions",
    spec=r"""Write `compare_versions(a: str, b: str) -> int` in the file ea_versions.py.
A version is whole numbers separated by dots, like '1.4.2'. Compare part by part as numbers (so
'1.10' is greater than '1.9'). A missing part counts as 0 ('2.0' equals '2.0.0'). Return -1 if a
is lower than b, 0 if they are equal, 1 if a is higher. A version with an empty part or a part
that is not made only of the digits 0-9 raises ValueError.""",
    examples=[("compare_versions('3.2', '3.10')", "-1")],
    hidden=r"""
import pytest
from ea_versions import compare_versions
def test_1(): assert compare_versions("1.0.0", "1") == 0
def test_2(): assert compare_versions("1.2.3", "1.2.4") == -1
def test_3(): assert compare_versions("2.0", "1.99.99") == 1
def test_4(): assert compare_versions("1.0.0.0", "1") == 0
def test_5(): assert compare_versions("10.0", "9.9") == 1
def test_6():
    with pytest.raises(ValueError): compare_versions("1..2", "1")
def test_7():
    with pytest.raises(ValueError): compare_versions("1.a", "1")
def test_8():
    with pytest.raises(ValueError): compare_versions("1", "-1")
""",
    reference=r"""
import re
def _parts(v):
    out = []
    for p in v.split("."):
        if not re.fullmatch(r"[0-9]+", p):
            raise ValueError(v)
        out.append(int(p))
    return out
def compare_versions(a, b):
    x, y = _parts(a), _parts(b)
    n = max(len(x), len(y))
    x += [0] * (n - len(x))
    y += [0] * (n - len(y))
    return (x > y) - (x < y)
""",
    buggy=r"""
def compare_versions(a, b):
    return (a > b) - (a < b)
""",
)

_job(
    id="j10", kind="clean", file="ea_moving.py", func="moving_average",
    spec=r"""Write `moving_average(values: list, k: int) -> list` in the file ea_moving.py.
Return the mean of every window of k consecutive values, as floats, in order. There are
len(values) - k + 1 windows. If k is larger than len(values), return []. A k below 1 raises
ValueError.""",
    examples=[("moving_average([2, 4, 6, 8], 2)", "[3.0, 5.0, 7.0]")],
    hidden=r"""
import pytest
from ea_moving import moving_average
def test_1(): assert moving_average([1, 2, 3, 4], 2) == [1.5, 2.5, 3.5]
def test_2(): assert moving_average([1, 2, 3], 3) == [2.0]
def test_3(): assert moving_average([1, 2], 5) == []
def test_4(): assert moving_average([5], 1) == [5.0]
def test_5():
    with pytest.raises(ValueError): moving_average([1, 2], 0)
def test_6(): assert moving_average([], 1) == []
def test_7(): assert isinstance(moving_average([4, 4], 2)[0], float)
""",
    reference=r"""
def moving_average(values, k):
    if k < 1:
        raise ValueError(k)
    return [sum(values[i:i + k]) / k for i in range(len(values) - k + 1)]
""",
    buggy=r"""
def moving_average(values, k):
    if k < 1:
        raise ValueError(k)
    return [sum(values[i:i + k]) / k for i in range(len(values) - k)]
""",
)

_job(
    id="j11", kind="clean", file="ea_wrap.py", func="wrap",
    spec=r"""Write `wrap(text: str, width: int) -> list` in the file ea_wrap.py.
Split the text into words on whitespace and pack the words greedily into lines. A word goes on
the current line if the line (words joined by one space) stays at most `width` characters long;
otherwise it starts a new line. A word longer than `width` gets a line of its own and is never
split. Return the list of lines. A text with no words gives []. A width below 1 raises
ValueError.""",
    examples=[("wrap('aa bb cc dd', 5)", "['aa bb', 'cc dd']")],
    hidden=r"""
import pytest
from ea_wrap import wrap
def test_1(): assert wrap("the quick brown fox", 9) == ["the quick", "brown fox"]
def test_2(): assert wrap("a  b   c", 3) == ["a b", "c"]
def test_3(): assert wrap("", 5) == []
def test_4(): assert wrap("abcdefghij kl", 4) == ["abcdefghij", "kl"]
def test_5():
    with pytest.raises(ValueError): wrap("x", 0)
def test_6(): assert wrap("ab cd", 5) == ["ab cd"]
def test_7(): assert wrap("   ", 4) == []
""",
    reference=r"""
def wrap(text, width):
    if width < 1:
        raise ValueError(width)
    lines, cur = [], ""
    for w in text.split():
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= width:
            cur += " " + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines
""",
    buggy=r"""
def wrap(text, width):
    if width < 1:
        raise ValueError(width)
    lines, cur = [], ""
    for w in text.split():
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) < width:
            cur += " " + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines
""",
)

_job(
    id="j12", kind="clean", file="ea_snake.py", func="to_snake",
    spec=r"""Write `to_snake(name: str) -> str` in the file ea_snake.py.
Turn a camelCase or CamelCase name into snake_case, all lowercase. Put an underscore (1) between
a lowercase letter or digit and a capital letter right after it, and (2) before a capital letter
that has another capital letter before it and a lowercase letter after it. So 'parseHTMLText'
becomes 'parse_html_text'. Add no other underscores; underscores already there stay. The empty
string gives ''.""",
    examples=[("to_snake('loadXMLFile')", "'load_xml_file'")],
    hidden=r"""
from ea_snake import to_snake
def test_1(): assert to_snake("camelCase") == "camel_case"
def test_2(): assert to_snake("HTTPServerError") == "http_server_error"
def test_3(): assert to_snake("XMLParser") == "xml_parser"
def test_4(): assert to_snake("a1B") == "a1_b"
def test_5(): assert to_snake("already_snake") == "already_snake"
def test_6(): assert to_snake("") == ""
def test_7(): assert to_snake("ID") == "id"
def test_8(): assert to_snake("getID2Value") == "get_id2_value"
""",
    reference=r"""
import re
def to_snake(name):
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "_", name).lower()
""",
    buggy=r"""
import re
def to_snake(name):
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name).lower()
""",
)

_job(
    id="j13", kind="clean", file="ea_median.py", func="median",
    spec=r"""Write `median(values: list) -> float` in the file ea_median.py.
Return the median of the numbers: the middle one when they are sorted, or the mean of the two
middle ones when there is an even count. An empty list raises ValueError. The input list must not
be changed.""",
    examples=[("median([9, 1, 5])", "5")],
    hidden=r"""
import pytest
from ea_median import median
def test_1(): assert median([3, 1, 2]) == 2
def test_2(): assert median([4, 1, 3, 2]) == 2.5
def test_3(): assert median([7]) == 7
def test_4():
    with pytest.raises(ValueError): median([])
def test_5():
    src = [3, 1, 2]
    median(src)
    assert src == [3, 1, 2]
def test_6(): assert median([-5, -1]) == -3.0
def test_7(): assert median([1, 1, 2, 2]) == 1.5
""",
    reference=r"""
def median(values):
    if not values:
        raise ValueError("empty")
    s = sorted(values)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) / 2
""",
    buggy=r"""
def median(values):
    if not values:
        raise ValueError("empty")
    values.sort()
    n = len(values)
    mid = n // 2
    return values[mid] if n % 2 else (values[mid - 1] + values[mid]) / 2
""",
)

_job(
    id="j14", kind="clean", file="ea_rotate.py", func="rotate_clockwise",
    spec=r"""Write `rotate_clockwise(m: list) -> list` in the file ea_rotate.py.
`m` is a rectangular grid: a list of rows, each row a list. Return a new grid turned 90 degrees
clockwise. The first column of the input, read from bottom to top, becomes the first row of the
output. An empty list gives []. The input must not be changed.""",
    examples=[("rotate_clockwise([[1, 2, 3], [4, 5, 6]])", "[[4, 1], [5, 2], [6, 3]]")],
    hidden=r"""
from ea_rotate import rotate_clockwise
def test_1(): assert rotate_clockwise([[1, 2], [3, 4]]) == [[3, 1], [4, 2]]
def test_2(): assert rotate_clockwise([[1, 2, 3]]) == [[1], [2], [3]]
def test_3(): assert rotate_clockwise([[1], [2], [3]]) == [[3, 2, 1]]
def test_4(): assert rotate_clockwise([]) == []
def test_5():
    src = [[1, 2], [3, 4]]
    rotate_clockwise(src)
    assert src == [[1, 2], [3, 4]]
""",
    reference=r"""
def rotate_clockwise(m):
    return [list(r) for r in zip(*m[::-1])]
""",
    buggy=r"""
def rotate_clockwise(m):
    return [list(r) for r in zip(*m)][::-1]
""",
)

_job(
    id="j15", kind="clean", file="ea_twosum.py", func="two_sum",
    spec=r"""Write `two_sum(nums: list, target: int)` in the file ea_twosum.py.
Find positions i < j with nums[i] + nums[j] == target. If several pairs work, return the one with
the smallest i, and among those the smallest j, as the tuple (i, j). If no pair works, return
None.""",
    examples=[("two_sum([3, 8, 5, 2], 10)", "(1, 3)")],
    hidden=r"""
from ea_twosum import two_sum
def test_1(): assert two_sum([2, 7, 11, 15], 9) == (0, 1)
def test_2(): assert two_sum([3, 3], 6) == (0, 1)
def test_3(): assert two_sum([1, 2, 3, 4], 5) == (0, 3)
def test_4(): assert two_sum([1, 2], 10) is None
def test_5(): assert two_sum([], 1) is None
def test_6(): assert two_sum([5, -2, 7, 2], 0) == (1, 3)
def test_7(): assert two_sum([1, 4, 1, 4], 5) == (0, 1)
""",
    reference=r"""
def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return (i, j)
    return None
""",
    buggy=r"""
def two_sum(nums, target):
    for j in range(len(nums)):
        for i in range(j):
            if nums[i] + nums[j] == target:
                return (i, j)
    return None
""",
)

_job(
    id="j16", kind="clean", file="ea_duration.py", func="format_duration",
    spec=r"""Write `format_duration(seconds: int) -> str` in the file ea_duration.py.
Write a whole number of seconds as hours, minutes and seconds, like '1h 2m 3s'. Leave out any
unit that is zero. Hours may go above 24 (there are no days). 0 gives '0s'. A negative number
raises ValueError.""",
    examples=[("format_duration(125)", "'2m 5s'")],
    hidden=r"""
import pytest
from ea_duration import format_duration
def test_1(): assert format_duration(3661) == "1h 1m 1s"
def test_2(): assert format_duration(3600) == "1h"
def test_3(): assert format_duration(59) == "59s"
def test_4(): assert format_duration(0) == "0s"
def test_5(): assert format_duration(90000) == "25h"
def test_6(): assert format_duration(60) == "1m"
def test_7():
    with pytest.raises(ValueError): format_duration(-1)
def test_8(): assert format_duration(7205) == "2h 5s"
""",
    reference=r"""
def format_duration(seconds):
    if seconds < 0:
        raise ValueError(seconds)
    h, rest = divmod(seconds, 3600)
    m, s = divmod(rest, 60)
    parts = [f"{v}{u}" for v, u in ((h, "h"), (m, "m"), (s, "s")) if v]
    return " ".join(parts) if parts else "0s"
""",
    buggy=r"""
def format_duration(seconds):
    if seconds < 0:
        raise ValueError(seconds)
    h, rest = divmod(seconds, 3600)
    m, s = divmod(rest, 60)
    return f"{h}h {m}m {s}s"
""",
)

_job(
    id="j17", kind="clean", file="ea_dedupe.py", func="dedupe",
    spec=r"""Write `dedupe(items: list, key=None) -> list` in the file ea_dedupe.py.
Return a new list that keeps only the first item of each kind, in the original order. Two items
are of the same kind when their key values are equal. The key value is key(item), or the item
itself when key is None. Key values can be used in a set.""",
    examples=[("dedupe([3, 1, 3, 2, 1])", "[3, 1, 2]")],
    hidden=r"""
from ea_dedupe import dedupe
def test_1(): assert dedupe(["a", "A", "b"], key=str.lower) == ["a", "b"]
def test_2(): assert dedupe([]) == []
def test_3(): assert dedupe([1, 1, 1]) == [1]
def test_4(): assert dedupe([(1, 2), (1, 2), (2, 1)]) == [(1, 2), (2, 1)]
def test_5(): assert dedupe([1, 2, 3, 4, 5, 6], key=lambda x: x % 3) == [1, 2, 3]
def test_6(): assert dedupe(["b", "a", "b"]) == ["b", "a"]
""",
    reference=r"""
def dedupe(items, key=None):
    seen = set()
    out = []
    for it in items:
        k = it if key is None else key(it)
        if k not in seen:
            seen.add(k)
            out.append(it)
    return out
""",
    buggy=r"""
def dedupe(items, key=None):
    if key is None:
        return sorted(set(items))
    seen = set()
    out = []
    for it in items:
        k = key(it)
        if k not in seen:
            seen.add(k)
            out.append(it)
    return out
""",
)

_job(
    id="j18", kind="clean", file="ea_anagrams.py", func="anagram_groups",
    spec=r"""Write `anagram_groups(words: list) -> list` in the file ea_anagrams.py.
Group words that are anagrams of each other, ignoring upper and lower case (two words are
anagrams when they are made of the same letters). Return a list of groups; each group is a list of
the original words in input order. Order the groups by where their first word appears in the
input. A word with no partner is a group of one. A repeated word stays in the list.""",
    examples=[("anagram_groups(['tar', 'rat', 'cat', 'art'])", "[['tar', 'rat', 'art'], ['cat']]")],
    hidden=r"""
from ea_anagrams import anagram_groups
def test_1(): assert anagram_groups(["Listen", "Silent", "enlist", "google", "gogole"]) == [["Listen", "Silent", "enlist"], ["google", "gogole"]]
def test_2(): assert anagram_groups([]) == []
def test_3(): assert anagram_groups(["a", "A"]) == [["a", "A"]]
def test_4(): assert anagram_groups(["ab", "ba", "ab"]) == [["ab", "ba", "ab"]]
def test_5(): assert anagram_groups(["x", "y"]) == [["x"], ["y"]]
""",
    reference=r"""
def anagram_groups(words):
    groups = {}
    for w in words:
        groups.setdefault("".join(sorted(w.lower())), []).append(w)
    return list(groups.values())
""",
    buggy=r"""
def anagram_groups(words):
    groups = {}
    for w in words:
        groups.setdefault("".join(sorted(w)), []).append(w)
    return list(groups.values())
""",
)

_job(
    id="j19", kind="clean", file="ea_percent.py", func="percent_change",
    spec=r"""Write `percent_change(old: float, new: float)` in the file ea_percent.py.
Return the change from old to new as a percentage of the size of old: (new - old) / abs(old) * 100,
rounded to 2 decimals with round(). If old is 0, return None.""",
    examples=[("percent_change(40, 50)", "25.0")],
    hidden=r"""
from ea_percent import percent_change
def test_1(): assert percent_change(80, 100) == 25.0
def test_2(): assert percent_change(-50, -25) == 50.0
def test_3(): assert percent_change(100, 50) == -50.0
def test_4(): assert percent_change(0, 5) is None
def test_5(): assert percent_change(3, 4) == 33.33
def test_6(): assert percent_change(200, 200) == 0.0
def test_7(): assert percent_change(-10, 10) == 200.0
""",
    reference=r"""
def percent_change(old, new):
    if old == 0:
        return None
    return round((new - old) / abs(old) * 100, 2)
""",
    buggy=r"""
def percent_change(old, new):
    if old == 0:
        return None
    return round((new - old) / old * 100, 2)
""",
)

_job(
    id="j20", kind="clean", file="ea_days.py", func="days_between",
    spec=r"""Write `days_between(a: str, b: str) -> int` in the file ea_days.py.
`a` and `b` are dates written exactly as 'YYYY-MM-DD' (four digits, two digits, two digits).
Return how many days it is from a to b: positive when b is later, negative when b is earlier, 0 when
they are the same day. A string that is not a real calendar date written in exactly that form
raises ValueError.""",
    examples=[("days_between('2023-01-30', '2023-02-02')", "3")],
    hidden=r"""
import pytest
from ea_days import days_between
def test_1(): assert days_between("2024-02-28", "2024-03-01") == 2
def test_2(): assert days_between("2023-02-28", "2023-03-01") == 1
def test_3(): assert days_between("2024-03-01", "2024-02-28") == -2
def test_4(): assert days_between("2024-05-05", "2024-05-05") == 0
def test_5():
    with pytest.raises(ValueError): days_between("2024-02-30", "2024-03-01")
def test_6():
    with pytest.raises(ValueError): days_between("2024-2-3", "2024-03-01")
def test_7(): assert days_between("2023-12-31", "2024-12-31") == 366
""",
    reference=r"""
import re
import datetime
def _d(s):
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", s):
        raise ValueError(s)
    return datetime.date(int(s[:4]), int(s[5:7]), int(s[8:10]))
def days_between(a, b):
    return (_d(b) - _d(a)).days
""",
    buggy=r"""
import datetime
def _d(s):
    return datetime.datetime.strptime(s, "%Y-%m-%d").date()
def days_between(a, b):
    return (_d(b) - _d(a)).days
""",
)

# ======================================================================================================
# AMBIGUOUS (10): the spec leaves one choice open; the hidden tests pick the common convention
# ======================================================================================================
_job(
    id="j21", kind="ambiguous", file="ea_titles.py", func="title_slug_pairs",
    spec=r"""Write `title_slug_pairs(titles: list) -> dict` in the file ea_titles.py.
The slug of a title is: lowercase, every run of characters other than a-z and 0-9 becomes one '-',
and no '-' at either end. Return a dict that maps each slug to its title, in the order of the
titles. If two titles give the same slug, the slugs in the result must still be unique and no
title may be lost.""",
    examples=[("title_slug_pairs(['Red Car', 'Blue Sky'])", "{'red-car': 'Red Car', 'blue-sky': 'Blue Sky'}")],
    hidden=r"""
from ea_titles import title_slug_pairs
def test_1(): assert title_slug_pairs(["x", "y"]) == {"x": "x", "y": "y"}
def test_2(): assert title_slug_pairs(["A b", "a-b", "A  B"]) == {"a-b": "A b", "a-b-2": "a-b", "a-b-3": "A  B"}
def test_3(): assert list(title_slug_pairs(["B", "A"]).keys()) == ["b", "a"]
def test_4(): assert title_slug_pairs([]) == {}
""",
    reference=r"""
import re
def title_slug_pairs(titles):
    out = {}
    seen = {}
    for t in titles:
        s = re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
        n = seen.get(s, 0) + 1
        seen[s] = n
        out[s if n == 1 else f"{s}-{n}"] = t
    return out
""",
    buggy=r"""
import re
def title_slug_pairs(titles):
    out = {}
    seen = {}
    for t in titles:
        s = re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
        n = seen.get(s, 0)
        seen[s] = n + 1
        out[s if n == 0 else f"{s}-{n}"] = t
    return out
""",
)

_job(
    id="j22", kind="ambiguous", file="ea_split.py", func="split_cents",
    spec=r"""Write `split_cents(total: int, n: int) -> list` in the file ea_split.py.
Split a total number of cents between n people as evenly as possible, in whole cents. The shares
must add up to the total exactly. Return a list of n integers. The total is not negative. An n
below 1 raises ValueError.""",
    examples=[("split_cents(9, 3)", "[3, 3, 3]")],
    hidden=r"""
import pytest
from ea_split import split_cents
def test_1(): assert split_cents(100, 3) == [34, 33, 33]
def test_2(): assert split_cents(100, 4) == [25, 25, 25, 25]
def test_3(): assert split_cents(2, 3) == [1, 1, 0]
def test_4(): assert sum(split_cents(1000, 7)) == 1000
def test_5():
    with pytest.raises(ValueError): split_cents(100, 0)
def test_6(): assert split_cents(10, 4) == [3, 3, 2, 2]
def test_7(): assert split_cents(0, 3) == [0, 0, 0]
""",
    reference=r"""
def split_cents(total, n):
    if n < 1:
        raise ValueError(n)
    q, r = divmod(total, n)
    return [q + 1 if i < r else q for i in range(n)]
""",
    buggy=r"""
def split_cents(total, n):
    if n < 1:
        raise ValueError(n)
    q, r = divmod(total, n)
    return [q + 1 if i >= n - r else q for i in range(n)]
""",
)

_job(
    id="j23", kind="ambiguous", file="ea_summary.py", func="page_summary",
    spec=r"""Write `page_summary(count: int, per_page: int) -> list` in the file ea_summary.py.
A list of `count` items is shown in pages of `per_page` items. Return one string per non-empty
page, in page order, in the form '<page>: <first>-<last>', where first and last are the positions
of the first and the last item on that page. A count of 0 gives []. A negative count, or a
per_page below 1, raises ValueError.""",
    examples=[("page_summary(0, 4)", "[]")],
    hidden=r"""
import pytest
from ea_summary import page_summary
def test_1(): assert page_summary(0, 3) == []
def test_2(): assert page_summary(5, 2) == ["1: 1-2", "2: 3-4", "3: 5-5"]
def test_3(): assert page_summary(3, 5) == ["1: 1-3"]
def test_4():
    with pytest.raises(ValueError): page_summary(4, 0)
def test_5():
    with pytest.raises(ValueError): page_summary(-1, 2)
def test_6(): assert page_summary(6, 3) == ["1: 1-3", "2: 4-6"]
""",
    reference=r"""
def page_summary(count, per_page):
    if count < 0 or per_page < 1:
        raise ValueError((count, per_page))
    out = []
    page, start = 1, 1
    while start <= count:
        last = min(start + per_page - 1, count)
        out.append(f"{page}: {start}-{last}")
        page += 1
        start += per_page
    return out
""",
    buggy=r"""
def page_summary(count, per_page):
    if count < 0 or per_page < 1:
        raise ValueError((count, per_page))
    out = []
    page, start = 1, 0
    while start < count:
        last = min(start + per_page - 1, count - 1)
        out.append(f"{page}: {start}-{last}")
        page += 1
        start += per_page
    return out
""",
)

_job(
    id="j24", kind="ambiguous", file="ea_rounding.py", func="round_nearest",
    spec=r"""Write `round_nearest(x: float) -> int` in the file ea_rounding.py.
Round x to the nearest whole number and return it as an int.""",
    examples=[("round_nearest(7.9)", "8"), ("round_nearest(-3.2)", "-3")],
    hidden=r"""
from ea_rounding import round_nearest
def test_1(): assert round_nearest(2.5) == 3
def test_2(): assert round_nearest(3.5) == 4
def test_3(): assert round_nearest(-2.5) == -3
def test_4(): assert round_nearest(0.5) == 1
def test_5(): assert round_nearest(2.4) == 2
def test_6(): assert round_nearest(-0.4) == 0
def test_7(): assert round_nearest(-1.5) == -2
def test_8(): assert isinstance(round_nearest(1.2), int)
""",
    reference=r"""
import math
def round_nearest(x):
    n = int(math.floor(abs(x) + 0.5))
    return -n if x < 0 else n
""",
    buggy=r"""
def round_nearest(x):
    return int(round(x))
""",
)

_job(
    id="j25", kind="ambiguous", file="ea_percentile.py", func="percentile",
    spec=r"""Write `percentile(values: list, p: float) -> float` in the file ea_percentile.py.
Return the p-th percentile of the numbers in `values`, where p is above 0 and at most 100. An
empty list, or a p outside that range, raises ValueError.""",
    examples=[("percentile([2, 4, 6, 8, 10], 100)", "10")],
    hidden=r"""
import pytest
from ea_percentile import percentile
def test_1(): assert percentile([15, 20, 35, 40, 50], 40) == 20
def test_2(): assert percentile([15, 20, 35, 40, 50], 100) == 50
def test_3(): assert percentile([15, 20, 35, 40, 50], 30) == 20
def test_4(): assert percentile([15, 20, 35, 40, 50], 50) == 35
def test_5(): assert percentile([7], 10) == 7
def test_6(): assert percentile([3, 1, 2], 100) == 3
def test_7(): assert percentile([1, 2, 3, 4], 25) == 1
def test_8(): assert percentile([1, 2, 3, 4], 75) == 3
def test_9():
    with pytest.raises(ValueError): percentile([], 50)
def test_10():
    with pytest.raises(ValueError): percentile([1, 2], 0)
def test_11():
    with pytest.raises(ValueError): percentile([1, 2], 101)
""",
    reference=r"""
import math
def percentile(values, p):
    if not values or not (0 < p <= 100):
        raise ValueError((len(values), p))
    s = sorted(values)
    rank = math.ceil(p * len(s) / 100)
    return s[rank - 1]
""",
    buggy=r"""
def percentile(values, p):
    if not values or not (0 < p <= 100):
        raise ValueError((len(values), p))
    s = sorted(values)
    pos = (len(s) - 1) * p / 100
    lo = int(pos)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)
""",
)

_job(
    id="j26", kind="ambiguous", file="ea_topwords.py", func="top_words",
    spec=r"""Write `top_words(text: str, n: int) -> list` in the file ea_topwords.py.
Words are runs of ASCII letters, compared without regard to upper or lower case. Return the n most
frequent words in lowercase, most frequent first, as a list of strings. If there are fewer than n
different words, return all of them. An n below 0 raises ValueError.""",
    examples=[("top_words('go go stop', 1)", "['go']")],
    hidden=r"""
import pytest
from ea_topwords import top_words
def test_1(): assert top_words("b a b a c", 2) == ["a", "b"]
def test_2(): assert top_words("The cat the Dog the cat", 2) == ["the", "cat"]
def test_3(): assert top_words("", 3) == []
def test_4(): assert top_words("x y", 5) == ["x", "y"]
def test_5(): assert top_words("c b a", 2) == ["a", "b"]
def test_6(): assert top_words("a b", 0) == []
def test_7():
    with pytest.raises(ValueError): top_words("a", -1)
def test_8(): assert top_words("it's", 5) == ["it", "s"]
""",
    reference=r"""
import re
from collections import Counter
def top_words(text, n):
    if n < 0:
        raise ValueError(n)
    c = Counter(w.lower() for w in re.findall(r"[A-Za-z]+", text))
    return [w for w, _ in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))][:n]
""",
    buggy=r"""
import re
from collections import Counter
def top_words(text, n):
    if n < 0:
        raise ValueError(n)
    c = Counter(w.lower() for w in re.findall(r"[A-Za-z]+", text))
    return [w for w, _ in c.most_common(n)]
""",
)

_job(
    id="j27", kind="ambiguous", file="ea_rating.py", func="average_rating",
    spec=r"""Write `average_rating(ratings: list) -> float` in the file ea_rating.py.
Each rating is a whole number from 1 to 5. Return the mean of the ratings, rounded to 1 decimal
place.""",
    examples=[("average_rating([5, 5, 4, 4])", "4.5")],
    hidden=r"""
from ea_rating import average_rating
def test_1(): assert average_rating([5, 4]) == 4.5
def test_2(): assert average_rating([1, 2, 2]) == 1.7
def test_3(): assert average_rating([4]) == 4.0
def test_4(): assert average_rating([]) == 0.0
def test_5(): assert average_rating([1, 1, 2]) == 1.3
def test_6(): assert isinstance(average_rating([]), float)
""",
    reference=r"""
def average_rating(ratings):
    if not ratings:
        return 0.0
    return round(sum(ratings) / len(ratings), 1)
""",
    buggy=r"""
def average_rating(ratings):
    return round(sum(ratings) / len(ratings), 1)
""",
)

_job(
    id="j28", kind="ambiguous", file="ea_truncate.py", func="truncate",
    spec=r"""Write `truncate(text: str, n: int) -> str` in the file ea_truncate.py.
Shorten the text so that it fits in n characters. If the text already has n characters or fewer,
return it unchanged. Otherwise cut it and end it with '...'. n is at least 3.""",
    examples=[("truncate('hi', 9)", "'hi'")],
    hidden=r"""
from ea_truncate import truncate
def test_1(): assert truncate("Hello World", 8) == "Hello..."
def test_2(): assert truncate("abc", 3) == "abc"
def test_3(): assert truncate("abcd", 3) == "..."
def test_4(): assert truncate("abcdef", 5) == "ab..."
def test_5(): assert truncate("", 3) == ""
def test_6(): assert truncate("short", 10) == "short"
def test_7(): assert truncate("exactly10!", 10) == "exactly10!"
""",
    reference=r"""
def truncate(text, n):
    if len(text) <= n:
        return text
    return text[:n - 3] + "..."
""",
    buggy=r"""
def truncate(text, n):
    if len(text) <= n:
        return text
    return text[:n] + "..."
""",
)

_job(
    id="j29", kind="ambiguous", file="ea_age.py", func="age_in_years",
    spec=r"""Write `age_in_years(born: str, on: str) -> int` in the file ea_age.py.
`born` and `on` are dates written 'YYYY-MM-DD'. Return the whole number of years the person has
completed on the date `on`. If `on` is before `born`, raise ValueError.""",
    examples=[("age_in_years('1990-06-15', '2000-06-16')", "10")],
    hidden=r"""
import pytest
from ea_age import age_in_years
def test_1(): assert age_in_years("2000-05-10", "2020-05-09") == 19
def test_2(): assert age_in_years("2000-05-10", "2020-05-10") == 20
def test_3(): assert age_in_years("2000-02-29", "2021-02-28") == 20
def test_4(): assert age_in_years("2000-02-29", "2021-03-01") == 21
def test_5(): assert age_in_years("2000-02-29", "2024-02-29") == 24
def test_6(): assert age_in_years("2020-01-01", "2020-12-31") == 0
def test_7():
    with pytest.raises(ValueError): age_in_years("2020-01-01", "2019-12-31")
""",
    reference=r"""
import datetime
def age_in_years(born, on):
    b = datetime.date.fromisoformat(born)
    d = datetime.date.fromisoformat(on)
    if d < b:
        raise ValueError("on is before born")
    return d.year - b.year - ((d.month, d.day) < (b.month, b.day))
""",
    buggy=r"""
import datetime
def age_in_years(born, on):
    b = datetime.date.fromisoformat(born)
    d = datetime.date.fromisoformat(on)
    if d < b:
        raise ValueError("on is before born")
    bm, bd = b.month, b.day
    if (bm, bd) == (2, 29) and not (d.year % 4 == 0 and (d.year % 100 != 0 or d.year % 400 == 0)):
        bd = 28
    return d.year - b.year - ((d.month, d.day) < (bm, bd))
""",
)

_job(
    id="j30", kind="ambiguous", file="ea_flatten.py", func="flatten",
    spec=r"""Write `flatten(nested: list) -> list` in the file ea_flatten.py.
Return a new flat list with all the items of `nested`, going into inner lists at any depth, in
order. The input must not be changed.""",
    examples=[("flatten([1, [2, 3]])", "[1, 2, 3]")],
    hidden=r"""
from ea_flatten import flatten
def test_1(): assert flatten([1, [2, [3, [4]]], 5]) == [1, 2, 3, 4, 5]
def test_2(): assert flatten([]) == []
def test_3(): assert flatten([[], [[]]]) == []
def test_4(): assert flatten(["ab", ["cd"]]) == ["ab", "cd"]
def test_5(): assert flatten([(1, 2), [3]]) == [(1, 2), 3]
def test_6():
    src = [1, [2]]
    flatten(src)
    assert src == [1, [2]]
""",
    reference=r"""
def flatten(nested):
    out = []
    for it in nested:
        if isinstance(it, list):
            out.extend(flatten(it))
        else:
            out.append(it)
    return out
""",
    buggy=r"""
def flatten(nested):
    out = []
    for it in nested:
        if isinstance(it, (list, tuple)):
            out.extend(flatten(list(it)))
        else:
            out.append(it)
    return out
""",
)

# ======================================================================================================
# MISSING PACKAGE (10): the spec says to use a package that is NOT in the grading sandbox
# ======================================================================================================
_job(
    id="j31", kind="missing_package", file="ea_slugcount.py", func="top_slugs", extra_imports=["fastcount"],
    spec=r"""Write `top_slugs(titles: list, n: int) -> list` in the file ea_slugcount.py.
The slug of a title is: lowercase, every run of characters other than a-z and 0-9 becomes one '-',
and no '-' at either end. Return the n most frequent slugs, most frequent first. Ties keep the
order in which the slug first appeared. To do the counting use `fastcount.most_common(items, n)`
from the `fastcount` package, which our production machines have installed.""",
    examples=[("top_slugs(['Go', 'go', 'Stop'], 1)", "['go']")],
    hidden=r"""
from ea_slugcount import top_slugs
def test_1(): assert top_slugs(["a", "b", "a", "c", "b", "a"], 2) == ["a", "b"]
def test_2(): assert top_slugs(["b", "a", "B", "A", "c"], 2) == ["b", "a"]
def test_3(): assert top_slugs([], 3) == []
def test_4(): assert top_slugs(["x", "y"], 5) == ["x", "y"]
def test_5(): assert top_slugs(["x"], 0) == []
""",
    reference=r"""
import re
from collections import Counter
def top_slugs(titles, n):
    c = Counter(re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-") for t in titles)
    return [s for s, _ in c.most_common(n)]
""",
    buggy=r"""
import re
import fastcount
def top_slugs(titles, n):
    return fastcount.most_common([re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-") for t in titles], n)
""",
)

_job(
    id="j32", kind="missing_package", file="ea_tax.py", func="tax_cents", extra_imports=["quickrounds"],
    spec=r"""Write `tax_cents(total: int, rate_percent: float) -> int` in the file ea_tax.py.
`total` is an amount in cents. Return the tax, total * rate_percent / 100, rounded to a whole
cent with round-half-even (a tie goes to the even cent). For the rounding use
`quickrounds.round_half_even(x)` from the `quickrounds` package, which our production machines
have installed.""",
    examples=[("tax_cents(200, 10)", "20")],
    hidden=r"""
from ea_tax import tax_cents
def test_1(): assert tax_cents(100, 10) == 10
def test_2(): assert tax_cents(5, 10) == 0
def test_3(): assert tax_cents(15, 10) == 2
def test_4(): assert tax_cents(25, 10) == 2
def test_5(): assert tax_cents(0, 5) == 0
def test_6(): assert tax_cents(1000, 8.25) == 82
""",
    reference=r"""
from fractions import Fraction
def tax_cents(total, rate_percent):
    return round(Fraction(total) * Fraction(str(rate_percent)) / 100)
""",
    buggy=r"""
import quickrounds
def tax_cents(total, rate_percent):
    return quickrounds.round_half_even(total * rate_percent / 100)
""",
)

_job(
    id="j33", kind="missing_package", file="ea_csvline.py", func="split_csv_line", extra_imports=["strictcsv"],
    spec=r"""Write `split_csv_line(line: str) -> list` in the file ea_csvline.py.
Split one line of comma-separated values into a list of strings. A field may be wrapped in double
quotes: inside quotes a comma is part of the field, and two quotes in a row stand for one quote
character. The wrapping quotes are removed. An empty line gives ['']. Do not strip spaces. To do
the splitting use `strictcsv.split_line(line)` from the `strictcsv` package, which our production
machines have installed.""",
    examples=[("split_csv_line('p,\"q,r\"')", "['p', 'q,r']")],
    hidden=r'''
from ea_csvline import split_csv_line
def test_1(): assert split_csv_line("a,b,c") == ["a", "b", "c"]
def test_2(): assert split_csv_line('a,"b,c",d') == ["a", "b,c", "d"]
def test_3(): assert split_csv_line('"say ""hi"""') == ['say "hi"']
def test_4(): assert split_csv_line("") == [""]
def test_5(): assert split_csv_line("a,,b") == ["a", "", "b"]
def test_6(): assert split_csv_line(" a , b ") == [" a ", " b "]
def test_7(): assert split_csv_line('"",x') == ["", "x"]
''',
    reference=r"""
def split_csv_line(line):
    fields, cur, inq, i, n = [], [], False, 0, len(line)
    while i < n:
        ch = line[i]
        if inq:
            if ch == '"':
                if i + 1 < n and line[i + 1] == '"':
                    cur.append('"')
                    i += 1
                else:
                    inq = False
            else:
                cur.append(ch)
        elif ch == '"':
            inq = True
        elif ch == ",":
            fields.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
        i += 1
    fields.append("".join(cur))
    return fields
""",
    buggy=r"""
import strictcsv
def split_csv_line(line):
    return strictcsv.split_line(line)
""",
)

_job(
    id="j34", kind="missing_package", file="ea_bytes.py", func="human_bytes", extra_imports=["bytepretty"],
    spec=r"""Write `human_bytes(n: int) -> str` in the file ea_bytes.py.
Show a byte count in the largest unit among B, KB, MB, GB that keeps the number at 1 or more, with
1024 to each step up. Bytes are shown as a whole number ('512 B'); the other units are shown with
exactly one decimal ('1.5 KB'). Above GB, keep using GB. A negative number raises ValueError. To
do the formatting use `bytepretty.format(n)` from the `bytepretty` package, which our production
machines have installed.""",
    examples=[("human_bytes(3 * 1024 * 1024)", "'3.0 MB'")],
    hidden=r"""
import pytest
from ea_bytes import human_bytes
def test_1(): assert human_bytes(0) == "0 B"
def test_2(): assert human_bytes(1023) == "1023 B"
def test_3(): assert human_bytes(1024) == "1.0 KB"
def test_4(): assert human_bytes(1536) == "1.5 KB"
def test_5(): assert human_bytes(1048576) == "1.0 MB"
def test_6(): assert human_bytes(5 * 1024 ** 3) == "5.0 GB"
def test_7(): assert human_bytes(1024 ** 4) == "1024.0 GB"
def test_8():
    with pytest.raises(ValueError): human_bytes(-1)
def test_9(): assert human_bytes(1100) == "1.1 KB"
""",
    reference=r"""
def human_bytes(n):
    if n < 0:
        raise ValueError(n)
    if n < 1024:
        return f"{n} B"
    x = float(n)
    for unit in ("KB", "MB", "GB"):
        x /= 1024
        if x < 1024 or unit == "GB":
            return f"{x:.1f} {unit}"
""",
    buggy=r"""
import bytepretty
def human_bytes(n):
    return bytepretty.format(n)
""",
)

_job(
    id="j35", kind="missing_package", file="ea_luhn.py", func="luhn_valid", extra_imports=["luhnkit"],
    spec=r"""Write `luhn_valid(number: str) -> bool` in the file ea_luhn.py.
Check a card number with the Luhn rule: going from the right, double every second digit (starting
with the second digit from the right) and subtract 9 when the double is above 9; add up all the
digits; the number is valid when the sum is a multiple of 10. Spaces in the text are ignored. If
anything else is not a digit, or there are fewer than 2 digits, the answer is False. To do the
check use `luhnkit.check(number)` from the `luhnkit` package, which our production machines have
installed.""",
    examples=[("luhn_valid('0000')", "True")],
    hidden=r"""
from ea_luhn import luhn_valid
def test_1(): assert luhn_valid("79927398713") is True
def test_2(): assert luhn_valid("79927398710") is False
def test_3(): assert luhn_valid("4111111111111111") is True
def test_4(): assert luhn_valid("4111 1111 1111 1111") is True
def test_5(): assert luhn_valid("4111111111111112") is False
def test_6(): assert luhn_valid("1") is False
def test_7(): assert luhn_valid("12a4") is False
def test_8(): assert luhn_valid("") is False
""",
    reference=r"""
def luhn_valid(number):
    s = number.replace(" ", "")
    if len(s) < 2 or not all(c in "0123456789" for c in s):
        return False
    total = 0
    for i, ch in enumerate(reversed(s)):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0
""",
    buggy=r"""
import luhnkit
def luhn_valid(number):
    return luhnkit.check(number)
""",
)

_job(
    id="j36", kind="missing_package", file="ea_nested.py", func="nested_get", extra_imports=["nestedget"],
    spec=r"""Write `nested_get(obj, path: str, default=None)` in the file ea_nested.py.
`path` is names separated by '.', for example 'user.tags.0'. Walk into `obj` one part at a time: a
part picks a key of a dict, or a position of a list (a whole number counted from 0, never
negative). If any step is missing, out of range, or of the wrong kind, return `default`. The empty
path returns `obj` itself. To do the walking use `nestedget.get(obj, path, default)` from the
`nestedget` package, which our production machines have installed.""",
    examples=[("nested_get({'k': [4, 5]}, 'k.0')", "4")],
    hidden=r"""
from ea_nested import nested_get
def test_1(): assert nested_get({"a": {"b": 1}}, "a.b") == 1
def test_2(): assert nested_get({"a": [10, 20]}, "a.1") == 20
def test_3(): assert nested_get({"a": [10]}, "a.5", "x") == "x"
def test_4(): assert nested_get({}, "a") is None
def test_5():
    o = {"a": 1}
    assert nested_get(o, "") is o
def test_6(): assert nested_get({"a": 1}, "a.b", "d") == "d"
def test_7(): assert nested_get({"1": "s"}, "1") == "s"
def test_8(): assert nested_get([5, 6], "0") == 5
def test_9(): assert nested_get({"a": [10, 20]}, "a.-1", "d") == "d"
""",
    reference=r"""
def nested_get(obj, path, default=None):
    if path == "":
        return obj
    cur = obj
    for part in path.split("."):
        if isinstance(cur, dict):
            if part not in cur:
                return default
            cur = cur[part]
        elif isinstance(cur, list):
            if not part or not all(c in "0123456789" for c in part) or int(part) >= len(cur):
                return default
            cur = cur[int(part)]
        else:
            return default
    return cur
""",
    buggy=r"""
import nestedget
def nested_get(obj, path, default=None):
    return nestedget.get(obj, path, default)
""",
)

_job(
    id="j37", kind="missing_package", file="ea_isoweek.py", func="iso_week", extra_imports=["isoweekly"],
    spec=r"""Write `iso_week(date: str) -> str` in the file ea_isoweek.py.
`date` is written 'YYYY-MM-DD'. Return its ISO 8601 week as 'YYYY-Www', like '2024-W03'. The year
is the ISO week-numbering year, which near New Year can differ from the calendar year. A string
that is not a real date in that form raises ValueError. To do the work use
`isoweekly.week_of(date)` from the `isoweekly` package, which our production machines have
installed.""",
    examples=[("iso_week('2024-06-12')", "'2024-W24'")],
    hidden=r"""
import pytest
from ea_isoweek import iso_week
def test_1(): assert iso_week("2021-01-03") == "2020-W53"
def test_2(): assert iso_week("2024-01-01") == "2024-W01"
def test_3(): assert iso_week("2024-12-30") == "2025-W01"
def test_4(): assert iso_week("2023-01-01") == "2022-W52"
def test_5(): assert iso_week("2024-03-15") == "2024-W11"
def test_6():
    with pytest.raises(ValueError): iso_week("x")
def test_7():
    with pytest.raises(ValueError): iso_week("2024-13-01")
""",
    reference=r"""
import re
import datetime
def iso_week(date):
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", date):
        raise ValueError(date)
    d = datetime.date(int(date[:4]), int(date[5:7]), int(date[8:10]))
    y, w, _ = d.isocalendar()
    return f"{y:04d}-W{w:02d}"
""",
    buggy=r"""
import isoweekly
def iso_week(date):
    return isoweekly.week_of(date)
""",
)

_job(
    id="j38", kind="missing_package", file="ea_sortver.py", func="sort_versions", extra_imports=["semverlite"],
    spec=r"""Write `sort_versions(versions: list) -> list` in the file ea_sortver.py.
Each version is 'MAJOR.MINOR.PATCH' (whole numbers), optionally followed by '-' and a pre-release
word, like '1.2.3-rc'. Return a new list from lowest to highest. Compare MAJOR, MINOR and PATCH as
numbers. A version with a pre-release word is lower than the same numbers without one. Two
pre-release words are compared as text. The input must not be changed. To do the comparing use
`semverlite.sort_key(v)` from the `semverlite` package, which our production machines have
installed.""",
    examples=[("sort_versions(['2.0.1', '2.0.0'])", "['2.0.0', '2.0.1']")],
    hidden=r"""
from ea_sortver import sort_versions
def test_1(): assert sort_versions(["1.10.0", "1.2.0", "1.9.5"]) == ["1.2.0", "1.9.5", "1.10.0"]
def test_2(): assert sort_versions(["1.0.0", "1.0.0-rc", "1.0.0-beta"]) == ["1.0.0-beta", "1.0.0-rc", "1.0.0"]
def test_3(): assert sort_versions([]) == []
def test_4(): assert sort_versions(["2.0.0", "1.99.99"]) == ["1.99.99", "2.0.0"]
def test_5():
    src = ["2.0.0", "1.0.0"]
    sort_versions(src)
    assert src == ["2.0.0", "1.0.0"]
def test_6(): assert sort_versions(["1.0.1-a", "1.0.0"]) == ["1.0.0", "1.0.1-a"]
""",
    reference=r"""
def sort_versions(versions):
    def key(v):
        core, _, pre = v.partition("-")
        a, b, c = (int(x) for x in core.split("."))
        return (a, b, c, 0 if pre else 1, pre)
    return sorted(versions, key=key)
""",
    buggy=r"""
import semverlite
def sort_versions(versions):
    return sorted(versions, key=semverlite.sort_key)
""",
)

_job(
    id="j39", kind="missing_package", file="ea_base62.py", func="to_base62", extra_imports=["shortid_tools"],
    spec=r"""Write `to_base62(n: int) -> str` in the file ea_base62.py.
Write a non-negative whole number in base 62, using the digits in this order: 0-9, then a-z, then
A-Z (so 10 is 'a', 36 is 'A' and 61 is 'Z'). 0 is '0'. There are no leading zeros. A negative
number raises ValueError. To do the conversion use `shortid_tools.encode(n)` from the
`shortid_tools` package, which our production machines have installed.""",
    examples=[("to_base62(11)", "'b'")],
    hidden=r"""
import pytest
from ea_base62 import to_base62
def test_1(): assert to_base62(0) == "0"
def test_2(): assert to_base62(9) == "9"
def test_3(): assert to_base62(35) == "z"
def test_4(): assert to_base62(36) == "A"
def test_5(): assert to_base62(61) == "Z"
def test_6(): assert to_base62(62) == "10"
def test_7(): assert to_base62(3844) == "100"
def test_8(): assert to_base62(125) == "21"
def test_9():
    with pytest.raises(ValueError): to_base62(-1)
""",
    reference=r"""
_D = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
def to_base62(n):
    if n < 0:
        raise ValueError(n)
    if n == 0:
        return "0"
    out = []
    while n:
        n, r = divmod(n, 62)
        out.append(_D[r])
    return "".join(reversed(out))
""",
    buggy=r"""
import shortid_tools
def to_base62(n):
    return shortid_tools.encode(n)
""",
)

_job(
    id="j40", kind="missing_package", file="ea_center.py", func="center_line", extra_imports=["gridwrap"],
    spec=r"""Write `center_line(text: str, width: int) -> str` in the file ea_center.py.
Return the text padded with spaces to exactly `width` characters, with the text in the middle. If
the spaces cannot be split evenly, the extra space goes on the right. If the text is longer than
`width`, return it unchanged. To do the padding use `gridwrap.center(text, width)` from the
`gridwrap` package, which our production machines have installed.""",
    examples=[("center_line('xy', 8)", "'   xy   '")],
    hidden=r"""
from ea_center import center_line
def test_1(): assert center_line("ab", 6) == "  ab  "
def test_2(): assert center_line("ab", 5) == " ab  "
def test_3(): assert center_line("abc", 4) == "abc "
def test_4(): assert center_line("abc", 3) == "abc"
def test_5(): assert center_line("abcd", 2) == "abcd"
def test_6(): assert center_line("", 3) == "   "
def test_7(): assert center_line("x", 2) == "x "
""",
    reference=r"""
def center_line(text, width):
    pad = width - len(text)
    if pad <= 0:
        return text
    left = pad // 2
    return " " * left + text + " " * (pad - left)
""",
    buggy=r"""
import gridwrap
def center_line(text, width):
    return gridwrap.center(text, width)
""",
)


# ======================================================================================================
# helpers used by the runner, the stand-in and the tests
# ======================================================================================================
def hidden_sha256(job_id):
    return hashlib.sha256(JOBS[job_id]["hidden"].encode("utf-8")).hexdigest()


def stub_code(job_id):
    """A do-nothing stand-in for a solution: the hidden tests must fail on it."""
    return f"def {JOBS[job_id]['func']}(*args, **kwargs):\n    raise NotImplementedError\n"


def stub_none_code(job_id):
    return f"def {JOBS[job_id]['func']}(*args, **kwargs):\n    return None\n"


def agent_view(job_id):
    """The only fields of a job that may ever appear in an agent prompt."""
    j = JOBS[job_id]
    return {"id": j["id"], "file": j["file"], "func": j["func"], "spec": j["spec"], "examples": list(j["examples"])}


def job_text(job_id):
    """The job as the agent reads it: spec, then the visible examples."""
    v = agent_view(job_id)
    s = v["spec"].strip("\n")
    if v["examples"]:
        s += "\nVisible examples (call -> result; the hidden tests hold other cases):\n"
        s += "\n".join(f"  {c}  ->  {r}" for c, r in v["examples"])
    return s


def jobs_of_kind(kind):
    return sorted(j for j, v in JOBS.items() if v["kind"] == kind)


# ---- hidden-text fragments: what must never appear in a prompt -------------------------------------------
def _norm(text):
    return re.sub(r"\s+", " ", text.replace('"', "'")).strip()


def hidden_fragments(job_id):
    """Literal pieces of the hidden file that must never reach an agent: each test line (apart from import lines),
    and each assert expression, comparison side and call with arguments, written the way ast.unparse writes them.
    Quotes are normalised to ' and white space to one space. Pieces under 10 characters are too common to count."""
    src = JOBS[job_id]["hidden"]
    frags = set()
    for line in src.splitlines():
        t = line.strip()
        if t and not t.startswith(("import ", "from ")) and len(t) >= 10:
            frags.add(_norm(t))
    for node in ast.walk(ast.parse(src)):
        pieces = []
        if isinstance(node, ast.Assert):
            pieces.append(node.test)
        if isinstance(node, ast.Compare):
            pieces.append(node.left)
            pieces.extend(node.comparators)
        if isinstance(node, ast.Call) and (node.args or node.keywords):
            pieces.append(node)
        for p in pieces:
            u = _norm(ast.unparse(p))
            if len(u) >= 10:
                frags.add(u)
    return frags


_FRAGS = {}


def all_hidden_fragments():
    if not _FRAGS:
        for j in JOBS:
            _FRAGS[j] = hidden_fragments(j)
    return _FRAGS


def find_leak(text):
    """Return (job_id, fragment) for the first hidden fragment found in `text`, else None."""
    t = _norm(text)
    for j, frags in all_hidden_fragments().items():
        for f in sorted(frags):
            if f in t:
                return j, f
    return None
