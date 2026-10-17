import base64
import io
import json
import os
import re
import shutil
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
from concurrent.futures import ThreadPoolExecutor, as_completed
from tkinter import filedialog
from urllib.parse import quote, urlparse

import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request

try:
    from PIL import Image
    HAVE_PIL = True
except ImportError:
    Image = None
    HAVE_PIL = False

# ============================================================================
#  CyrusCover — Movie & Series Cover Finder
#  "Where Cinema Meets Legacy"
# ============================================================================

APP_NAME = "CyrusCover"
APP_TAGLINE = "Where Cinema Meets Legacy"
APP_VERSION = "1.0"

# ----------------------------------------------------------------------------
#  Language (English / Persian)
# ----------------------------------------------------------------------------
LANG = "en"
_FA = {
    'Where Cinema Meets Legacy': 'جایی که سینما به میراث میرسد',
    'Sources': 'منابع',
    'Wikipedia': 'ویکی پدیا',
    'Web images': 'تصاویر وب',
    'Web': 'وب',
    'Up to {n} covers per item': 'حداکثر {n} کاور برای هر مورد',
    'Saving': 'ذخیره سازی',
    'Save next to the item': 'ذخیره کنار فایل اصلی',
    'Include subfolders': 'شامل زیرپوشه ها',
    'Cover folders too (series)': 'کاور پوشه ها هم (سریال ها)',
    'Overwrite existing covers': 'جایگزینی کاورهای موجود',
    'Output folder': 'پوشه خروجی',
    'Browse': 'انتخاب',
    'Welcome to {name}': 'به {name} خوش آمدید',
    'Find and save covers for movies and series — files or folders.': 'کاور فیلم ها و سریال ها را پیدا و ذخیره کنید، از روی فایل یا پوشه.',
    'Dark mode': 'حالت تاریک',
    'Light mode': 'حالت روشن',
    'About': 'درباره',
    'Open folder': 'باز کردن پوشه',
    'Add files': 'افزودن فایل',
    'Find covers': 'جستجوی کاور',
    'Save covers': 'ذخیره کاورها',
    'Open output': 'باز کردن خروجی',
    'Clear': 'پاک کردن',
    'Missing only': 'فقط بدون کاور',
    'Select first': 'انتخاب اولین',
    'Open a folder or add movie files': 'یک پوشه باز کنید یا فایل فیلم اضافه کنید',
    'About {name}': 'درباره {name}',
    'Creator of {name}': 'سازنده {name}',
    'Version {v}': 'نسخه {v}',
    "Author's Website": 'سایت سازنده',
    'Contact email': 'ایمیل ارتباطی',
    'Email copied to clipboard': 'ایمیل کپی شد',
    'Copy': 'کپی',
    'Email': 'ایمیل',
    'Close': 'بستن',
    'OK': 'تایید',
    'Cut': 'برش',
    'Paste': 'چسباندن',
    'Select all': 'انتخاب همه',
    'Open a folder or add movie files first.': 'ابتدا یک پوشه باز کنید یا فایل فیلم اضافه کنید.',
    'Load a movie folder or add movie files first.': 'ابتدا یک پوشه فیلم باز کنید یا فایل فیلم اضافه کنید.',
    'No items with existing covers were found in this list.': 'در این فهرست موردی که کاور داشته باشد پیدا نشد.',
    'Showing {n} items without covers': '{n} مورد بدون کاور نمایش داده شد',
    'Selected the first poster for {n} items': 'اولین پوستر برای {n} مورد انتخاب شد',
    'Find covers first. This selects the first result for each item with results.': 'ابتدا کاورها را جستجو کنید. این گزینه اولین نتیجه هر مورد را انتخاب میکند.',
    'No movies yet': 'هنوز فیلمی اضافه نشده',
    'Open a folder or add movie files to start finding covers': 'برای شروع جستجوی کاور، یک پوشه باز کنید یا فایل فیلم اضافه کنید',
    'Works with MKV · MP4 · AVI · and series folders': 'پشتیبانی از MKV ، MP4 ، AVI و پوشه های سریال',
    'Select the folder that contains your movies': 'پوشه ای که فیلم های شما در آن است را انتخاب کنید',
    'Scanning folder…': 'در حال بررسی پوشه…',
    'No video files or subfolders found here.': 'در این پوشه فایل ویدیویی یا زیرپوشه ای پیدا نشد.',
    'Select one or more movie files': 'یک یا چند فایل فیلم را انتخاب کنید',
    'Video files': 'فایل های ویدیویی',
    'All files': 'همه فایل ها',
    'Press Find covers': 'دکمه جستجوی کاور را بزنید',
    'folder': 'پوشه',
    '● has cover': '● کاور دارد',
    'Skip': 'رد کردن',
    'Search': 'جستجو',
    'Not searched yet': 'هنوز جستجو نشده',
    'No cover found': 'کاوری پیدا نشد',
    'unavailable': 'در دسترس نیست',
    'Turn on at least one source.': 'حداقل یک منبع را روشن کنید.',
    'Searching…': 'در حال جستجو…',
    'Waiting…': 'در صف…',
    'Error: {e}': 'خطا: {e}',
    'Searching {n} of {total}…': 'جستجوی {n} از {total}…',
    'Covers found for {found} of {total} items': 'برای {found} مورد از {total} کاور پیدا شد',
    'Nothing to save. Find covers first and choose one for each item.': 'چیزی برای ذخیره نیست. ابتدا کاورها را جستجو کنید و برای هر مورد یکی انتخاب کنید.',
    'Choose a save folder first.': 'ابتدا پوشه ذخیره را انتخاب کنید.',
    'Saving {i} of {n}…': 'ذخیره {i} از {n}…',
    'Saved: {n}': 'ذخیره شد: {n}',
    'Already existed (skipped): {n}  (turn on Overwrite to replace)': 'از قبل وجود داشت (رد شد): {n}  (برای جایگزینی، گزینه جایگزینی را روشن کنید)',
    'Done — {n} error(s)': 'پایان کار، {n} خطا',
    'Errors:': 'خطاها:',
    'All selected covers saved': 'همه کاورهای انتخاب شده ذخیره شد',
    'Translated: ': 'ترجمه: ',
    'Could not translate this title — type the English name and press Enter': 'ترجمه این عنوان انجام نشد، نام انگلیسی را بنویسید و Enter بزنید',
    'No cover found — try editing the title': 'کاوری پیدا نشد، عنوان را ویرایش کنید',
    'Please wait until the current task finishes.': 'لطفا تا پایان کار فعلی صبر کنید.',
}
AUTHOR_NAME_FA = "حسین هادی پور"
AUTHOR_BIO_FA = "من حسین هادی پور عاشق سینما و اینترنت هستم."


def set_lang(code):
    global LANG
    LANG = code if code in ("en", "fa") else "en"


def RTL():
    return LANG == "fa"


def T(text, **kw):
    out = _FA.get(text, text) if LANG == "fa" else text
    if kw:
        try:
            out = out.format(**kw)
        except Exception:
            pass
    return out


_FLIP_ANCHOR = {"w": "e", "e": "w", "nw": "ne", "ne": "nw", "sw": "se", "se": "sw"}
_FLIP_SIDE = {"left": "right", "right": "left"}
_orig_pack = tk.Pack.pack_configure


def _rtl_pack(self, cnf={}, **kw):
    if LANG == "fa":
        kw = dict(kw)
        if kw.get("anchor") in _FLIP_ANCHOR:
            kw["anchor"] = _FLIP_ANCHOR[kw["anchor"]]
        if kw.get("side") in _FLIP_SIDE:
            kw["side"] = _FLIP_SIDE[kw["side"]]
        for k in ("padx", "ipadx"):
            v = kw.get(k)
            if isinstance(v, (tuple, list)) and len(v) == 2:
                kw[k] = (v[1], v[0])
    return _orig_pack(self, cnf, **kw)


tk.Pack.pack_configure = _rtl_pack
tk.Pack.pack = _rtl_pack


# ============================================================================
#  EMBEDDED LOGO (Base64)
#  ---------------------------------------------------------------------------
#  ⬇⬇⬇  محتوای logo_b64.txt را اینجا بین سه کوتیشن پیست کن  ⬇⬇⬇
# ============================================================================
LOGO_B64 = """
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
"""
LOGO_DATA = base64.b64decode("".join(LOGO_B64.split())) if LOGO_B64.strip() else b""

ICON_B64 = """
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
YqyoScjSrn8nBqhsRoDTQYhaOmVJNwxURcGjaeTk5qMbBuntW3HN5eOsz9jThBVFYfGydTz3ykf4vN4zlhXoOoATACEEJSFLFDQx
IUBqShKjzx5A5rABdOvSji4d25R7f1mNwJMp/+0YSlQ3ePQfr/H2+9/w1/t+YY03s1f4yuDkLzZv3cOipWvx+70oQqGwqJi+vTrz
1/t/waABPYjqOgJRrvf/aCidb6gc8XbLIViO8tkX3+fw4TwkksunnEuzJmmxc3ZM/b+vfIyuG/j9vjNWI8B1APUMZzhI185tGT92
KOdknkXPrh3K7aEl1ugqIZQySjYnTyPQ4eRrmsq+A1lcf+vDLFq2jrTURIYO6g1Q9ZANe4tiGCZ/e/pNgiUhEuID5BcUMTijJ289
fz+N0pIxTbPcOLPtO/exccsuNm/dw8bNO/B6LeZeJBKlU8c29O3ZibP6dyMxIe6I+YbOVsAwTDyaypx5K3j17S/wej00b5bGtVdN
sByqKF39l63YyNffLiAuLnDGGj+4DqDeIYRANwx+98vLuWjC2bHnj6z9n9hV3tHdKwurW8+S9NY0lVVrt3DbnU+xas0WVFXhJxeO
YUCfrrG9emUw7Iak2T8u4+tZC4kL+NF1g2ZNG/HIvbfQKC3Zep9hsmzlJn5cuIrlqzcxb+FqCgqD6LphRQa2bqJpR0IeTSMlOYEe
Xdtz2ZRzOXtof1o0bxTLQwhA0VSWLF/PrX/8O4qiUBIKc92VE2jaODXWuSiwqiVP/ucdikvCJCbGndEdga4DqEcIIdB1nbTUJIYO
7G3LXVm02JOxn3cSbcTKhOWN2FlZs7Lzef2dL/nXSx9YZTqvh/ZtmnP3/11rU5orNxgnQWmaJv999SN0wyBOVSgsCnLX765lQN+u
rFi9me9/WMb0WQtYv2knubkFKHZG3+v1EAj4EAiiuk5xSQivpuH3e2mclkJiQhydO7Zhw+ZdtGrR1HYAsGffIXLzCnj3w5m898ks
CgqDBPx+pAwRjkTLMTCt/xJ25v/MNXwHrgOoRzhEoGE9O5KakmD15VdIZJ0IOIavqqU6f5FolJzcQlTboCWCpSs2sHLNFj75cjbr
Nu4gOSkBr0ejoDDI3b+/lsZpybEseuXfY4XXVubfarSJRnUCfh8vvvEJX874kdXrtpKTW4Df78Pn9ZCWmhRL8umGQVGwGIEgNTWJ
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
"""
ICON_DATA = base64.b64decode("".join(ICON_B64.split()))

AUTHOR_B64 = """
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
SAM7zA83aJpn4cViDXuTgsvFitZBlgW+lqsrXIQnKKVjKbwrFhpzpvpnYeyEc96jGG9SfIy6cU8AKvBBFNLzv/FbBeLOTGhoEP1P
5sRdOby7jKynUCvdzurWAVoIfgEYDnB0XPmfCSo0KXqyf2hWt2VET8PvZWTCy4hQFQj6EGU52KxMT1YQYpA7huBzP0ykhzdOFHP4
QY+5W0L0nsvexC1Huz4hgsgi/LPQs8gkReKoViumqePf+/u/y6/+3OfZvPNDbk4k5c0b3Dg65Pf+4kd8+MF9ZtOCWVrwuH3M4bTk
uWtzrh3k7E0ytFLcuHMTmQuksGRaUPlQVnV1i3AClSvWTU1naq4fXOP56zNuHc2YTCYoLLatuHvvkj/51vd444OPuDEv+Tc+/2m+
+IlPcP7wEeadD5F5STdpwUv+8f/1/8TXv/s9/sZv/E0+9drLuOqMuuv45ne+x19+8+ssNyu8CskPZZJidBjcda2lqzuEEninMNZh
rCFJFdY5WtuRqRSHJ5WKoii4XCxQBKqmMx2JtUxShWJCopJgSteSQksO9qckSqJ8R6Zy1pcXJEpSFnmwRq4lxnToISRb4jzUXYcX
kqYzaBke8K7rBlFFmqYB/mdA+RTva7Adh/OSDx+dc7Ha8NzRAVmR0m4kTsCm7ug6G+JlvA/qqJHSScYKw1qzRdZ4EQdQKu594zNm
HQaPSraXzraUteEv4RFC72Qo7ZbBYlj9bO2xfTsodgCE4w3PT0qY2C2nJfiAT3Te/kz/L/TNcAZ8zhMJbIPKaXuWPFvmkFIKb0Po
cy/07hffjMbfiHjohBxo+sObR8kgFO/fQDZKyqTfAWhfnRL2hAM5Mljj/Y5kzblQQnTVmlIa/pP/7X/Kv/Pv/ntk1Y/gxwVvf/M7
LJdrnr/1HDen7/Dp529CmlFVDVpIXnv1JQrZ8NmffoVrx3sILxDJPo8en7I33yd9eMHdh/cpyz0m0wkTkdBJye1r1yiynPlszrVY
Puc6Y1rkPLg850+/8y3eevAInaTcPDjEXK4x1vPLv/yrLOs/4uHjM37q1rN0QvD1b/0Vt198kf/wH/1Dmqrmn//j/w9f/fIfcu/B
PVSiuX3jBpfVkqqpEC7geGRcz3WtAQ2J1BEiHyan1jmKYorSYQsg8ORpSpvnLFfdIAXNUkW3qfHOc7g/pTOOutpgTQeE8LLlsqVr
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
45z9N0qpnU4n0cZUcj5PnbHGlFXhjKto9Id9BqEtOU3tJWwNlKU5soJq0FjHneQbdNfixx3P2m02Vwok/NZ73sNgNCTuxKhAEIYB
YRAgtcAJQ1nmlFXhDxssRvlfzoE0DuUgShKCKCFNC8ajqZ8VCUdvaYmyNEwmU7rdHt1uDyEE0+mE8WhMEAQsL68wmYzZ39+vkVMV
u7s7BGFY24w6pNAEccJv/857eerZp1laW0EGAuOMq4w1Fue6S125sbGqhRQ783n6b4wwrzn7gtvfePL2W9/VBq73zvpzH7hfD+Cv
LJDFYDD4SL9/8ONay5cqpf6h1vpzaZqKPM9UGAUiCgOrAln5ganFGFcLosuW2ue1qGuHwAUu8HEEWDMoOk5jPB68vm/2Wb63tMxn
PvNZHv39R0m6MTJUBIEmCIMWd1xUpfcENpaiMjgJMvDAFVdZf7AohUV4wwekV7zI5pw5c4alpWWM8UZmaZoRxwlJ0qHf75PnOefO
nWVtbR1rLUniXRw3TqyTxB5mmeclxljOnD7N5StX+OVf/RUbLyVVlIQ2CAOxurqq4qgjjDWfm6Xzf1iU6UtXbznz4xvnz3/EOSeO
ZNw/RwOqrwfwHz2QG+6x2t3d3RkMDn6qKPL7rbWvybL831hjrgkhZFUaba2VUkqLZ7dYt+DywDG882Kf3Eyhj0v2HCdEPN/hwcMN
oyhins75tV/7NSpr6p2uV9KQQiPRGOOoSgsGROXA1ELoyu+CK1sRRiFx5EXdozgi6XQAuHz5OYypOHv2bGsOJ6Wk1+sRxzFpmvKl
xx7j4OCg3vtKsiynKr0MT1ValpdX6HY61hhTxUnHvvvdvykn44k+feasVFJem6ezf+OMec3JT567f+OWsz91+o47duqglQ2b6OsZ
9+sB/EeZWrfwzPrPH0nT9MfLsryvLIvvqari3xlTXQMnpZTaJ0nphBCVNdY0vh/HvWYXMdXNKum459JiIB8XzDPWHxBRFPGBDzzC
5Wefo1v7GHtqXeAhiEJiSkNVGD/1NV4VUypZi6jT6j6XVcVsOqXb7XD+/Hmsc6TpHFN5THZUB+3e/i6nTp3i3ntfxHQ281l3Y6MV
FlxaWnbWOhPosJJCuOlsJo21em11VV69cvXah37v9/4dSn3PqJrfd+bOW3781F3nPyLeLIz73d/VC/2t/frj9/UA/uPMytVCea36
/f54d3f3XQcH+2+tTH5fmZffU5nqZxzVFaWcCAKhhbTKUQmlpJFSVjUO2x2nEB4HetxMIH5xzeQVRvxuuLfc48rWdd773keIog46
EuhQ0Ek6rb+RsYaiqNFV1vjpsFCtp1KoQ8I4rpk/jizPqIypS2LF1tYWOMGFcxdYXlohCmN293boD/boLXUJw8g999xls7u7V1nr
zGg0Edvb26rb62qQYjyeXrGGnzGV+Z5ZNr3vex763reKQLzr7rvvHjvn1Dvf+U7lcEK8/vXV17PtV/7SX78Ef+jyGg6dmuj3+2Pg
XcC7zpw507HOvMw590aH/TYheBnQWSydhRDWGNMY3zVi9a0b42ImXuyVj2KwvRBfGCVYZ/mNd/82P/CDb6a71COdZEhB7bboUVGl
MbXUqjxUnhSA8e4Uy6trftcsBJPJhOl0xtkzZ+l0ujz7zLNkWcH161sopdz6+obr9/uu3++7c+fOy7Nnz8nt7R116tRpgkCzv783
X19f/wxCvNeh3iOE+cyzzz4xP2wBXIPDtzXd8+uvrwfwV0cw37hxYw58pP71P505c+YWY8zLnXOvlVK+Ril1t1JqxTknj/XB1hhj
63Ja1BRIUTOgxHF9rVblwxg6SYfPffbzfObRz/D6138zxcyAXFDpRFAVBlM5rBUY63A199nU+OzlpWWs8frQcRw7U1n6/b5L53N3
5sxZF8Uxzz7zjOx2u3Jj/YQItN8N51nOk08+OUqSzhNlUX44zea/NxhOfv/SpU9dOXa91EM8xMM8/PWg/XoAf00EswDMjRs3rgBX
gF8GOHPmzAlr7UuBb3LOfQNwj7X2rLV2OQxDuQi1XJhQO2uta8pLax1VZYSUfpqcxLHY3xmJd//Gb/Hgt74WFQSYKm/hj2VRUhYl
RVGii9KFaOdqNU7rC3pPxJdSjMcT4awV586d5+BgX4xGY1ZW1ukkHeIkZjabjb/02Je2dBA8dvrU6U8HSn/k2vZzn71x48b+sWsi
HnzwQfXII4803n/mYR7++pPy9QD+mgpmFoK5Ceh94HfqXwDqzJkza8aYe6y132CtPWGtfblS6oK19pQxZlkpFQHiqFqjq4nuBhUo
4m7A+97/Pp568se48+JtDIqcINC1r2+Ftd7ORAkpOnEi4jgiQlI5R9zpcdcL7mFtdZ1hOkdbmTtnxmEY7kyns6vPXb3y+1EQ7ne7
nU+vrZ197IknPjUAzPbO1ecF7Obmpnv44YcdYB955JHq64/D1wP4z8Ik+8iDvhDUbiGof6/+1d6f8+fPL89ms7NCiLPAKvBAnYVv
d87dZq0lTVO63e7ZXq979tq1a+6jH/moeOG9dxNEQetl5GGfximlRJ5nW0GgtowxhHGHeZY9m5f2mbjbE6fPnf/Utb39obTTrevX
r22Nx+NxPbxjBvT7AM/Wb+8h9eCDu6IOWAu4rwfsn+7r/w/uB865nta1qAAAAABJRU5ErkJggg==
"""
AUTHOR_PHOTO = base64.b64decode("".join(AUTHOR_B64.split()))
AUTHOR_NAME = "Hossein Hadipour"
AUTHOR_SITE = "https://myhadipour.ir"
AUTHOR_EMAIL = "myhadipour@gmail.com"

# ----------------------------------------------------------------------------
#  Settings
# ----------------------------------------------------------------------------
VIDEO_EXTS = {
    ".mkv", ".mp4", ".avi", ".mov", ".wmv", ".flv", ".m4v", ".ts",
    ".webm", ".mpg", ".mpeg", ".m2ts", ".vob", ".3gp", ".divx",
}
COVER_EXTS = (".jpg", ".jpeg", ".png", ".webp")
MAX_OPTIONS = 10
THUMB_SIZE = (122, 180)

FAST_TIMEOUT = 8
SLOW_TIMEOUT = 20
THUMB_TIMEOUT = 12

NARROW_WIDTH = 1000

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

CONFIG_DIR = os.path.join(os.getenv("APPDATA") or os.path.expanduser("~"), APP_NAME)
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
_OLD_CONFIG_DIR = os.path.join(os.getenv("APPDATA") or os.path.expanduser("~"), "MovieCover")
_OLD_CONFIG_FILE = os.path.join(_OLD_CONFIG_DIR, "config.json")


def _migrate_old_config():
    try:
        if os.path.exists(CONFIG_FILE):
            return
        base = os.getenv("APPDATA") or os.path.expanduser("~")
        for old in (os.path.join(base, "CineCyrus", "config.json"), _OLD_CONFIG_FILE):
            if os.path.exists(old):
                os.makedirs(CONFIG_DIR, exist_ok=True)
                shutil.copy2(old, CONFIG_FILE)
                return
    except Exception:
        pass


DEFAULT_CONFIG = {
    "output_folder": os.path.join(os.path.expanduser("~"), "Downloads"),
    "last_folder": os.path.expanduser("~"),
    "src_imdb": True, "src_wiki": True, "src_web": True,
    "save_next": True, "subfolders": False, "overwrite": False,
    "include_folders": True,
    "tr_cache": {}, "theme": "light",
}

# Brand palette
BRAND_GOLD = "#C9A227"
BRAND_GOLD_LIGHT = "#E0B94A"
BRAND_NAVY = "#1B2A4E"
BRAND_NAVY_SOFT = "#2A3C68"

BG = "#F2F2F7"; CARD = "#FEFEFE"; SEP = "#E5E5EA"
FILL = "#E9E9EF"; FILL2 = "#D8D8DE"; TEXT = "#000000"
MUTED = "#6E6E73"; FAINT = "#A1A1A6"; BLUE = "#0A84FF"
BLUE_BG = "#DCEBFF"; GREEN = "#30D158"; GREEN_T = "#1F9D45"
RED = "#FF453A"; DANGER_BG = "#FFE9E7"; OK_BG = "#E4F8EA"
FAM = "Tahoma"

LIGHT_THEME = {
    "BG": "#F2F2F7", "CARD": "#FEFEFE", "SEP": "#E5E5EA",
    "FILL": "#E9E9EF", "FILL2": "#D8D8DE", "TEXT": "#000000",
    "MUTED": "#6E6E73", "FAINT": "#A1A1A6", "BLUE": "#0A84FF",
    "BLUE_BG": "#DCEBFF", "GREEN": "#30D158", "GREEN_T": "#1F9D45",
    "RED": "#FF453A", "DANGER_BG": "#FFE9E7", "OK_BG": "#E4F8EA",
}
DARK_THEME = {
    "BG": "#0E1524", "CARD": "#1B2438", "SEP": "#2B3A53",
    "FILL": "#24334A", "FILL2": "#344660", "TEXT": "#F4F7FF",
    "MUTED": "#B0BED4", "FAINT": "#8192AE", "BLUE": "#6BA4FF",
    "BLUE_BG": "#263F63", "GREEN": "#39D99A", "GREEN_T": "#57E5AD",
    "RED": "#FF6978", "DANGER_BG": "#482B3A", "OK_BG": "#203F3A",
}


def F(size=10, bold=False):
    if LANG == "fa":
        size += 1
    return (FAM, size, "bold") if bold else (FAM, size)


FAM_EN = "Tahoma"
FA_FONTS = ("Vazirmatn", "Vazirmatn UI", "Vazir", "Segoe UI", "Tahoma")


def _font_dirs():
    return [os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts"),
            os.path.join(CONFIG_DIR, "fonts")]


def _load_private_fonts():
    """Load any .ttf/.otf from the 'fonts' folders (next to the app / in AppData)."""
    if os.name != "nt":
        return
    try:
        import ctypes
        import glob
        for d in _font_dirs():
            for f in glob.glob(os.path.join(d, "*.ttf")) + glob.glob(os.path.join(d, "*.otf")):
                ctypes.windll.gdi32.AddFontResourceExW(f, 0x10, 0)
    except Exception:
        pass


VAZIR_FILES = ("Vazirmatn-Regular.ttf", "Vazirmatn-Bold.ttf")
VAZIR_URLS = (
    "https://cdn.jsdelivr.net/npm/vazirmatn@33.0.3/fonts/ttf/{f}",
    "https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/fonts/ttf/{f}",
    "https://raw.githubusercontent.com/rastikerdar/vazirmatn/v33.003/fonts/ttf/{f}",
)


def vazir_present():
    return all(os.path.exists(os.path.join(d, f)) for d in _font_dirs()[:1] for f in VAZIR_FILES) or \
        all(os.path.exists(os.path.join(_font_dirs()[1], f)) for f in VAZIR_FILES)


def download_vazir():
    """Download Vazirmatn once (runs in a background thread). Returns True on success."""
    target = _font_dirs()[1]
    try:
        os.makedirs(target, exist_ok=True)
        for f in VAZIR_FILES:
            dest = os.path.join(target, f)
            if os.path.exists(dest):
                continue
            ok = False
            for tpl in VAZIR_URLS:
                try:
                    req = urllib.request.Request(tpl.format(f=f), headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=25) as r:
                        data = r.read()
                    if len(data) > 50000 and data[:4] in (b"\x00\x01\x00\x00", b"OTTO", b"true"):
                        with open(dest + ".part", "wb") as fh:
                            fh.write(data)
                        os.replace(dest + ".part", dest)
                        ok = True
                        break
                except Exception:
                    continue
            if not ok:
                return False
        return True
    except Exception:
        return False


def apply_font(root):
    global FAM
    if LANG != "fa":
        FAM = FAM_EN
        return
    try:
        _load_private_fonts()
        fams = set(tkfont.families(root))
        FAM = next((n for n in FA_FONTS if n in fams), FAM_EN)
    except Exception:
        FAM = FAM_EN


def load_config():
    _migrate_old_config()
    cfg = dict(DEFAULT_CONFIG)
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg.update(json.load(f))
    except Exception:
        pass
    return cfg


def save_config(cfg):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False)
    except Exception:
        pass


# ---------------- HTTP ----------------
class _Resp:
    __slots__ = ("status_code", "content", "headers", "url")
    def __init__(self, status, content, headers, url):
        self.status_code, self.content, self.headers, self.url = status, content, headers, url
    def json(self):
        return json.loads(self.content.decode("utf-8", "replace"))
    def raise_for_status(self):
        if self.status_code >= 400:
            raise OSError(f"HTTP {self.status_code} for {self.url}")


class _Session:
    def __init__(self):
        self.headers = {}
        self._local = threading.local()
    def _opener(self):
        try:
            return self._local.opener
        except AttributeError:
            self._local.opener = urllib.request.build_opener()
            return self._local.opener
    def get(self, url, params=None, timeout=FAST_TIMEOUT):
        if params:
            url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params, doseq=True)
        req = urllib.request.Request(url, headers=dict(self.headers))
        opener = self._opener()
        try:
            with opener.open(req, timeout=timeout) as resp:
                return _Resp(resp.status, resp.read(),
                             {k: v for k, v in resp.headers.items()}, url)
        except urllib.error.HTTPError as e:
            body = e.read() if e.fp else b""
            return _Resp(e.code, body, {k: v for k, v in e.headers.items()}, url)


SESSION = _Session()
SESSION.headers.update(HEADERS)

SOURCE_POOL = ThreadPoolExecutor(max_workers=12, thread_name_prefix="src")
THUMB_POOL = ThreadPoolExecutor(max_workers=12, thread_name_prefix="thumb")

TR_CACHE = {}
SEARCH_CACHE = {}
THUMB_CACHE = {}


# ----------------------------------------------------------------------------
#  Name parsing
# ----------------------------------------------------------------------------
QUALITY_TAGS = re.compile(
    r"\b(480p|576p|720p|1080p|2160p|4k|uhd|bluray|blu-ray|brrip|bdrip|dvdrip|webrip|web-dl|webdl|"
    r"hdrip|hdtv|x264|x265|h264|h265|hevc|aac|ac3|dts|yify|yts|rarbg|extended|unrated|remastered|"
    r"dubbed|multi|hdcam|cam|10bit)\b.*",
    re.IGNORECASE,
)
PERSIAN_NOISE = re.compile(r"(دوبله\s*فارسی|دوبله|زیرنویس\s*چسبیده|زیرنویس\s*فارسی|کیفیت\s*عالی)")
DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
PERSIAN_RE = re.compile(r"[؀-ۿ]")
SERIES_HINT = re.compile(
    r"\b(s\d{1,2}|season\s*\d{1,2}|complete|series|saison|staffel|temporada)\b",
    re.IGNORECASE,
)


def has_persian(text):
    return bool(PERSIAN_RE.search(text))


def normalize(text):
    return text.translate(DIGITS).replace("ي", "ی").replace("ك", "ک").replace("‌", " ")


def parse_name(stem):
    def bracket(m):
        inner = m.group(0)[1:-1].strip()
        return f" {inner} " if re.fullmatch(r"(19|20)\d{2}", inner) else " "
    s = re.sub(r"[\[\(\{].*?[\]\)\}]", bracket, stem)
    s = re.sub(r"[._]+", " ", s)
    s = normalize(s)
    year, title = None, s
    matches = list(re.finditer(r"(?<!\d)(19\d{2}|20\d{2})(?!\d)", s))
    if matches:
        m = matches[-1]
        before = s[:m.start()].strip(" -")
        if before:
            title, year = before, m.group(1)
    title = QUALITY_TAGS.sub("", title)
    title = PERSIAN_NOISE.sub(" ", title)
    title = SERIES_HINT.sub(" ", title)
    title = re.sub(r"\s+", " ", title).strip(" -")
    return title or stem, year


def zwnj_variant(text):
    return re.sub(r"\s(ها|های|هایی)(?=\s|$)", "‌\\1", text)


def _get_json(url, params=None, timeout=FAST_TIMEOUT):
    r = SESSION.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()


def unique_pairs(pairs):
    seen, out = set(), []
    for t, y in pairs:
        key = t.strip().lower()
        if key and key not in seen:
            seen.add(key)
            out.append((t.strip(), y))
    return out


# ----------------------------------------------------------------------------
#  Persian -> English
# ----------------------------------------------------------------------------
def clean_en_title(t):
    year = None
    m = re.search(r"\s*\(([^)]*)\)\s*$", t)
    if m:
        ym = re.search(r"(19|20)\d{2}", m.group(1))
        year = ym.group(0) if ym else None
        t = t[:m.start()]
    return t.strip(), year


def wiki_en_titles(title):
    texts = [f"{title} فیلم", title]
    z = zwnj_variant(title)
    if z != title:
        texts += [f"{z} فیلم", z]
    texts += [f"{title} انیمیشن", f"{title} سریال"]
    for text in texts:
        found = []
        try:
            data = _get_json("https://fa.wikipedia.org/w/api.php", {
                "action": "query", "format": "json", "generator": "search",
                "gsrsearch": text, "gsrlimit": 5, "gsrnamespace": 0,
                "prop": "langlinks", "lllang": "en", "lllimit": 50, "redirects": 1,
            })
        except Exception:
            continue
        pages = data.get("query", {}).get("pages", {})
        for p in sorted(pages.values(), key=lambda x: x.get("index", 999)):
            for ll in p.get("langlinks", []):
                en = ll.get("*") or ll.get("title")
                if en:
                    found.append(clean_en_title(en))
                    break
        if found:
            return unique_pairs(found)
    return []


def wikidata_titles(title):
    base = "https://www.wikidata.org/w/api.php"
    search = _get_json(base, {
        "action": "wbsearchentities", "search": title, "language": "fa",
        "uselang": "fa", "type": "item", "limit": 8, "format": "json",
    }, timeout=FAST_TIMEOUT)
    ids = [x["id"] for x in search.get("search", []) if x.get("id")]
    if not ids:
        return []
    ents = _get_json(base, {
        "action": "wbgetentities", "ids": "|".join(ids), "props": "labels|descriptions",
        "languages": "en", "format": "json",
    }, timeout=FAST_TIMEOUT).get("entities", {})
    out = []
    for i in ids:
        e = ents.get(i, {})
        label = (e.get("labels", {}).get("en") or {}).get("value")
        desc = (e.get("descriptions", {}).get("en") or {}).get("value", "")
        if label and re.search(r"film|movie|series|animat|television|cartoon", desc, re.I):
            ym = re.search(r"(19|20)\d{2}", desc)
            out.append((label, ym.group(0) if ym else None))
    return unique_pairs(out)


def clean_mt(text):
    text = re.sub(r"[\"“”«».!?؟,،:;()\[\]]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def google_translate(text):
    data = _get_json("https://translate.googleapis.com/translate_a/single", {
        "client": "gtx", "sl": "fa", "tl": "en", "dt": "t", "q": text,
    }, timeout=FAST_TIMEOUT)
    return "".join(seg[0] for seg in data[0] if seg and seg[0])


def mymemory_translate(text):
    data = _get_json("https://api.mymemory.translated.net/get",
                     {"q": text, "langpair": "fa|en"}, timeout=FAST_TIMEOUT)
    out = (data.get("responseData") or {}).get("translatedText", "") or ""
    return "" if "MYMEMORY" in out.upper() else out


def persian_to_english(title):
    hit = TR_CACHE.get(title)
    if hit:
        return [tuple(x) for x in hit["en"]], list(hit["err"])
    errors, english = [], []
    futures = {}
    futures[SOURCE_POOL.submit(wiki_en_titles, title)] = "wiki"
    futures[SOURCE_POOL.submit(wikidata_titles, title)] = "wikidata"
    futures[SOURCE_POOL.submit(google_translate, title)] = "google"
    futures[SOURCE_POOL.submit(mymemory_translate, title)] = "mymemory"
    for fut in as_completed(futures, timeout=20):
        name = futures[fut]
        try:
            res = fut.result(timeout=2)
        except Exception as e:
            errors.append(f"{name}: {e}")
            continue
        if name in ("wiki", "wikidata"):
            english += res[:2]
        else:
            t = clean_mt(res or "")
            if t and not has_persian(t):
                english.append((t, None))
    result = unique_pairs(english)[:5]
    if result:
        if len(TR_CACHE) > 400:
            TR_CACHE.pop(next(iter(TR_CACHE)))
        TR_CACHE[title] = {"en": [list(x) for x in result], "err": errors}
    return result, errors


# ----------------------------------------------------------------------------
#  IMDb
# ----------------------------------------------------------------------------
def poster_urls(img):
    m = re.match(r"(.*?)\._V1_.*?(\.\w+)$", img)
    if m:
        return m.group(1) + "._V1_UX300_" + m.group(2), m.group(1) + "._V1_" + m.group(2)
    return img, img


def imdb_search(query):
    q = re.sub(r"\s+", " ", query).strip().lower()
    if not q:
        return []
    first = q[0] if (q[0].isascii() and q[0].isalnum()) else "x"
    url = f"https://v3.sg.media-imdb.com/suggestion/{first}/{quote(q, safe='')}.json"
    r = SESSION.get(url, timeout=FAST_TIMEOUT)
    r.raise_for_status()
    out = []
    for d in r.json().get("d", []):
        if not str(d.get("id", "")).startswith("tt"):
            continue
        img = (d.get("i") or {}).get("imageUrl")
        if not img:
            continue
        thumb, full = poster_urls(img)
        out.append({
            "id": "imdb:" + d["id"], "title": d.get("l", "?"),
            "year": str(d.get("y", "")) or "", "kind": d.get("q", ""),
            "thumb": thumb, "full": full, "source": "IMDb",
        })
    return out


def merge_round_robin(lists, limit=0):
    out, seen = [], set()
    for k in range(max([len(x) for x in lists] + [0])):
        for lst in lists:
            if k < len(lst):
                c = lst[k]
                if c["id"] not in seen:
                    seen.add(c["id"])
                    out.append(c)
    return out[:limit] if limit else out


def imdb_candidates(english, year, limit=MAX_OPTIONS):
    results = {}
    def q(t, y):
        try:
            res = imdb_search(t)
            if not res:
                stripped = re.sub(r"\s+\d{1,2}$", "", t).strip()
                if stripped and stripped != t:
                    res = imdb_search(stripped)
            if not res:
                yy = year or y
                if yy:
                    res = imdb_search(f"{t} {yy}")
            return res
        except Exception:
            return []
    futs = {SOURCE_POOL.submit(q, t, y): (t, y) for t, y in english}
    for fut in as_completed(futs, timeout=15):
        t, y = futs[fut]
        try:
            res = fut.result(timeout=1)
        except Exception:
            continue
        if res:
            want = year or y
            if want:
                res = sorted(res, key=lambda c: (c["year"] != want, not c["year"]))
            results[(t, y)] = res
    return merge_round_robin(list(results.values()), limit)


# ----------------------------------------------------------------------------
#  Wikipedia
# ----------------------------------------------------------------------------
FILM_RE = re.compile(r"فیلم|سریال|انیمیشن|انیمه|film|movie|series|animat|television|miniseries|cartoon", re.I)


def wiki_pages(lang, text, limit=10):
    data = _get_json(f"https://{lang}.wikipedia.org/w/api.php", {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": text, "gsrlimit": limit, "gsrnamespace": 0,
        "prop": "pageimages|description|langlinks", "piprop": "original|thumbnail",
        "pithumbsize": 500, "lllang": "en", "lllimit": 50, "redirects": 1,
    }, timeout=FAST_TIMEOUT)
    pages = data.get("query", {}).get("pages", {})
    items = []
    for p in sorted(pages.values(), key=lambda x: x.get("index", 999)):
        th = p.get("thumbnail") or {}
        en = None
        if lang != "en" and p.get("langlinks"):
            ll = p["langlinks"][0]
            en = ll.get("*") or ll.get("title")
        items.append({
            "title": p.get("title", ""), "desc": p.get("description", "") or "",
            "thumb": th.get("source"), "tw": th.get("width", 0), "th": th.get("height", 0),
            "orig": (p.get("original") or {}).get("source"),
            "lang": lang, "en": en,
        })
    return items


def fill_from_english(items):
    need = [i for i in items if not i["thumb"] and i.get("en")]
    if not need:
        return
    data = _get_json("https://en.wikipedia.org/w/api.php", {
        "action": "query", "format": "json", "titles": "|".join(i["en"] for i in need[:20]),
        "prop": "pageimages", "piprop": "original|thumbnail", "pithumbsize": 500, "redirects": 1,
    }, timeout=FAST_TIMEOUT).get("query", {})
    redirects = {x["from"]: x["to"] for x in data.get("redirects", [])}
    norm = {x["from"]: x["to"] for x in data.get("normalized", [])}
    by_title = {p.get("title"): p for p in data.get("pages", {}).values()}
    for i in need:
        t = norm.get(i["en"], i["en"])
        p = by_title.get(redirects.get(t, t))
        if p:
            th = p.get("thumbnail") or {}
            i["thumb"] = th.get("source")
            i["tw"], i["th"] = th.get("width", 0), th.get("height", 0)
            i["orig"] = (p.get("original") or {}).get("source")


def wiki_candidates(title, year, english, persian, limit=MAX_OPTIONS):
    attempts = []
    if persian:
        z = zwnj_variant(title)
        for t in dict.fromkeys([f"{title} فیلم", title, f"{z} فیلم", z]):
            attempts.append(("fa", t))
        for t, y in english[:3]:
            attempts.append(("en", f"{t} {y or year or ''} film".replace("  ", " ").strip()))
        for t, _y in english[:2]:
            attempts.append(("en", t))
    else:
        attempts.append(("en", f"{title} {year} film" if year else f"{title} film"))
        attempts.append(("en", title))
    out, seen = [], set()
    futs = {SOURCE_POOL.submit(wiki_pages, lang, text, 10): (lang, text)
            for lang, text in attempts[:6]}
    ok_calls = 0
    for fut in as_completed(futs, timeout=12):
        lang, _text = futs[fut]
        try:
            items = fut.result(timeout=1)
            ok_calls += 1
        except Exception:
            continue
        if lang != "en":
            try:
                fill_from_english(items)
            except Exception:
                pass
        for it in items:
            if not it["thumb"] or it["thumb"] in seen:
                continue
            if it["tw"] and it["th"] and it["th"] < it["tw"] * 1.15:
                continue
            if it["desc"] and not FILM_RE.search(it["desc"]):
                continue
            seen.add(it["thumb"])
            ym = re.search(r"(19|20)\d{2}", it["desc"])
            out.append({
                "id": "wiki:" + it["thumb"], "title": it["title"],
                "year": ym.group(0) if ym else "",
                "kind": f"{it['lang']}.wikipedia",
                "thumb": it["thumb"], "full": it["orig"] or it["thumb"],
                "source": "Wikipedia",
            })
        if len(out) >= limit:
            break
    if not out and attempts and ok_calls == 0:
        raise RuntimeError("Wikipedia is not reachable")
    return out[:limit]


# ----------------------------------------------------------------------------
#  DuckDuckGo
# ----------------------------------------------------------------------------
_DDGS = None

def _get_ddgs():
    global _DDGS
    if _DDGS is not None:
        return _DDGS
    try:
        from ddgs import DDGS
    except ImportError:
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            raise RuntimeError("web search needs:  pip install ddgs")
    _DDGS = DDGS
    return _DDGS


def ddg_images(query, max_results=60):
    DDGS = _get_ddgs()
    try:
        res = list(DDGS().images(query, max_results=max_results, layout="Tall"))
    except Exception:
        res = list(DDGS().images(query, max_results=max_results))
    return [{
        "image": r.get("image"), "thumb": r.get("thumbnail") or r.get("image"),
        "w": r.get("width") or 0, "h": r.get("height") or 0,
        "title": r.get("title", ""), "page": r.get("url") or "",
    } for r in res if r.get("image")]


def is_poster(it, strict):
    w, h = it["w"], it["h"]
    if not w or not h:
        return not strict
    ratio = h / w
    if strict:
        return 1.3 <= ratio <= 1.9 and h >= 400
    return 1.15 <= ratio <= 2.2 and h >= 250


def web_candidates(title, year, english, persian, limit=MAX_OPTIONS):
    queries = []
    if persian:
        queries += [f"{title} پوستر فیلم", f"{title} فیلم"]
        for t, y in english[:2]:
            queries.append(f"{t} {y or year or ''} movie poster".replace("  ", " ").strip())
    else:
        queries.append(f"{title} {year or ''} movie poster".replace("  ", " ").strip())
        queries.append(f"{title} movie poster")
    fetch_n = max(60, limit * 4)
    raw, seen, last_err = [], set(), None
    futs = {SOURCE_POOL.submit(ddg_images, q, fetch_n): q for q in queries[:4]}
    for fut in as_completed(futs, timeout=15):
        try:
            items = fut.result(timeout=1)
        except Exception as e:
            last_err = e
            continue
        for it in items:
            if it["image"] not in seen:
                seen.add(it["image"])
                raw.append(it)
        if len([x for x in raw if is_poster(x, True)]) >= limit * 2:
            break
    if not raw and last_err:
        raise last_err
    good = [x for x in raw if is_poster(x, True)]
    if len(good) < limit:
        chosen_ids = {x["image"] for x in good}
        loose = [x for x in raw if x["image"] not in chosen_ids and is_poster(x, False)]
        good += loose
    out = []
    for it in good[:limit]:
        host = urlparse(it["page"]).netloc.replace("www.", "") if it["page"] else ""
        out.append({
            "id": "web:" + it["image"],
            "title": (it["title"] or host or "image")[:70],
            "year": "", "kind": host,
            "thumb": it["thumb"], "full": it["image"],
            "source": "Web",
        })
    return out


# ----------------------------------------------------------------------------
#  Combine sources
# ----------------------------------------------------------------------------
def find_covers(query_text, opts):
    title, year = parse_name(query_text)
    persian = has_persian(title)
    limit = opts.get("limit", MAX_OPTIONS)
    english, tr_errors = ([], [])
    if persian:
        english, tr_errors = persian_to_english(title)
    else:
        english = [(title, year)]
    futs = {}
    if opts.get("wiki"):
        futs["Wikipedia"] = SOURCE_POOL.submit(
            wiki_candidates, title, year, english if persian else [], persian, limit)
    if opts.get("imdb") and english:
        futs["IMDb"] = SOURCE_POOL.submit(imdb_candidates, english, year, limit)
    if opts.get("web"):
        futs["Web"] = SOURCE_POOL.submit(
            web_candidates, title, year, english if persian else [], persian, limit)
    results, src_errors = {}, {}
    for name, f in futs.items():
        try:
            results[name] = f.result(timeout=20)
        except Exception as e:
            results[name] = []
            src_errors[name] = str(e)[:100]
    order = ["Wikipedia", "IMDb", "Web"] if persian else ["IMDb", "Wikipedia", "Web"]
    cands = merge_round_robin([results.get(n, []) for n in order], limit)
    note_parts = []
    if persian and english:
        note_parts.append(T("Translated: ") + " | ".join(t for t, _ in english[:2]))
    counts = {}
    for c in cands:
        counts[c["source"]] = counts.get(c["source"], 0) + 1
    if counts:
        note_parts.append("  ".join(f"{k} {v}" for k, v in counts.items()))
    note = "\n".join(note_parts)
    if not cands:
        if persian and not english and not results.get("Wikipedia") and not results.get("Web"):
            msg = T("Could not translate this title — type the English name and press Enter")
        else:
            msg = T("No cover found — try editing the title")
        extra = "; ".join(f"{k}: {v}" for k, v in src_errors.items())
        if not extra and tr_errors and persian and not english:
            extra = tr_errors[0][:100]
        if extra:
            msg += f"\n({extra})"
        return [], msg, ""
    return cands, None, note


def find_covers_cached(query_text, opts):
    key = (query_text.strip().lower(), opts["imdb"], opts["wiki"], opts["web"])
    if key in SEARCH_CACHE:
        return SEARCH_CACHE[key]
    res = find_covers(query_text, opts)
    if res[0]:
        SEARCH_CACHE[key] = res
    return res


# ----------------------------------------------------------------------------
#  Drawing helpers
# ----------------------------------------------------------------------------
_TMP = tempfile.mkdtemp(prefix="cyruscover_")


def _ps_resize(src, dst, max_w, max_h):
    s = src.replace("'", "''")
    d = dst.replace("'", "''")
    ps = ("Add-Type -AssemblyName System.Drawing;"
          f"$i=[System.Drawing.Image]::FromFile('{s}');"
          f"$r=[Math]::Min({max_w}/$i.Width,{max_h}/$i.Height);"
          "if($r -gt 1){$r=1};"
          "$nw=[int]($i.Width*$r);$nh=[int]($i.Height*$r);"
          "$b=New-Object System.Drawing.Bitmap $nw,$nh;"
          "$g=[System.Drawing.Graphics]::FromImage($b);"
          "$g.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic;"
          "$g.DrawImage($i,0,0,$nw,$nh);"
          f"$b.Save('{d}',[System.Drawing.Imaging.ImageFormat]::Png);"
          "$g.Dispose();$b.Dispose();$i.Dispose()")
    subprocess.run(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps],
                   creationflags=0x08000000, timeout=40, capture_output=True)
    return os.path.exists(dst) and os.path.getsize(dst) > 0


def prepare_thumb(data, key, max_w=THUMB_SIZE[0], max_h=THUMB_SIZE[1]):
    out = os.path.join(_TMP, "t_" + str(abs(hash(key))) + ".png")
    try:
        if HAVE_PIL:
            im = Image.open(io.BytesIO(data)).convert("RGB")
            im.thumbnail((max_w, max_h))
            im.save(out, "PNG")
            return out
    except Exception:
        pass
    raw = os.path.join(_TMP, "r_" + str(abs(hash(key))))
    try:
        with open(raw, "wb") as fh:
            fh.write(data)
        if os.name == "nt" and _ps_resize(raw, out, max_w, max_h):
            return out
        if data[:8] == b"\x89PNG\r\n\x1a\n" or data[:6] in (b"GIF87a", b"GIF89a"):
            return raw
    except Exception:
        pass
    return None


def rrect(c, x1, y1, x2, y2, r, **kw):
    r = max(1, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
           x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return c.create_polygon(pts, smooth=True, **kw)


def lbl(parent, text="", size=10, bold=False, fg=TEXT, bg=None, **kw):
    anchor = kw.pop("anchor", "w")
    justify = kw.pop("justify", None)
    if LANG == "fa":
        anchor = _FLIP_ANCHOR.get(anchor, anchor)
        justify = justify or ("center" if anchor == "center" else "right")
    return tk.Label(parent, text=text, font=F(size, bold), fg=fg, bg=bg or parent["bg"],
                    anchor=anchor, justify=justify or "left", **kw)


def section_title(parent, text, size=13):
    f = tk.Frame(parent, bg=parent["bg"])
    tk.Frame(f, bg=BRAND_GOLD, width=4, height=18).pack(side="left", padx=(0, 9))
    lbl(f, text, size, True, bg=parent["bg"]).pack(side="left")
    return f


def _ctrl_keys(e):
    """Ctrl+C/V/X/A that work on ANY keyboard layout (e.g. Persian)."""
    w = e.widget
    k = e.keycode
    try:
        if k == 86:
            w.event_generate("<<Paste>>")
        elif k == 67:
            w.event_generate("<<Copy>>")
        elif k == 88:
            w.event_generate("<<Cut>>")
        elif k == 65:
            w.select_range(0, "end")
            w.icursor("end")
        else:
            return None
    except tk.TclError:
        return None
    return "break"


def _entry_menu(e):
    w = e.widget
    try:
        w.focus_set()
        m = tk.Menu(w, tearoff=0, font=F(9))
        m.add_command(label=T("Cut"), command=lambda: w.event_generate("<<Cut>>"))
        m.add_command(label=T("Copy"), command=lambda: w.event_generate("<<Copy>>"))
        m.add_command(label=T("Paste"), command=lambda: w.event_generate("<<Paste>>"))
        m.add_separator()
        m.add_command(label=T("Select all"), command=lambda: (w.select_range(0, "end"), w.icursor("end")))
        m.tk_popup(e.x_root, e.y_root)
    finally:
        try:
            m.grab_release()
        except Exception:
            pass


class REntry(tk.Canvas):
    """Rounded text field. Works with paste on every keyboard layout."""
    PX, PY = 14, 8

    def __init__(self, parent, var, width=30, size=11):
        super().__init__(parent, bg=parent["bg"], highlightthickness=0, bd=0)
        self._focus = False
        self._e = tk.Entry(self, textvariable=var, width=width, bg=FILL, fg=TEXT,
                           insertbackground=BLUE, relief="flat", bd=0, highlightthickness=0,
                           disabledbackground=FILL, disabledforeground=FAINT, font=F(size),
                           justify="right" if LANG == "fa" else "left")
        self._win = self.create_window(self.PX, self.PY, window=self._e, anchor="nw")
        self._cw = self._e.winfo_reqwidth() + 2 * self.PX
        self._ch = self._e.winfo_reqheight() + 2 * self.PY
        tk.Canvas.configure(self, width=self._cw, height=self._ch)
        tk.Canvas.bind(self, "<Configure>", self._cfg)
        self._e.bind("<FocusIn>", lambda ev: self._set_focus(True), add="+")
        self._e.bind("<FocusOut>", lambda ev: self._set_focus(False), add="+")
        self._e.bind("<Control-KeyPress>", _ctrl_keys)
        self._e.bind("<Shift-Insert>", lambda ev: (self._e.event_generate("<<Paste>>"), "break")[1])
        self._e.bind("<Button-3>", _entry_menu)
        tk.Canvas.bind(self, "<Button-1>", lambda ev: self._e.focus_set())

    def _set_focus(self, on):
        self._focus = on
        self._draw()

    def _cfg(self, ev):
        self._cw, self._ch = ev.width, ev.height
        self.itemconfigure(self._win, width=max(10, ev.width - 2 * self.PX),
                           height=max(10, ev.height - 2 * self.PY))
        self._draw()

    def _draw(self):
        self.delete("bg")
        W, H = self._cw, self._ch
        if W < 20 or H < 20:
            return
        rrect(self, 2, 2, W - 2, H - 2, 14, fill=FILL,
              outline=BLUE if self._focus else SEP, width=2, tags="bg")
        self.tag_lower("bg")

    def restyle(self):
        self._e.configure(bg=FILL, fg=TEXT, insertbackground=BLUE,
                          disabledbackground=FILL, disabledforeground=FAINT)
        self._draw()

    def bind(self, seq=None, func=None, add=None):
        return self._e.bind(seq, func, add)

    def get(self):
        return self._e.get()

    def focus_set(self):
        self._e.focus_set()

    def configure(self, cnf=None, **kw):
        if "state" in kw:
            self._e.configure(state=kw.pop("state"))
            self._draw()
        if cnf or kw:
            return tk.Canvas.configure(self, cnf, **kw)
    config = configure


def entry(parent, var, width=30, **kw):
    return REntry(parent, var, width=width)


# ----------------------------------------------------------------------------
#  Embedded logo helpers
# ----------------------------------------------------------------------------
_LOGO_CACHE = {}


def load_logo(max_size=None, tile=False):
    if not LOGO_DATA:
        return None
    key = (max_size, tile)
    if key in _LOGO_CACHE:
        return _LOGO_CACHE[key]
    try:
        if tile and HAVE_PIL:
            im = _logo_tile(max_size[0] if max_size else 64)
            buf = io.BytesIO()
            im.save(buf, "PNG")
            photo = tk.PhotoImage(data=buf.getvalue())
        elif max_size and HAVE_PIL:
            im = Image.open(io.BytesIO(LOGO_DATA)).convert("RGBA")
            im.thumbnail(max_size)
            buf = io.BytesIO()
            im.save(buf, "PNG")
            photo = tk.PhotoImage(data=buf.getvalue())
        else:
            photo = tk.PhotoImage(data=LOGO_DATA)
            if max_size and (photo.width() > max_size[0] or photo.height() > max_size[1]):
                factor = max(1, max(photo.width() // max_size[0],
                                    photo.height() // max_size[1]))
                photo = photo.subsample(factor, factor)
        _LOGO_CACHE[key] = photo
        return photo
    except Exception:
        return None


def _logo_tile(size):
    """White logo on a rounded navy tile, so it is visible on any background."""
    from PIL import ImageDraw
    S = 512
    tile = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(tile).rounded_rectangle((0, 0, S - 1, S - 1), radius=int(S * 0.22),
                                           fill=BRAND_NAVY)
    logo = Image.open(io.BytesIO(LOGO_DATA)).convert("RGBA")
    pad = int(S * 0.14)
    logo = logo.resize((S - 2 * pad, S - 2 * pad), Image.LANCZOS)
    tile.alpha_composite(logo, (pad, pad))
    return tile.resize((size, size), Image.LANCZOS)


def build_icon_file():
    try:
        ico_path = os.path.join(_TMP, "cyruscover.ico")
        with open(ico_path, "wb") as fh:
            fh.write(ICON_DATA)
        return ico_path
    except Exception:
        return None


def force_win_icon(root, ico):
    """Force the icon onto the real window handle (title bar + taskbar + Alt-Tab)."""
    if sys.platform != "win32" or not ico:
        return
    try:
        import ctypes
        from ctypes import wintypes
        u = ctypes.windll.user32
        u.LoadImageW.restype = wintypes.HANDLE
        u.LoadImageW.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR, wintypes.UINT,
                                 ctypes.c_int, ctypes.c_int, wintypes.UINT]
        u.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        root.update_idletasks()
        hwnd = u.GetParent(root.winfo_id()) or root.winfo_id()
        IMAGE_ICON, LR_LOADFROMFILE = 1, 0x10
        big = u.LoadImageW(None, ico, IMAGE_ICON,
                           u.GetSystemMetrics(11), u.GetSystemMetrics(12), LR_LOADFROMFILE)
        small = u.LoadImageW(None, ico, IMAGE_ICON,
                             u.GetSystemMetrics(49), u.GetSystemMetrics(50), LR_LOADFROMFILE)
        WM_SETICON = 0x0080
        if big:
            u.SendMessageW(hwnd, WM_SETICON, 1, big)
        if small:
            u.SendMessageW(hwnd, WM_SETICON, 0, small)
        root._win_icons = (big, small)
    except Exception:
        pass


def _hex(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _mix(c1, c2, t):
    a, b = _hex(c1), _hex(c2)
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


_BANNER_CACHE = {}


def _glow(base, color, cx, cy, size, strength):
    from PIL import Image, ImageChops
    g = Image.radial_gradient("L").resize((size, size), Image.BILINEAR)
    g = g.point(lambda v: int(255 * strength * (max(0.0, (176 - v) / 176.0) ** 1.6)))
    base.paste(Image.new("RGB", (size, size), color), (int(cx - size / 2), int(cy - size / 2)), g)


def _perforations(W, H, step=26):
    from PIL import Image, ImageDraw
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    x = 10
    while x < W - 10:
        d.rounded_rectangle((x, 8, x + 10, 15), radius=2, fill=(255, 255, 255, 24))
        d.rounded_rectangle((x, H - 16, x + 10, H - 9), radius=2, fill=(255, 255, 255, 24))
        x += step
    return ov


def _round_mask(W, H, r, S=3):
    from PIL import Image, ImageDraw
    m = Image.new("L", (W * S, H * S), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, W * S - 1, H * S - 1), radius=r * S, fill=255)
    return m.resize((W, H), Image.LANCZOS)


def _banner_base(W, H, r):
    from PIL import Image, ImageChops
    grad = Image.linear_gradient("L").rotate(90, expand=True).resize((W, H), Image.BILINEAR)
    base = Image.composite(Image.new("RGB", (W, H), _hex("#2B4685")),
                           Image.new("RGB", (W, H), _hex("#0B1530")), grad)
    _glow(base, _hex("#E0B94A"), H * 0.55, H * 0.5, int(H * 3.2), 0.34)
    _glow(base, _hex("#6C7BFF"), W - H * 0.8, H * 0.2, int(H * 3.6), 0.30)
    out = base.convert("RGBA")
    out.alpha_composite(_perforations(W, H))
    out.putalpha(_round_mask(W, H, r))
    return out


def make_banner_png(W, H, r=22, flip=False):
    key = (W, H, flip)
    if key in _BANNER_CACHE:
        return _BANNER_CACHE[key]
    import io
    buf = io.BytesIO()
    img = _banner_base(W, H, r)
    if flip:
        from PIL import Image
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    img.save(buf, "PNG")
    if len(_BANNER_CACHE) > 6:
        _BANNER_CACHE.clear()
    _BANNER_CACHE[key] = buf.getvalue()
    return _BANNER_CACHE[key]


def make_about_header_png(W, H, avatar_png, r=20, d=112):
    import io
    from PIL import Image, ImageDraw
    out = _banner_base(W, H, r)
    S = 4
    ring = Image.new("RGBA", ((d + 28) * S, (d + 28) * S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(ring)
    n = (d + 28) * S
    dr.ellipse((0, 0, n - 1, n - 1), fill=(224, 185, 74, 60))
    dr.ellipse((8 * S, 8 * S, n - 8 * S - 1, n - 8 * S - 1), fill=(224, 185, 74, 255))
    dr.ellipse((13 * S, 13 * S, n - 13 * S - 1, n - 13 * S - 1), fill=(12, 21, 48, 255))
    ring = ring.resize((d + 28, d + 28), Image.LANCZOS)
    av = Image.open(io.BytesIO(avatar_png)).convert("RGBA").resize((d, d), Image.LANCZOS)
    ring.alpha_composite(av, (14, 14))
    out.alpha_composite(ring, ((W - d - 28) // 2, (H - d - 28) // 2))
    buf = io.BytesIO()
    out.save(buf, "PNG")
    return buf.getvalue()


class Card(tk.Canvas):
    def __init__(self, parent, r=22, pad=16, bg=CARD, shadow=True, accent=None, stretch=False):
        super().__init__(parent, bg=parent["bg"], highlightthickness=0, height=40, width=40)
        self.r, self.pad, self.cbg, self.shadow, self.m = r, pad, bg, shadow, 5
        self.accent = accent
        self.stretch = stretch
        self._W = self._H = 0
        self.body = tk.Frame(self, bg=bg)
        self.win = self.create_window(0, 0, window=self.body, anchor="nw")
        self.bind("<Configure>", self._cfg)
        self.body.bind("<Configure>", self._bcfg)

    def _bcfg(self, e=None):
        k = self.pad + self.m
        h = self.body.winfo_reqheight() + 2 * k
        w = self.body.winfo_reqwidth() + 2 * k
        if int(float(self["height"])) != h:
            self.configure(height=h)
        if int(float(self["width"])) != w:
            self.configure(width=w)

    def _cfg(self, e):
        self._W, self._H = e.width, e.height
        self._draw()

    def _draw(self):
        self.delete("bg")
        W, H, m = self._W, self._H, self.m
        if W < 20 or H < 20:
            return
        light = self.cbg in ("#FEFEFE", "#FFFFFF")
        if self.shadow:
            sb = "#7F88A3" if light else "#03060C"
            for dy, t in ((5, .07), (4, .12), (3, .18), (2, .25)):
                rrect(self, m, m + dy, W - m, H - m + dy, self.r,
                      fill=_mix(self["bg"], sb, t), outline="", tags="bg")
        rrect(self, m, m, W - m, H - m, self.r, fill=self.cbg, outline="", tags="bg")
        if self.accent:
            ax = (W - m - 7) if LANG == "fa" else (m + 2)
            rrect(self, ax, m + self.r * 0.7, ax + 5, H - m - self.r * 0.7, 3,
                  fill=self.accent, outline="", tags="bg")
        self.tag_lower("bg")
        k = self.pad + m
        self.coords(self.win, k, k)
        self.itemconfigure(self.win, width=max(10, W - 2 * k))
        if self.stretch:
            self.itemconfigure(self.win, height=max(10, H - 2 * k))


# ----------------------------------------------------------------------------
#  Vector icons
# ----------------------------------------------------------------------------
class IconPath:
    ICONS = {
        "search": [("oval", 4, 4, 16, 16), ("line", 16.5, 16.5, 21, 21)],
        "save": [("poly", [(3, 3), (17, 3), (21, 7), (21, 21), (3, 21)]),
                 ("rect", 7, 3, 17, 8), ("rect", 7, 13, 17, 21)],
        "folder": [("poly", [(3, 5), (9, 5), (11, 7), (21, 7), (21, 19), (3, 19)])],
        "plus": [("line", 12, 4, 12, 20), ("line", 4, 12, 20, 12)],
        "open": [("poly", [(10, 4), (20, 4), (20, 14)]),
                 ("poly", [(20, 4), (10, 14)]),
                 ("poly", [(4, 8), (4, 20), (16, 20), (16, 14)])],
        "trash": [("line", 4, 7, 20, 7), ("poly", [(6, 7), (6, 21), (18, 21), (18, 7)]),
                  ("line", 9, 7, 9, 4), ("line", 15, 7, 15, 4),
                  ("line", 9, 4, 15, 4), ("line", 10, 11, 10, 18), ("line", 14, 11, 14, 18)],
        "filter": [("poly", [(3, 4), (21, 4), (14, 13), (14, 21), (10, 19), (10, 13)])],
        "star": [("poly", [(12, 3), (14.5, 9), (21, 9.5), (16, 14), (17.5, 21),
                           (12, 17.5), (6.5, 21), (8, 14), (3, 9.5), (9.5, 9)])],
        "moon": [("arc", 4, 3, 21, 21, 70, 230)],
        "sun": [("oval", 9, 9, 15, 15),
                ("line", 12, 2, 12, 4), ("line", 12, 20, 12, 22),
                ("line", 2, 12, 4, 12), ("line", 20, 12, 22, 12),
                ("line", 5, 5, 6.5, 6.5), ("line", 17.5, 17.5, 19, 19),
                ("line", 5, 19, 6.5, 17.5), ("line", 17.5, 6.5, 19, 5)],
        "info": [("oval", 3, 3, 21, 21), ("line", 12, 11, 12, 17),
                 ("circle", 12, 7.5, 1.1)],
        "check": [("poly", [(4, 12), (9, 17), (20, 6)])],
        "x": [("line", 6, 6, 18, 18), ("line", 18, 6, 6, 18)],
        "skip": [("line", 5, 5, 19, 19), ("line", 19, 5, 5, 19)],
        "sparkle": [("poly", [(12, 3), (13.5, 10.5), (21, 12), (13.5, 13.5),
                              (12, 21), (10.5, 13.5), (3, 12), (10.5, 10.5)])],
        "shield": [("poly", [(12, 3), (20, 6), (20, 13), (12, 21), (4, 13), (4, 6)]),
                   ("poly", [(9, 12), (11.5, 14.5), (16, 9.5)])],
        "film": [("rect", 3, 4, 21, 20),
                 ("line", 7, 4, 7, 20), ("line", 17, 4, 17, 20),
                 ("line", 3, 8, 7, 8), ("line", 3, 12, 7, 12), ("line", 3, 16, 7, 16),
                 ("line", 17, 8, 21, 8), ("line", 17, 12, 21, 12), ("line", 17, 16, 21, 16)],
        "mail": [("rect", 3, 6, 21, 18), ("line", 3, 7, 12, 14), ("line", 21, 7, 12, 14)],
        "copy": [("rect", 9, 9, 20, 20), ("line", 5, 15, 5, 5), ("line", 5, 5, 15, 5)],
        "globe": [("oval", 3, 3, 21, 21), ("line", 3, 12, 21, 12), ("oval", 8, 3, 16, 21)],
        "crown": [("poly", [(3, 18), (5, 8), (9, 12), (12, 6), (15, 12), (19, 8), (21, 18)]),
                  ("line", 3, 18, 21, 18)],
    }


def draw_icon(canvas, name, x, y, size, color, width=1.8, tags="icon"):
    ops = IconPath.ICONS.get(name)
    if not ops:
        return
    s = size / 24.0
    def T(px, py):
        return x + (px - 12) * s, y + (py - 12) * s
    for op in ops:
        kind = op[0]
        if kind == "line":
            x1, y1 = T(op[1], op[2]); x2, y2 = T(op[3], op[4])
            canvas.create_line(x1, y1, x2, y2, fill=color, width=width,
                               capstyle="round", tags=tags)
        elif kind == "rect":
            x1, y1 = T(op[1], op[2]); x2, y2 = T(op[3], op[4])
            canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=width,
                                    fill="", tags=tags)
        elif kind == "circle":
            cx, cy = T(op[1], op[2]); r = op[3] * s
            canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=color,
                               outline="", tags=tags)
        elif kind == "oval":
            x1, y1 = T(op[1], op[2]); x2, y2 = T(op[3], op[4])
            canvas.create_oval(x1, y1, x2, y2, outline=color, width=width,
                               fill="", tags=tags)
        elif kind == "poly":
            coords = []
            for px, py in op[1]:
                coords.extend(T(px, py))
            canvas.create_polygon(coords, outline=color, width=width, fill="",
                                  joinstyle="round", tags=tags)
        elif kind == "arc":
            x1, y1 = T(op[1], op[2]); x2, y2 = T(op[3], op[4])
            canvas.create_arc(x1, y1, x2, y2, start=op[5], extent=op[6],
                              style="arc", outline=color, width=width, tags=tags)


class Btn(tk.Canvas):
    STY = {
        "primary":    ("#0A84FF", "#0A6CE0", "#FFFFFF", "#FFFFFF"),
        "success":    ("#30D158", "#24A847", "#FFFFFF", "#FFFFFF"),
        "danger":     ("#FF453A", "#D93A30", "#FFFFFF", "#FFFFFF"),
        "warning":    ("#FF9F0A", "#E08800", "#FFFFFF", "#FFFFFF"),
        "purple":     ("#7B4DFF", "#6B3DEF", "#FFFFFF", "#FFFFFF"),
        "teal":       ("#00C7BE", "#00A89F", "#FFFFFF", "#FFFFFF"),
        "indigo":     ("#5856D6", "#4846C6", "#FFFFFF", "#FFFFFF"),
        "pink":       ("#FF375F", "#E02A50", "#FFFFFF", "#FFFFFF"),
        "dark":       ("#1C1C1E", "#3A3A3C", "#FFFFFF", "#FFFFFF"),
        "gold":       (BRAND_GOLD, "#B08D1E", "#FFFFFF", "#FFFFFF"),
        "navy":       (BRAND_NAVY, BRAND_NAVY_SOFT, "#FFFFFF", "#FFFFFF"),
        "tint":       ("#DCEBFF", "#C9DEFF", "#0A84FF", "#0A84FF"),
        "tint-green": ("#E4F8EA", "#CFF0D9", "#1F9D45", "#1F9D45"),
        "tint-red":   ("#FFE9E7", "#FFD8D4", "#FF453A", "#FF453A"),
        "tint-purple":("#EFE4FF", "#E0CEFF", "#7B4DFF", "#7B4DFF"),
        "tint-amber": ("#FFF4DE", "#FFE8B8", "#C77700", "#C77700"),
        "tint-teal":  ("#DFF7F5", "#C6EFEB", "#00968E", "#00968E"),
        "tint-gold":  ("#FAF0D2", "#F1E2B0", "#8B6E11", "#8B6E11"),
        "plain":      ("#E9E9EF", "#D8D8DE", "#000000", "#6E6E73"),
    }

    def __init__(self, parent, text, cmd=None, style="plain", size=10, px=16, py=7,
                 icon=None, icon_size=14, gap=7):
        self.cmd, self.text, self.enabled, self.style = cmd, text, True, style
        self.icon, self.icon_size, self.gap = icon, icon_size, gap
        self._f = F(size, style in ("primary", "dark", "success", "danger",
                                    "warning", "purple", "teal", "indigo", "pink",
                                    "gold", "navy"))
        tf = tkfont.Font(font=self._f)
        icon_w = (icon_size + gap) if icon else 0
        self._W = tf.measure(text) + 2 * px + icon_w
        self._H = tf.metrics("linespace") + 2 * py
        super().__init__(parent, width=self._W, height=self._H, highlightthickness=0,
                         bg=parent["bg"], cursor="hand2")
        self._hover = False
        self.set_style(style)
        self.bind("<Enter>", self._enter)
        self.bind("<Leave>", self._leave)
        self.bind("<ButtonRelease-1>", self._click)

    def _enter(self, e):
        self._hover = True
        if self.enabled:
            self._paint(self._hv)

    def _leave(self, e):
        self._hover = False
        if self.enabled:
            self._paint(self._bg)

    def set_icon(self, icon):
        self.icon = icon
        self._paint(self._hv if self._hover and self.enabled else self._bg)

    def set_style(self, style):
        self.style = style
        self._bg, self._hv, self._fg, self._icon_fg = self.STY[style]
        self._paint(self._hv if self._hover and self.enabled else self._bg)

    def set_enabled(self, on):
        self.enabled = on
        self._paint(self._bg if on else "#E5E5EA")
        self.configure(cursor="hand2" if on else "arrow")

    def set_text(self, text):
        self.text = text
        tf = tkfont.Font(font=self._f)
        icon_w = (self.icon_size + self.gap) if self.icon else 0
        self._W = tf.measure(text) + 32 + icon_w
        self.configure(width=self._W)
        self._paint(self._hv if self._hover and self.enabled else self._bg)

    def _paint(self, col):
        self.delete("all")
        radius = self._H / 2
        rrect(self, 0, 0, self._W, self._H, radius, fill=col, outline="")
        fg = self._fg if self.enabled else FAINT
        icon_col = self._icon_fg if self.enabled else FAINT
        tf = tkfont.Font(font=self._f)
        text_w = tf.measure(self.text)
        icon_w = (self.icon_size + self.gap) if self.icon else 0
        total_w = text_w + icon_w
        start_x = (self._W - total_w) / 2
        cy = self._H / 2
        if self.icon and LANG == "fa":
            text_x = start_x
            draw_icon(self, self.icon, start_x + text_w + self.gap + self.icon_size / 2, cy,
                      self.icon_size, icon_col, width=1.9, tags="ic")
        elif self.icon:
            draw_icon(self, self.icon, start_x + self.icon_size / 2, cy,
                      self.icon_size, icon_col, width=1.9, tags="ic")
            text_x = start_x + self.icon_size + self.gap
        else:
            text_x = start_x
        self.create_text(text_x, cy, text=self.text, font=self._f,
                         fill=fg, anchor="w")

    def _click(self, e):
        if self.enabled and self.cmd and 0 <= e.x <= self._W and 0 <= e.y <= self._H:
            self.cmd()


class Switch(tk.Canvas):
    """Settings row: label on one side, animated pill toggle on the other."""

    def __init__(self, parent, text, value=False, cmd=None, size=10):
        self.on, self.cmd, self.text = bool(value), cmd, text
        self._f = F(size)
        self._tf = tkfont.Font(font=self._f)
        self._tw = self._tf.measure(text)
        self._sw, self._sh = 46, 26
        self._h = 42
        self._pos = 1.0 if self.on else 0.0
        self._anim = None
        self._hover = False
        super().__init__(parent, width=self._tw + self._sw + 28, height=self._h,
                         bg=parent["bg"], highlightthickness=0, cursor="hand2", bd=0)
        self.bind("<Button-1>", self.toggle)
        self.bind("<Enter>", self._hover_on)
        self.bind("<Leave>", self._hover_off)
        self.bind("<Configure>", lambda e: self._draw())
        self._draw()

    def get(self):
        return self.on

    def toggle(self, e=None):
        self.on = not self.on
        self._step()
        if self.cmd:
            self.cmd(self.on)

    def _step(self):
        if self._anim:
            try:
                self.after_cancel(self._anim)
            except Exception:
                pass
            self._anim = None
        target = 1.0 if self.on else 0.0
        if abs(self._pos - target) < 0.04:
            self._pos = target
            self._draw()
            return
        self._pos += (target - self._pos) * 0.45
        self._draw()
        try:
            self._anim = self.after(15, self._step)
        except Exception:
            self._anim = None

    def _hover_on(self, _e=None):
        self._hover = True
        self._draw()

    def _hover_off(self, _e=None):
        self._hover = False
        self._draw()

    def _draw(self):
        self.delete("all")
        W = max(self.winfo_width(), self._tw + self._sw + 28)
        H = self._h
        rtl = LANG == "fa"
        if rtl:
            self.create_text(W - 2, H / 2, text=self.text, font=self._f, fill=TEXT, anchor="e")
            x0 = 3
        else:
            self.create_text(2, H / 2, text=self.text, font=self._f, fill=TEXT, anchor="w")
            x0 = W - self._sw - 3
        y0 = (H - self._sh) / 2
        x1, y1 = x0 + self._sw, y0 + self._sh
        off = FILL2 if not self._hover else _mix(FILL2, "#000000", .08)
        on = BRAND_GOLD if not self._hover else BRAND_GOLD_LIGHT
        track = _mix(off, on, self._pos)
        rrect(self, x0 - 1, y0 - 1, x1 + 1, y1 + 1, self._sh / 2 + 1,
              fill=_mix(track, "#000000", .12), outline="")
        rrect(self, x0, y0, x1, y1, self._sh / 2, fill=track, outline="")
        kr = (self._sh - 6) / 2
        pad = 3 + kr
        cx = x0 + pad + (self._sw - 2 * pad) * self._pos
        cy = H / 2
        self.create_oval(cx - kr, cy - kr + 1.6, cx + kr, cy + kr + 1.6,
                         fill=_mix(track, "#000000", .28), outline="")
        self.create_oval(cx - kr, cy - kr, cx + kr, cy + kr, fill="#FFFFFF", outline="")


class RScroll(tk.Canvas):
    def __init__(self, parent, command, bg=CARD, w=10):
        super().__init__(parent, width=w, bg=bg, highlightthickness=0)
        self.command, self.lo, self.hi, self._off = command, 0.0, 1.0, 0
        self.bind("<Configure>", lambda e: self._draw())
        self.bind("<ButtonPress-1>", self._press)
        self.bind("<B1-Motion>", self._move)

    def set(self, lo, hi):
        self.lo, self.hi = float(lo), float(hi)
        self._draw()

    def _geom(self):
        H = self.winfo_height()
        ln = max(28, H * (self.hi - self.lo))
        y1 = H * self.lo
        if y1 + ln > H:
            y1 = H - ln
        return H, y1, y1 + ln

    def _draw(self):
        self.delete("all")
        W = self.winfo_width()
        if self.hi - self.lo >= 0.999 or self.winfo_height() < 20 or W < 4:
            return
        H, y1, y2 = self._geom()
        rrect(self, 2, y1 + 2, W - 2, y2 - 2, (W - 4) / 2, fill="#C7C7CC", outline="")

    def _press(self, e):
        H, y1, y2 = self._geom()
        self._off = e.y - y1 if y1 <= e.y <= y2 else (y2 - y1) / 2
        self._move(e)

    def _move(self, e):
        H = max(self.winfo_height(), 1)
        self.command("moveto", max(0.0, (e.y - self._off) / H))


class FlatBox(tk.Frame):
    """Same API as ScrollBox but does not scroll by itself: the whole page scrolls."""

    def __init__(self, parent, bg=BG):
        super().__init__(parent, bg=bg)
        self.canvas = self
        self.vsb = tk.Frame(self, bg=bg)
        self.inner = tk.Frame(self, bg=bg)
        self.inner.pack(fill="x")

    def wheel(self, delta):
        pass


class SideScroll(tk.Frame):
    """Scrollable column. Fills the window height (content sticks to the bottom);
    scrolls when the window is too short. Optional height limit for narrow layouts."""

    def __init__(self, parent, bg=BG):
        super().__init__(parent, bg=bg)
        self.limit = None
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0, height=1)
        self.vsb = RScroll(self, self.canvas.yview, bg)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self.win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.bind("<Configure>", self._fit)
        self.inner.bind("<Configure>", self._fit)
        self._last_req = -1
        self.after(150, self._poll)

    def _poll(self):
        try:
            req = self.inner.winfo_reqheight()
            if req != self._last_req:
                self._last_req = req
                self._fit()
            self.after(120, self._poll)
        except tk.TclError:
            pass

    def set_limit(self, limit):
        if limit != self.limit:
            self.limit = limit
            self._fit()

    def _fit(self, e=None):
        try:
            W = self.canvas.winfo_width()
            req = self.inner.winfo_reqheight()
            if self.limit:
                want = max(80, min(req, self.limit))
                if int(float(self.canvas["height"])) != want:
                    self.canvas.configure(height=want)
                H = want
            else:
                if int(float(self.canvas["height"])) != 1:
                    self.canvas.configure(height=1)
                H = self.canvas.winfo_height()
            h = max(H, req)
            self.canvas.itemconfigure(self.win, width=max(W, 10), height=h)
            self.canvas.configure(scrollregion=(0, 0, max(W, 10), h))
        except tk.TclError:
            pass

    def wheel(self, delta):
        if self.inner.winfo_reqheight() > self.canvas.winfo_height():
            self.canvas.yview_scroll(int(-delta / 120), "units")


class FlowFrame(tk.Frame):
    def __init__(self, parent, bg=CARD, gx=10, gy=10):
        super().__init__(parent, bg=bg)
        self.items, self.gx, self.gy = [], gx, gy
        self._layout_pending = False
        self.bind("<Configure>", self._schedule_layout)

    def add(self, w):
        self.items.append(w)
        self._schedule_layout()

    def clear(self):
        for w in self.items:
            w.destroy()
        self.items = []
        self.configure(height=1)

    def _schedule_layout(self, e=None):
        if self._layout_pending:
            return
        self._layout_pending = True
        self.after_idle(self._layout)

    def _layout(self, e=None):
        self._layout_pending = False
        W = self.winfo_width()
        if W <= 1:
            return
        x = y = rowh = 0
        for w in self.items:
            try:
                ww, wh = w.winfo_reqwidth(), w.winfo_reqheight()
                if x > 0 and x + ww > W:
                    x, y, rowh = 0, y + rowh + self.gy, 0
                w.place(x=(W - x - ww) if LANG == "fa" else x, y=y)
                x += ww + self.gx
                rowh = max(rowh, wh)
            except tk.TclError:
                pass
        new_h = max(1, y + rowh)
        if int(float(self["height"])) != new_h:
            self.configure(height=new_h)


class ScrollBox(tk.Frame):
    def __init__(self, parent, bg=BG):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.vsb = RScroll(self, self.canvas.yview, bg)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self.win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>",
                        lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfigure(self.win, width=e.width))

    def wheel(self, delta):
        if self.inner.winfo_reqheight() > self.canvas.winfo_height():
            self.canvas.yview_scroll(int(-delta / 120), "units")


class RProgress(tk.Canvas):
    def __init__(self, parent, h=6):
        super().__init__(parent, height=h, bg=BG, highlightthickness=0)
        self.maximum, self.value, self._h = 1, 0, h
        self.bind("<Configure>", lambda e: self._draw())

    def set(self, value, maximum=None):
        if maximum is not None:
            self.maximum = max(1, maximum)
        self.value = value
        self._draw()

    def _draw(self):
        self.delete("all")
        W, H = self.winfo_width(), self._h
        if W < 10:
            return
        rrect(self, 0, 0, W, H, H / 2, fill=FILL2, outline="")
        fw = W * min(1.0, self.value / self.maximum)
        if fw > H:
            if LANG == "fa":
                rrect(self, W - fw, 0, W, H, H / 2, fill=BRAND_GOLD, outline="")
            else:
                rrect(self, 0, 0, fw, H, H / 2, fill=BRAND_GOLD, outline="")


class Dlg(tk.Toplevel):
    def __init__(self, app, title):
        super().__init__(app.root)
        self.app = app
        self.title(title)
        self.configure(bg=BG)
        self.transient(app.root)
        self.card = Card(self, pad=20)
        self.card.pack(fill="both", expand=True, padx=12, pady=12)
        self.body = self.card.body

    def finish(self):
        self.update_idletasks()
        r = self.app.root
        c = self.card
        k = c.pad + c.m
        cw = c.body.winfo_reqwidth() + 2 * k
        ch = c.body.winfo_reqheight() + 2 * k
        c.configure(width=cw, height=ch)
        w = max(cw, 440) + 24
        h = ch + 24
        x = r.winfo_rootx() + (r.winfo_width() - w) // 2
        y = r.winfo_rooty() + (r.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{max(x, 0)}+{max(y, 0)}")
        try:
            self.grab_set()
        except Exception:
            pass


def info(app, text):
    d = Dlg(app, APP_NAME)
    lbl(d.body, text, 10, wraplength=400).pack(anchor="w", pady=(0, 16))
    Btn(d.body, T("OK"), d.destroy, "gold", icon="check").pack(anchor="e")
    d.finish()
    app.root.wait_window(d)


def existing_cover(movie_path, folder=None):
    stem = os.path.splitext(os.path.basename(movie_path))[0]
    folder = folder or os.path.dirname(movie_path)
    for ext in COVER_EXTS:
        p = os.path.join(folder, stem + ext)
        if os.path.exists(p):
            return p
    return None


def find_folder_cover(folder):
    for name in ("folder", "poster", "cover", "fanart"):
        for ext in COVER_EXTS:
            p = os.path.join(folder, name + ext)
            if os.path.exists(p):
                return p
    base = os.path.basename(folder).lower()
    try:
        for n in os.listdir(folder):
            stem, ext = os.path.splitext(n)
            if ext.lower() in COVER_EXTS and stem.lower() == base:
                return os.path.join(folder, n)
    except OSError:
        pass
    return None


# ============================================================================
#  App
# ============================================================================
class App:
    def __init__(self, root):
        self.root = root
        root.title(f"{APP_NAME} — {APP_TAGLINE}")
        root.configure(bg=BG)

        self._go_fullscreen_on_start()

        self._window_icon = None
        self._set_window_icon()
        self._ico_path = build_icon_file()
        for ms in (50, 400, 1200):
            self.root.after(ms, lambda: force_win_icon(self.root, self._ico_path))

        self.cfg = load_config()
        set_lang(self.cfg.get("lang", "en"))
        apply_font(root)
        root.title(f"{APP_NAME} — {T(APP_TAGLINE)}")
        TR_CACHE.update(self.cfg.get("tr_cache", {}))
        self.output_folder = tk.StringVar(value=self.cfg["output_folder"])
        self.rows = []
        self.busy = False
        self.last_dest = None
        self.theme = self.cfg.get("theme", "light")
        self.apply_palette(self.theme, initial=True)

        self._narrow = False
        self.build_ui()

        root.bind_all("<MouseWheel>", self._on_wheel)
        root.bind("<Configure>", self._on_root_resize, add="+")
        root.protocol("WM_DELETE_WINDOW", self.close)

        self.root.after(60, self._apply_responsive)
        self.root.after(800, self._ensure_font)

    def _go_fullscreen_on_start(self):
        try:
            self.root.state("zoomed")
        except tk.TclError:
            try:
                sw = self.root.winfo_screenwidth()
                sh = self.root.winfo_screenheight()
                self.root.geometry(f"{sw}x{sh}+0+0")
            except Exception:
                pass

    def _set_window_icon(self):
        ico = build_icon_file()
        photo = None
        try:
            if HAVE_PIL and LOGO_DATA:
                buf = io.BytesIO()
                _logo_tile(256).save(buf, "PNG")
                photo = tk.PhotoImage(data=buf.getvalue())
                self._window_icon = photo
        except Exception:
            photo = None
        if ico and os.path.exists(ico):
            try:
                self.root.iconbitmap(default=ico)
                self.root.iconbitmap(ico)
            except Exception:
                pass
        if photo:
            try:
                self.root.iconphoto(True, photo)
            except Exception:
                pass

    def close(self):
        self.cfg.update({
            "output_folder": self.output_folder.get(),
            "src_imdb": self.sw_imdb.get(), "src_wiki": self.sw_wiki.get(), "src_web": self.sw_web.get(),
            "save_next": self.sw_next.get(), "subfolders": self.sw_sub.get(),
            "overwrite": self.sw_over.get(),
            "include_folders": self.sw_folders.get(),
            "tr_cache": dict(list(TR_CACHE.items())[-300:]),
            "theme": self.theme,
            "lang": LANG,
        })
        save_config(self.cfg)
        self.root.destroy()

    def _on_wheel(self, e):
        sc = getattr(self, "scroll", None)
        if sc is not None and sc.inner.winfo_reqheight() > sc.canvas.winfo_height():
            sc.wheel(e.delta)
        else:
            self.page.wheel(e.delta)

    def _on_root_resize(self, e):
        if e.widget is not self.root:
            return
        self._apply_responsive()

    def _apply_responsive(self):
        try:
            W = self.root.winfo_width()
            H = self.root.winfo_height()
        except tk.TclError:
            return
        narrow = W < NARROW_WIDTH
        changed = narrow != self._narrow
        self._narrow = narrow
        if changed:
            self._place_side()
            if hasattr(self, "header_canvas"):
                self.root.after_idle(self._paint_header_banner)
            for row in self.rows:
                try:
                    row["posters"]._schedule_layout()
                except Exception:
                    pass

    def apply_palette(self, theme, initial=False):
        global BG, CARD, SEP, FILL, FILL2, TEXT, MUTED, FAINT, BLUE, BLUE_BG, GREEN, GREEN_T, RED, DANGER_BG, OK_BG
        pal = DARK_THEME if theme == "dark" else LIGHT_THEME
        globals().update(pal)
        self.theme = theme
        Btn.STY = {
            "primary":    (BLUE, "#0869D8" if theme == "dark" else "#0A6CE0", "#FFFFFF", "#FFFFFF"),
            "success":    (GREEN, "#24A847", "#FFFFFF", "#FFFFFF"),
            "danger":     (RED, "#D93A30", "#FFFFFF", "#FFFFFF"),
            "warning":    ("#FF9F0A", "#E08800", "#FFFFFF", "#FFFFFF"),
            "purple":     ("#7B4DFF", "#6B3DEF", "#FFFFFF", "#FFFFFF"),
            "teal":       ("#00C7BE", "#00A89F", "#FFFFFF", "#FFFFFF"),
            "indigo":     ("#5856D6", "#4846C6", "#FFFFFF", "#FFFFFF"),
            "pink":       ("#FF375F", "#E02A50", "#FFFFFF", "#FFFFFF"),
            "dark":       ("#E5E5EA" if theme == "dark" else "#1C1C1E",
                           "#D1D1D6" if theme == "dark" else "#3A3A3C",
                           "#17171A" if theme == "dark" else "#FFFFFF",
                           "#17171A" if theme == "dark" else "#FFFFFF"),
            "gold":       (BRAND_GOLD_LIGHT if theme == "dark" else BRAND_GOLD,
                           "#9A7C15" if theme == "dark" else "#B08D1E",
                           "#0E1524" if theme == "dark" else "#FFFFFF",
                           "#0E1524" if theme == "dark" else "#FFFFFF"),
            "navy":       (BRAND_NAVY_SOFT if theme == "dark" else BRAND_NAVY,
                           "#3A4E80" if theme == "dark" else BRAND_NAVY_SOFT,
                           "#FFFFFF", "#FFFFFF"),
            "tint":       (BLUE_BG, FILL2, BLUE, BLUE),
            "tint-green": (OK_BG, FILL2, GREEN_T, GREEN_T),
            "tint-red":   (DANGER_BG, FILL2, RED, RED),
            "tint-purple":("#EFE4FF" if theme == "light" else "#3A2C5E",
                           FILL2, "#7B4DFF" if theme == "light" else "#B69CFF",
                           "#7B4DFF" if theme == "light" else "#B69CFF"),
            "tint-amber": ("#FFF4DE" if theme == "light" else "#4A3A1E",
                           FILL2, "#C77700" if theme == "light" else "#FFC46B",
                           "#C77700" if theme == "light" else "#FFC46B"),
            "tint-teal":  ("#DFF7F5" if theme == "light" else "#1F4442",
                           FILL2, "#00968E" if theme == "light" else "#5DD8D1",
                           "#00968E" if theme == "light" else "#5DD8D1"),
            "tint-gold":  ("#FAF0D2" if theme == "light" else "#3F3418",
                           FILL2, "#8B6E11" if theme == "light" else "#F1D77A",
                           "#8B6E11" if theme == "light" else "#F1D77A"),
            "plain":      (FILL, FILL2, TEXT, MUTED),
        }

    def toggle_theme(self):
        old_pal = {k: globals()[k] for k in
                   ("BG", "CARD", "SEP", "FILL", "FILL2", "TEXT", "MUTED", "FAINT",
                    "BLUE", "BLUE_BG", "GREEN", "GREEN_T", "RED", "DANGER_BG", "OK_BG")}
        new_theme = "dark" if self.theme == "light" else "light"
        self.apply_palette(new_theme)
        new_pal = {k: globals()[k] for k in old_pal}
        mapping = {old_pal[k]: new_pal[k] for k in old_pal}

        def repaint(w):
            try:
                if isinstance(w, Card):
                    w.cbg = CARD
                    w.configure(bg=w.master["bg"])
                    w.body.configure(bg=CARD)
                    w._draw()
                elif isinstance(w, Btn):
                    w.configure(bg=w.master["bg"])
                    w.set_style(w.style)
                elif isinstance(w, Switch):
                    w.configure(bg=w.master["bg"])
                    w._draw()
                elif isinstance(w, RProgress):
                    w.configure(bg=BG)
                    w._draw()
                elif isinstance(w, REntry):
                    w.configure(bg=w.master["bg"])
                    w.restyle()
                elif isinstance(w, tk.Canvas):
                    cur = w.cget("bg")
                    if cur in mapping:
                        w.configure(bg=mapping[cur])
                else:
                    opts = w.configure()
                    for opt in ("bg", "background", "fg", "foreground", "insertbackground",
                                "highlightbackground", "highlightcolor",
                                "disabledbackground", "disabledforeground"):
                        if opt in opts:
                            val = w.cget(opt)
                            if val in mapping:
                                w.configure(**{opt: mapping[val]})
            except (tk.TclError, KeyError):
                pass
            for c in w.winfo_children():
                repaint(c)
        repaint(self.root)

        for row in self.rows:
            for td in row.get("tiles", []):
                td["bg"] = CARD
                td["frame"].configure(bg=CARD)
                for lab in td["labels"]:
                    lab.configure(bg=CARD, fg=TEXT if lab is td["labels"][0] else FAINT)
                td["img"].configure(bg=CARD if td["loaded"] else FILL)
            if row.get("cands"):
                self.refresh(row)
            try:
                row["status"].configure(bg=CARD, fg=MUTED if row["cands"] else RED)
            except tk.TclError:
                pass
        if hasattr(self, "scroll"):
            self.scroll.canvas.configure(bg=BG)
            self.scroll.inner.configure(bg=BG)
            self.scroll.vsb.configure(bg=BG)
        if hasattr(self, "theme_btn"):
            self.theme_btn.set_icon("moon" if new_theme == "light" else "sun")
            self.theme_btn.set_text(T("Dark mode") if new_theme == "light" else T("Light mode"))
            self.theme_btn.set_style("tint")
        if hasattr(self, "header_canvas"):
            self.header_canvas.configure(bg=BG)
            self._paint_header_banner()
        if not self.rows:
            self.clear_rows(keep_status=True)
        self.cfg["theme"] = new_theme

    def _ensure_font(self):
        """If Vazirmatn is missing, fetch it in the background and refresh the UI when ready."""
        if LANG != "fa" or getattr(self, "_vazir_failed", False) or vazir_present():
            return
        if getattr(self, "_font_thread", None):
            return

        def work():
            ok = download_vazir()
            try:
                self.root.after(0, lambda: self._font_ready(ok))
            except Exception:
                pass
        self._font_thread = threading.Thread(target=work, daemon=True)
        self._font_thread.start()

    def _font_ready(self, ok):
        self._font_thread = None
        if not ok:
            self._vazir_failed = True
            return
        if LANG == "fa" and not self.busy:
            self.rebuild_ui()

    def rebuild_ui(self):
        apply_font(self.root)
        items = [(r["path"], r.get("is_folder", False)) for r in self.rows]
        self.cfg.update({
            "output_folder": self.output_folder.get(),
            "src_imdb": self.sw_imdb.get(), "src_wiki": self.sw_wiki.get(),
            "src_web": self.sw_web.get(), "save_next": self.sw_next.get(),
            "subfolders": self.sw_sub.get(), "overwrite": self.sw_over.get(),
            "include_folders": self.sw_folders.get(),
        })
        self.wrap.destroy()
        self.rows = []
        self.build_ui()
        if items:
            self.load_items(items)
        self.root.after(80, self._paint_header_banner)

    def set_language(self, code):
        if code == LANG:
            return
        if self.busy:
            info(self, T("Please wait until the current task finishes."))
            return
        items = [(r["path"], r.get("is_folder", False)) for r in self.rows]
        self.cfg.update({
            "output_folder": self.output_folder.get(),
            "src_imdb": self.sw_imdb.get(), "src_wiki": self.sw_wiki.get(),
            "src_web": self.sw_web.get(), "save_next": self.sw_next.get(),
            "subfolders": self.sw_sub.get(), "overwrite": self.sw_over.get(),
            "include_folders": self.sw_folders.get(), "lang": code,
        })
        set_lang(code)
        apply_font(self.root)
        self.root.title(f"{APP_NAME} — {T(APP_TAGLINE)}")
        self.wrap.destroy()
        self.rows = []
        self.last_dest = None
        self.build_ui()
        if items:
            self.load_items(items)
        self.root.after(80, self._paint_header_banner)
        self.root.after(300, self._ensure_font)

    def build_ui(self):
        if not hasattr(self, "page") or not self.page.winfo_exists():
            self.page = SideScroll(self.root, BG)
            self.page.pack(fill="both", expand=True)
        wrap = tk.Frame(self.page.inner, bg=BG)
        wrap.pack(fill="both", expand=True, padx=24, pady=(22, 0))
        self.wrap = wrap
        side = tk.Frame(wrap, bg=BG)
        main = tk.Frame(wrap, bg=BG)
        self.side, self.main, self._side_mode = side, main, None
        tk.Frame(side, bg=BG, width=300, height=1).pack(side="top")
        self.build_sidebar(side)
        self.build_main(main)
        self._place_side()

    def _sync_list_mode(self):
        """Wide window: only the movie list scrolls (header and sidebar stay fixed).
        Narrow window: the whole page scrolls once, the list shows all its items."""
        sc = getattr(self, "scroll", None)
        if sc is None:
            return
        sc.pack_forget()
        if getattr(self, "_narrow", False):
            sc.pack(fill="x")
            self._fit_list_narrow()
        else:
            sc.canvas.configure(height=1)
            sc.pack(fill="both", expand=True)

    def _fit_list_narrow(self):
        sc = getattr(self, "scroll", None)
        if sc is None or not getattr(self, "_narrow", False):
            return
        sc.canvas.configure(height=max(1, sc.inner.winfo_reqheight()))

    def _place_side(self):
        if not hasattr(self, "side"):
            return
        mode = "top" if self._narrow else "right"
        self._sync_list_mode()
        if mode == self._side_mode:
            return
        self._side_mode = mode
        self.side.pack_forget()
        self.main.pack_forget()
        if mode == "right":
            self.side.pack(side="right", fill="y", padx=(20, 0))
            self.main.pack(side="left", fill="both", expand=True, pady=(0, 14))
        else:
            self.side.pack(side="top", fill="x", pady=(0, 10))
            self.main.pack(side="top", fill="both", expand=True, pady=(0, 14))

    def _paint_side_banner(self, c):
        c.delete("all")
        W, H = c.winfo_width(), c.winfo_height()
        if W < 60 or H < 40:
            return
        R = RTL()
        drawn = False
        if HAVE_PIL:
            try:
                img = tk.PhotoImage(data=make_banner_png(W, H, 18, R))
                c._bg_ref = img
                c.create_image(0, 0, image=img, anchor="nw")
                drawn = True
            except Exception:
                drawn = False
        if not drawn:
            rrect(c, 0, 0, W, H, 18, fill=BRAND_NAVY, outline="")

        def X(x):
            return W - x if R else x
        anc = "e" if R else "w"
        cy = H / 2
        cx = X(44)
        c.create_oval(cx - 27, cy - 27, cx + 27, cy + 27, fill="#142348", outline=BRAND_GOLD, width=2)
        logo = load_logo((36, 36))
        if logo:
            c._logo_ref = logo
            c.create_image(cx, cy, image=logo, anchor="center")
        else:
            draw_icon(c, "film", cx, cy, 26, BRAND_GOLD, width=2.0, tags="hero")
        c.create_text(X(84), cy - 11, text=APP_NAME, anchor=anc, fill="#FFFFFF", font=(FAM, 16, "bold"))
        c.create_text(X(84), cy + 14, text=T(APP_TAGLINE) if R else APP_TAGLINE,
                      anchor=anc, fill=BRAND_GOLD_LIGHT, font=F(8))

    def build_sidebar(self, side):
        sc = Card(side, r=26, pad=18, stretch=True)
        sc.pack(fill="both", expand=True)
        b = sc.body

        foot = tk.Frame(b, bg=CARD)
        foot.pack(side="bottom", fill="x")
        tk.Frame(foot, bg=SEP, height=1).pack(fill="x", pady=(18, 10))
        lbl(foot, f"v{APP_VERSION}  •  {APP_NAME}", 8, fg=FAINT, bg=CARD).pack(anchor="w")

        banner = tk.Canvas(b, width=10, height=96, bg=CARD, highlightthickness=0, bd=0)
        banner.pack(fill="x", pady=(0, 18))
        banner.bind("<Configure>", lambda e, c=banner: self._paint_side_banner(c))

        def sep():
            tk.Frame(b, bg=SEP, height=1).pack(fill="x")

        section_title(b, T("Sources")).pack(anchor="w", pady=(0, 4))
        self.sw_imdb = Switch(b, "IMDb", self.cfg["src_imdb"])
        self.sw_imdb.pack(fill="x")
        sep()
        self.sw_wiki = Switch(b, T("Wikipedia"), self.cfg["src_wiki"])
        self.sw_wiki.pack(fill="x")
        sep()
        self.sw_web = Switch(b, T("Web images"), self.cfg["src_web"])
        self.sw_web.pack(fill="x")
        lbl(b, T("Up to {n} covers per item", n=MAX_OPTIONS), 9, fg=MUTED, bg=FILL,
            padx=12, pady=7).pack(fill="x", pady=(10, 0))

        tk.Frame(b, bg=CARD, height=18).pack(fill="x")
        section_title(b, T("Saving")).pack(anchor="w", pady=(0, 4))
        self.sw_next = Switch(b, T("Save next to the item"), self.cfg["save_next"], self.toggle_folder)
        self.sw_next.pack(fill="x")
        sep()
        self.sw_sub = Switch(b, T("Include subfolders"), self.cfg["subfolders"])
        self.sw_sub.pack(fill="x")
        sep()
        self.sw_folders = Switch(b, T("Cover folders too (series)"), self.cfg.get("include_folders", True))
        self.sw_folders.pack(fill="x")
        sep()
        self.sw_over = Switch(b, T("Overwrite existing covers"), self.cfg["overwrite"])
        self.sw_over.pack(fill="x")

        lbl(b, T("Output folder"), 9, True, fg=MUTED, bg=CARD).pack(anchor="w", pady=(16, 6))
        self.folder_entry = entry(b, self.output_folder, width=16)
        self.folder_entry.pack(fill="x")
        self.browse_btn = Btn(b, T("Browse"), self.choose_folder, "tint", size=9, px=18, py=6,
                              icon="folder", icon_size=13)
        self.browse_btn.pack(anchor="e", pady=(10, 0))
        self.toggle_folder(self.sw_next.get())

    def build_header(self, parent):
        self.header_canvas = tk.Canvas(parent, height=120, highlightthickness=0,
                                       bd=0, bg=BG)
        self.header_canvas.pack(fill="x", pady=(0, 6))
        self.header_canvas.bind("<Configure>", lambda e: self._paint_header_banner())

    def _paint_header_banner(self):
        c = self.header_canvas
        c.delete("all")
        W = c.winfo_width()
        H = c.winfo_height()
        if W < 40 or H < 40:
            return
        R = RTL()

        def X(x):
            return W - x if R else x

        def A(a):
            return _FLIP_ANCHOR.get(a, a) if R else a

        drawn = False
        if HAVE_PIL:
            try:
                bg = tk.PhotoImage(data=make_banner_png(W, H, 22, R))
                c._bg_ref = bg
                c.create_image(0, 0, image=bg, anchor="nw")
                drawn = True
            except Exception:
                drawn = False
        if not drawn:
            rrect(c, 0, 0, W, H, 22, fill=BRAND_NAVY, outline="")
            rrect(c, 0, 0, W, H, 22, fill="", outline=BRAND_GOLD, width=1)

        cy = H / 2
        logo = load_logo((64, 64))
        cx = X(72)
        c.create_oval(cx - 44, cy - 44, cx + 44, cy + 44, fill="#142348", outline=BRAND_GOLD, width=2)
        c.create_oval(cx - 50, cy - 50, cx + 50, cy + 50, outline="#5D6F9E", width=1)
        if logo:
            c._logo_ref = logo
            c.create_image(cx, cy, image=logo, anchor="center")
        else:
            draw_icon(c, "film", cx, cy, 42, BRAND_GOLD, width=2.0, tags="hero")
        text_x = X(142)

        if W < 620:
            c.create_text(text_x, cy, text=APP_NAME, anchor=A("w"), fill="#FFFFFF", font=(FAM, 20, "bold"))
            return
        c.create_text(text_x, cy - 14, text=APP_NAME, anchor=A("w"), fill="#FFFFFF", font=(FAM, 27, "bold"))
        tag = T(APP_TAGLINE) if R else APP_TAGLINE.upper()
        c.create_text(text_x, cy + 20, text=tag, anchor=A("w"),
                      fill=BRAND_GOLD_LIGHT, font=(FAM, 9, "bold"))

        import tkinter.font as tkfont
        f9 = tkfont.Font(family=FAM, size=9, weight="bold")
        pos = [30]

        def pill(text, fill, outline, fg):
            w = f9.measure(text) + 26
            if R:
                x1 = pos[0]
                x2 = x1 + w
            else:
                x2 = W - pos[0]
                x1 = x2 - w
            rrect(c, x1, cy - 14, x2, cy + 14, 14, fill=fill, outline=outline, width=1)
            c.create_text((x1 + x2) / 2, cy, text=text, fill=fg, font=(FAM, 9, "bold"))
            pos[0] += w + 10

        pill(f"v{APP_VERSION}", "#1B2A4E", BRAND_GOLD, BRAND_GOLD_LIGHT)
        if W >= 900:
            for name in ("Web", "Wikipedia", "IMDb"):
                pill(T(name), "#1E3266", "#4A63A0", "#D5E0FA")

    def build_main(self, main):
        self.build_header(main)

        head = tk.Frame(main, bg=BG)
        self.head_frame = head
        self._banner_shown = True
        head.pack(fill="x", pady=(10, 12))
        title_box = tk.Frame(head, bg=BG)
        title_box.pack(side="left", anchor="w")
        lbl(title_box, T("Welcome to {name}", name=APP_NAME), 22, True, bg=BG, fg=TEXT).pack(anchor="w")
        lbl(title_box, T("Find and save covers for movies and series — files or folders."),
            10, fg=MUTED, bg=BG).pack(anchor="w", pady=(1, 0))
        self.count_l = lbl(head, "", 9, fg=BRAND_GOLD, bg=BG)
        self.count_l.pack(side="left", padx=16, pady=(18, 0))
        self.theme_btn = Btn(head, T("Dark mode") if self.theme == "light" else T("Light mode"),
                             self.toggle_theme, "tint", size=10, px=18, py=9,
                             icon="moon" if self.theme == "light" else "sun", icon_size=15)
        self.theme_btn.pack(side="right", padx=(8, 0))
        self.about_btn = Btn(head, T("About"), self.show_about, "tint-gold", size=10, px=18, py=9,
                             icon="crown", icon_size=15)
        self.about_btn.pack(side="right")
        self.lang_btn = Btn(head, "فارسی" if LANG == "en" else "English",
                            lambda: self.set_language("fa" if LANG == "en" else "en"),
                            "tint-purple", size=10, px=18, py=9, icon="globe", icon_size=15)
        self.lang_btn.pack(side="right", padx=(0, 8))

        self.acts = FlowFrame(main, BG, gx=8, gy=8)
        self.acts.pack(fill="x", pady=(16, 12))
        self.acts.add(Btn(self.acts, T("Open folder"), self.select_folder, "navy", icon="folder"))
        self.acts.add(Btn(self.acts, T("Add files"), self.select_files, "indigo", icon="plus"))
        self.search_btn = Btn(self.acts, T("Find covers"), self.search_all, "gold", icon="search")
        self.acts.add(self.search_btn)
        self.save_btn = Btn(self.acts, T("Save covers"), self.save_all, "navy", icon="save")
        self.acts.add(self.save_btn)
        self.open_btn = Btn(self.acts, T("Open output"), self.open_output, "teal", icon="open")
        self.acts.add(self.open_btn)
        self.open_btn.set_enabled(False)
        self.acts.add(Btn(self.acts, T("Clear"), self.clear_rows, "tint-red", icon="trash", icon_size=13))
        self.acts.add(Btn(self.acts, T("Missing only"), self.filter_missing, "tint-amber",
                          icon="filter", icon_size=13))
        self.acts.add(Btn(self.acts, T("Select first"), self.select_first_results, "tint-gold",
                          icon="star", icon_size=13))

        self.status_l = lbl(main, T("Open a folder or add movie files"), 9, fg=MUTED, bg=BG)
        self.status_l.pack(anchor="w", pady=(0, 8))

        self.progress = RProgress(main)
        self.progress.pack(fill="x", pady=(0, 16))

        self.scroll = ScrollBox(main, BG)
        self.scroll.canvas.configure(height=1)
        self.scroll.pack(fill="both", expand=True)
        self.scroll.inner.bind("<Configure>", lambda e: self._fit_list_narrow(), add="+")
        self.list_frame = self.scroll.inner
        self.show_empty()

    def show_about(self):
        import webbrowser
        d = Dlg(self, T("About {name}", name=APP_NAME))
        d.resizable(False, False)
        body = d.body

        photo = None
        try:
            if HAVE_PIL:
                photo = tk.PhotoImage(data=make_about_header_png(420, 170, AUTHOR_PHOTO))
            else:
                photo = tk.PhotoImage(data=AUTHOR_PHOTO)
                f = max(1, photo.width() // 120)
                photo = photo.subsample(f, f)
        except Exception:
            photo = None
        if photo:
            img = tk.Label(body, image=photo, bg=CARD, bd=0)
            img.image = photo
            img.pack(pady=(0, 14))

        lbl(body, AUTHOR_NAME_FA if RTL() else AUTHOR_NAME, 18, True, fg=TEXT, bg=CARD).pack()
        lbl(body, T("Creator of {name}", name=APP_NAME), 10, fg=MUTED, bg=CARD).pack(pady=(3, 0))
        lbl(body, T("Version {v}", v=APP_VERSION), 9, True, fg=BRAND_GOLD, bg=CARD).pack(pady=(8, 12))

        lbl(body, (AUTHOR_BIO_FA if RTL() else f"I'm {AUTHOR_NAME}, a lover of cinema and the internet."), 10,
            fg=TEXT, bg=CARD, wraplength=400, justify="center").pack(pady=(0, 14))

        buttons = tk.Frame(body, bg=CARD)
        buttons.pack(pady=(0, 14))
        Btn(buttons, T("Author's Website"), lambda: webbrowser.open(AUTHOR_SITE), "gold",
            size=10, px=20, icon="globe", icon_size=15).pack(side="left")

        mail = Card(body, r=16, pad=13)
        mail.pack(fill="x", pady=(0, 14))
        row = tk.Frame(mail.body, bg=CARD)
        row.pack(fill="x")
        ic = tk.Canvas(row, width=26, height=26, bg=CARD, highlightthickness=0)
        ic.pack(side="left", padx=(0, 10))
        draw_icon(ic, "mail", 13, 13, 22, BRAND_GOLD, width=1.8, tags="ic")
        txt = tk.Frame(row, bg=CARD)
        txt.pack(side="left", fill="x", expand=True)
        lbl(txt, T("Contact email"), 9, fg=MUTED, bg=CARD).pack(anchor="w")
        lbl(txt, AUTHOR_EMAIL, 11, True, fg=TEXT, bg=CARD).pack(anchor="w")
        copied = lbl(mail.body, "", 9, fg=GREEN_T, bg=CARD)

        def copy_mail():
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(AUTHOR_EMAIL)
                copied.configure(text=T("Email copied to clipboard"))
                copied.pack(anchor="w", pady=(6, 0))
            except Exception:
                pass

        btns = tk.Frame(row, bg=CARD)
        btns.pack(side="right", padx=(12, 0))
        Btn(btns, T("Copy"), copy_mail, "tint-gold", size=9, px=12, py=6,
            icon="copy", icon_size=13).pack(side="left", padx=(0, 6))
        Btn(btns, T("Email"), lambda: webbrowser.open("mailto:" + AUTHOR_EMAIL), "tint-gold",
            size=9, px=12, py=6, icon="mail", icon_size=13).pack(side="left")

        Btn(body, T("Close"), d.destroy, "plain", size=10, px=20).pack(anchor="w")
        d.finish()

    def filter_missing(self):
        if not self.rows:
            info(self, T("Load a movie folder or add movie files first."))
            return
        def has_saved_cover(row):
            target = row["path"]
            if row.get("is_folder"):
                if find_folder_cover(target):
                    return True
            else:
                if existing_cover(target):
                    return True
            if not self.sw_next.get():
                output_dir = self.output_folder.get().strip()
                if not output_dir:
                    return False
                name = os.path.basename(target)
                stem = name if row.get("is_folder") else os.path.splitext(name)[0]
                for ext in COVER_EXTS:
                    if os.path.exists(os.path.join(output_dir, stem + ext)):
                        return True
            return False

        missing = [r for r in self.rows if not has_saved_cover(r)]
        missing_ids = {id(r) for r in missing}
        removed = len(self.rows) - len(missing)
        if not removed:
            info(self, T("No items with existing covers were found in this list."))
            return
        for r in self.rows:
            if id(r) not in missing_ids:
                try:
                    r["card"].destroy()
                except (KeyError, tk.TclError):
                    pass
        self.rows = missing
        if not self.rows:
            self.show_empty()
        self.update_count()
        self.set_status(T("Showing {n} items without covers", n=len(missing)))

    def select_first_results(self):
        count = 0
        for row in self.rows:
            if row.get("cands"):
                row["sel"] = 0
                row["skip"].set_style("tint-red")
                self.refresh(row)
                count += 1
        if count:
            self.set_status(T("Selected the first poster for {n} items", n=count))
        else:
            info(self, T("Find covers first. This selects the first result for each item with results."))

    def set_status(self, text):
        self.status_l.config(text=text)

    def update_count(self):
        n = len(self.rows)
        if not n:
            self.count_l.config(text="")
            return
        chosen = sum(1 for r in self.rows if r["cands"] and 0 <= r["sel"] < len(r["cands"]))
        if RTL():
            self.count_l.config(text=f"{n} مورد  •  {chosen} کاور انتخاب شده")
        else:
            self.count_l.config(text=f"{n} item{'s' if n != 1 else ''}  •  {chosen} cover{'s' if chosen != 1 else ''} selected")

    def show_empty(self):
        f = tk.Frame(self.list_frame, bg=BG)
        self.empty_hint = f
        f.pack(fill="x", pady=24)
        H = 300
        cv = tk.Canvas(f, bg=BG, height=H, highlightthickness=0, bd=0)
        cv.pack(fill="x", padx=6)

        def paint(_e=None):
            cv.delete("all")
            W = cv.winfo_width()
            if W < 120:
                return
            rrect(cv, 3, 3, W - 3, H - 3, 28, fill=CARD, outline=SEP, width=2, dash=(7, 6))
            cx = W / 2
            cv.create_oval(cx - 46, 20, cx + 46, 112, fill=_mix(CARD, BRAND_GOLD, .14),
                           outline=_mix(CARD, BRAND_GOLD, .45), width=2)
            draw_icon(cv, "film", cx, 66, 44, BRAND_GOLD, width=2.2, tags="ic")
            cv.create_text(cx, 138, text=T("No movies yet"), fill=TEXT, font=F(16, True))
            cv.create_text(cx, 166, text=T("Open a folder or add movie files to start finding covers"),
                           fill=MUTED, font=F(10))
            steps = [T("Open folder"), T("Find covers"), T("Save covers")]
            tf = tkfont.Font(font=F(10, True))
            widths = [tf.measure(t) + 60 for t in steps]
            total = sum(widths) + 18 * (len(steps) - 1)
            x = cx - total / 2
            order = list(enumerate(steps, 1))
            if LANG == "fa":
                order = order[::-1]
                widths = widths[::-1]
            for (n, t), w in zip(order, widths):
                rrect(cv, x, 196, x + w, 232, 18, fill=_mix(CARD, BRAND_GOLD, .10),
                      outline=_mix(CARD, BRAND_GOLD, .35), width=1)
                bx = x + 20
                cv.create_oval(bx - 11, 214 - 11, bx + 11, 214 + 11, fill=BRAND_GOLD, outline="")
                cv.create_text(bx, 214, text=str(n), fill="#FFFFFF", font=(FAM, 9, "bold"))
                cv.create_text(bx + 20, 214, text=t, anchor="w", fill=TEXT, font=F(10, True))
                x += w + 18
            cv.create_text(cx, 266, text=T("Works with MKV · MP4 · AVI · and series folders"),
                           fill=FAINT, font=F(9))
        cv.bind("<Configure>", paint)

    def toggle_folder(self, on):
        if on:
            self.folder_entry.configure(state="disabled")
            self.browse_btn.set_enabled(False)
        else:
            self.folder_entry.configure(state="normal")
            self.browse_btn.set_enabled(True)

    def choose_folder(self):
        folder = filedialog.askdirectory(initialdir=self.output_folder.get())
        if folder:
            self.output_folder.set(folder)

    def open_output(self):
        folder = self.last_dest
        if folder and os.path.isdir(folder) and os.name == "nt":
            os.startfile(folder)

    def select_folder(self):
        start = self.cfg.get("last_folder") or os.path.expanduser("~")
        folder = filedialog.askdirectory(title=T("Select the folder that contains your movies"), initialdir=start)
        if not folder:
            return
        self.cfg["last_folder"] = folder
        self.set_status(T("Scanning folder…"))
        self.root.update_idletasks()
        def scan():
            video_files = []
            subfolders = []
            def walk(dirpath):
                try:
                    entries = list(os.scandir(dirpath))
                except OSError:
                    return
                for e in entries:
                    try:
                        if e.is_file(follow_symlinks=False):
                            if os.path.splitext(e.name)[1].lower() in VIDEO_EXTS:
                                video_files.append(e.path)
                        elif e.is_dir(follow_symlinks=False):
                            subfolders.append(e.path)
                            if self.sw_sub.get():
                                walk(e.path)
                    except OSError:
                        continue
            walk(folder)
            self.root.after(0, self.load_from_scan, folder, video_files, subfolders)
        threading.Thread(target=scan, daemon=True).start()

    def load_from_scan(self, root_folder, video_files, subfolders):
        items = []
        for vf in video_files:
            items.append((vf, False))
        if self.sw_folders.get():
            for sf in subfolders:
                if os.path.normpath(sf) == os.path.normpath(root_folder):
                    continue
                try:
                    inner = [n for n in os.listdir(sf)
                             if os.path.splitext(n)[1].lower() in VIDEO_EXTS]
                except OSError:
                    inner = []
                folder_base = os.path.basename(sf).lower()
                if len(inner) == 1:
                    stem = os.path.splitext(inner[0])[0].lower()
                    if stem == folder_base or stem.startswith(folder_base):
                        continue
                items.append((sf, True))
        if not items:
            info(self, T("No video files or subfolders found here."))
            return
        items.sort(key=lambda x: os.path.basename(x[0]).lower())
        self.load_items(items)

    def select_files(self):
        exts = " ".join(f"*{e}" for e in sorted(VIDEO_EXTS))
        paths = filedialog.askopenfilenames(
            title=T("Select one or more movie files"),
            initialdir=self.cfg.get("last_folder") or None,
            filetypes=[(T("Video files"), exts), (T("All files"), "*.*")],
        )
        if paths:
            self.cfg["last_folder"] = os.path.dirname(paths[0])
            self.load_items([(p, False) for p in paths])

    def load_items(self, items):
        self.clear_rows(keep_status=True)
        try:
            self.empty_hint.destroy()
        except Exception:
            pass
        for path, is_folder in items:
            self.add_row(path, is_folder)
        self.update_count()
        self.set_status(T("Press Find covers"))

    def clear_rows(self, keep_status=False):
        for w in self.list_frame.winfo_children():
            w.destroy()
        self.rows.clear()
        self.progress.set(0, 1)
        self.update_count()
        self.show_empty()
        if not keep_status:
            self.set_status(T("Open a folder or add movie files"))

    def add_row(self, path, is_folder=False):
        if is_folder:
            stem = os.path.basename(path.rstrip("\\/"))
            display = f"📁  {stem}"
        else:
            stem = os.path.splitext(os.path.basename(path))[0]
            display = os.path.basename(path)
        title, year = parse_name(stem)
        qvar = tk.StringVar(value=f"{title} {year}" if year else title)

        card = Card(self.list_frame, r=20, pad=16, accent=BRAND_GOLD)
        card.pack(fill="x", pady=6)
        b = card.body

        top = tk.Frame(b, bg=CARD)
        top.pack(fill="x")
        lbl(top, display, 11, True, bg=CARD, wraplength=760).pack(side="left", anchor="w")
        if is_folder:
            lbl(top, T("folder"), 9, True, fg="#7B4DFF", bg=CARD).pack(side="left", padx=8)
        if not is_folder and existing_cover(path):
            lbl(top, T("● has cover"), 9, True, fg=GREEN_T, bg=CARD).pack(side="left", padx=10)
        if is_folder and find_folder_cover(path):
            lbl(top, T("● has cover"), 9, True, fg=GREEN_T, bg=CARD).pack(side="left", padx=10)

        controls = FlowFrame(b, CARD, gx=8, gy=8)
        controls.pack(fill="x", pady=(8, 0))
        row = {"path": path, "query": qvar, "cands": [], "sel": -1,
               "tiles": [], "token": 0, "card": card, "is_folder": is_folder}
        row["skip"] = Btn(controls, T("Skip"), lambda r=row: self.skip(r), "tint-red", size=9,
                          icon="skip", icon_size=12)
        controls.add(row["skip"])
        controls.add(Btn(controls, T("Search"), lambda r=row: self.search_one(r), "gold", size=9,
                         icon="search", icon_size=12))
        ent = entry(controls, qvar, width=34)
        controls.add(ent)
        ent.bind("<Return>", lambda e, r=row: self.search_one(r))

        row["status"] = lbl(b, T("Not searched yet"), 9, fg=FAINT, bg=CARD, wraplength=900)
        row["status"].pack(fill="x", pady=(8, 0))
        row["posters"] = FlowFrame(b, CARD, gx=12, gy=12)
        row["posters"].pack(fill="x", pady=(8, 0))
        self.rows.append(row)

    def render(self, row, cands, err, note=""):
        row["token"] += 1
        token = row["token"]
        row["cands"] = cands
        row["tiles"] = []
        row["posters"].clear()
        row["skip"].set_style("tint-red")
        if not cands:
            row["sel"] = -1
            row["status"].config(text=err or T("No cover found"), fg=RED)
            self.update_count()
            return
        row["sel"] = 0
        for i, c in enumerate(cands[:MAX_OPTIONS]):
            tile = tk.Frame(row["posters"], bg=CARD, cursor="hand2")
            row["posters"].add(tile)
            img = tk.Label(tile, text="…", bg=FILL, fg=FAINT, width=15, height=9)
            cap = lbl(tile, c["title"], 8, True, bg=CARD, wraplength=THUMB_SIZE[0], anchor="center")
            meta = lbl(tile, " · ".join(x for x in (c["source"], c["year"]) if x), 8, fg=FAINT,
                       bg=CARD, anchor="center")
            img.pack(padx=4, pady=(4, 0))
            cap.pack(fill="x", pady=(6, 0))
            meta.pack(fill="x", pady=(0, 6))
            td = {"frame": tile, "img": img, "labels": [cap, meta], "bg": CARD, "loaded": False}
            for w in [tile, img, cap, meta]:
                w.bind("<Button-1>", lambda e, r=row, k=i: self.select(r, k))
            row["tiles"].append(td)
            THUMB_POOL.submit(self.load_thumb, row, token, td, c["thumb"])
        self.refresh(row)
        if RTL():
            text = f"{len(cands)} کاور، یکی را برای انتخاب کلیک کنید"
        else:
            text = f"{len(cands)} cover{'s' if len(cands) != 1 else ''} — click one to choose"
        if note:
            text += "\n" + note
        row["status"].config(text=text, fg=MUTED)
        self.update_count()

    def paint_tile(self, td, sel):
        bg = ("#FAF0D2" if self.theme == "light" else "#3F3418") if sel else CARD
        td["bg"] = bg
        edge = BRAND_GOLD if sel else CARD
        td["frame"].configure(bg=bg, highlightthickness=2, highlightbackground=edge,
                              highlightcolor=edge)
        for w in td["labels"]:
            w.configure(bg=bg)
        td["img"].configure(bg=bg if td["loaded"] else FILL)

    def refresh(self, row):
        for i, td in enumerate(row["tiles"]):
            self.paint_tile(td, i == row["sel"])
        self.update_count()

    def select(self, row, idx):
        row["sel"] = idx
        row["skip"].set_style("tint-red")
        self.refresh(row)

    def skip(self, row):
        if not row["cands"]:
            return
        if row["sel"] == -1:
            self.select(row, 0)
            return
        row["sel"] = -1
        row["skip"].set_style("dark")
        self.refresh(row)

    def load_thumb(self, row, token, td, url):
        im = THUMB_CACHE.get(url)
        if im is None:
            try:
                r = SESSION.get(url, timeout=THUMB_TIMEOUT)
                r.raise_for_status()
                im = prepare_thumb(r.content, url)
                if im:
                    if len(THUMB_CACHE) > 600:
                        for _ in range(100):
                            THUMB_CACHE.pop(next(iter(THUMB_CACHE)))
                    THUMB_CACHE[url] = im
            except Exception:
                im = None
        self.root.after(0, self.set_thumb, row, token, td, im)

    def set_thumb(self, row, token, td, im):
        if row["token"] != token:
            return
        try:
            if im is None:
                td["img"].configure(text=T("unavailable"), bg=td["bg"])
                return
            photo = tk.PhotoImage(file=im)
            td["loaded"] = True
            td["img"].configure(image=photo, text="", width=photo.width(),
                                height=photo.height(), bg=td["bg"])
            td["img"].image = photo
            td["frame"].master._schedule_layout()
        except tk.TclError:
            pass

    def current_opts(self):
        return {
            "imdb": self.sw_imdb.get(), "wiki": self.sw_wiki.get(),
            "web": self.sw_web.get(), "limit": MAX_OPTIONS,
        }

    def search_one(self, row):
        opts = self.current_opts()
        if not (opts["imdb"] or opts["wiki"] or opts["web"]):
            info(self, T("Turn on at least one source."))
            return
        row["status"].config(text=T("Searching…"), fg=MUTED)
        q = row["query"].get().strip()

        def work():
            cands, err, note = find_covers_cached(q, opts)
            self.root.after(0, self.render, row, cands, err, note)

        threading.Thread(target=work, daemon=True).start()

    def search_all(self):
        if self.busy:
            return
        if not self.rows:
            info(self, T("Open a folder or add movie files first."))
            return
        opts = self.current_opts()
        if not (opts["imdb"] or opts["wiki"] or opts["web"]):
            info(self, T("Turn on at least one source."))
            return
        self.busy = True
        self.search_btn.set_enabled(False)
        self.save_btn.set_enabled(False)
        self.progress.set(0, len(self.rows))
        jobs = [(r, r["query"].get().strip()) for r in self.rows]
        for r, _ in jobs:
            r["status"].config(text=T("Waiting…"), fg=FAINT)
        threading.Thread(target=self._search_worker, args=(jobs, opts), daemon=True).start()

    def _search_worker(self, jobs, opts):
        total = len(jobs)
        lock = threading.Lock()
        counter = {"n": 0}

        def job(row, q):
            try:
                cands, err, note = find_covers_cached(q, opts)
            except Exception as e:
                cands, err, note = [], T("Error: {e}", e=e), ""
            with lock:
                counter["n"] += 1
                n = counter["n"]
            self.root.after(0, self.row_done, row, cands, err, note, n, total)

        with ThreadPoolExecutor(max_workers=6) as ex:
            for row, q in jobs:
                ex.submit(job, row, q)
        self.root.after(0, self.search_finished)

    def row_done(self, row, cands, err, note, n, total):
        self.render(row, cands, err, note)
        self.progress.set(n)
        self.set_status(T("Searching {n} of {total}…", n=n, total=total))

    def search_finished(self):
        self.busy = False
        self.search_btn.set_enabled(True)
        self.save_btn.set_enabled(True)
        found = sum(1 for r in self.rows if r["cands"])
        self.set_status(T("Covers found for {found} of {total} items", found=found, total=len(self.rows)))

    def save_all(self):
        if self.busy:
            return
        jobs = [(r["path"], r["cands"][r["sel"]], r.get("is_folder", False))
                for r in self.rows if r["cands"] and 0 <= r["sel"] < len(r["cands"])]
        if not jobs:
            info(self, T("Nothing to save. Find covers first and choose one for each item."))
            return
        dest = None
        if not self.sw_next.get():
            dest = self.output_folder.get().strip()
            if not dest:
                info(self, T("Choose a save folder first."))
                return
            try:
                os.makedirs(dest, exist_ok=True)
            except Exception as e:
                info(self, str(e))
                return
        self.last_dest = dest or (
            jobs[0][0] if jobs[0][2] else os.path.dirname(jobs[0][0])
        )
        self.busy = True
        self.search_btn.set_enabled(False)
        self.save_btn.set_enabled(False)
        self.progress.set(0, len(jobs))
        threading.Thread(target=self._save_worker,
                         args=(jobs, dest, self.sw_over.get()), daemon=True).start()

    @staticmethod
    def fetch_image(cand):
        last = None
        for url in (cand["full"], cand["thumb"]):
            try:
                r = SESSION.get(url, timeout=SLOW_TIMEOUT)
                r.raise_for_status()
                ctype = r.headers.get("Content-Type", "").lower()
                if ctype and not ctype.startswith("image"):
                    raise RuntimeError("not an image")
                return r, url
            except Exception as e:
                last = e
        raise last

    def _save_worker(self, jobs, dest, overwrite):
        saved, skipped, errors = 0, 0, []
        lock = threading.Lock()

        def do_one(i, item):
            nonlocal saved, skipped
            path, cand, is_folder = item
            name = os.path.basename(path.rstrip("\\/"))
            self.root.after(0, self.set_status, T("Saving {i} of {n}…", i=i, n=len(jobs)))
            try:
                folder = dest or (path if is_folder else os.path.dirname(path))
                stem = name if is_folder else os.path.splitext(name)[0]
                old = None
                if is_folder and not dest:
                    old = find_folder_cover(path)
                elif not is_folder and not dest:
                    old = existing_cover(path)
                else:
                    for ext in COVER_EXTS:
                        p = os.path.join(folder, stem + ext)
                        if os.path.exists(p):
                            old = p
                            break
                if old and not overwrite:
                    with lock:
                        skipped += 1
                    return
                r, url = self.fetch_image(cand)
                ext = self.extension_from(r, url)
                out_path = os.path.join(folder, stem + ext)
                temp_path = out_path + ".cyruscover-tmp"
                try:
                    with open(temp_path, "wb") as f:
                        f.write(r.content)
                    os.replace(temp_path, out_path)
                    if old and old != out_path and os.path.exists(old):
                        os.remove(old)
                finally:
                    if os.path.exists(temp_path):
                        try:
                            os.remove(temp_path)
                        except OSError:
                            pass
                with lock:
                    saved += 1
            except Exception as e:
                errors.append(f"{name}: {e}")
            finally:
                self.root.after(0, self.progress.set, i)

        with ThreadPoolExecutor(max_workers=4) as ex:
            for i, item in enumerate(jobs, start=1):
                ex.submit(do_one, i, item)
        self.root.after(0, self.save_finished, saved, skipped, errors)

    @staticmethod
    def extension_from(response, url):
        ctype = response.headers.get("Content-Type", "").lower()
        if "png" in ctype:
            return ".png"
        if "webp" in ctype:
            return ".webp"
        if "jpeg" in ctype or "jpg" in ctype:
            return ".jpg"
        path = url.lower().split("?")[0]
        for ext in (".png", ".jpg", ".jpeg", ".webp"):
            if path.endswith(ext):
                return ".jpg" if ext == ".jpeg" else ext
        return ".jpg"

    def save_finished(self, saved, skipped, errors):
        self.busy = False
        self.search_btn.set_enabled(True)
        self.save_btn.set_enabled(True)
        self.open_btn.set_enabled(bool(self.last_dest))
        msg = T("Saved: {n}", n=saved)
        if skipped:
            msg += "\n" + T("Already existed (skipped): {n}  (turn on Overwrite to replace)", n=skipped)
        if errors:
            self.set_status(T("Done — {n} error(s)", n=len(errors)))
            info(self, msg + "\n\n" + T("Errors:") + "\n" + "\n".join(errors[:15]))
        else:
            self.set_status(T("All selected covers saved"))
            info(self, msg)


def _log_error(text):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(os.path.join(CONFIG_DIR, "error.log"), "a", encoding="utf-8") as fh:
            fh.write(time.strftime("%Y-%m-%d %H:%M:%S") + "\n" + text + "\n\n")
    except Exception:
        pass


def main():
    import traceback
    try:
        if sys.platform == "win32":
            try:
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                    "CyrusCover.CoverFinder.1")
            except Exception:
                pass
        root = tk.Tk()
        App(root)
        root.mainloop()
    except Exception:
        err = traceback.format_exc()
        _log_error(err)
        try:
            from tkinter import messagebox
            messagebox.showerror(APP_NAME, "برنامه اجرا نشد.\n\n" + err[-900:])
        except Exception:
            print(err)


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        import traceback
        traceback.print_exc()
        input("\nAn error happened. Press Enter to close...")