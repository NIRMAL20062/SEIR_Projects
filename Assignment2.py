import sys
import re
import urllib.request
from html.parser import HTMLParser

P = 53
M = 2 ** 64
BITS = 64


def poly_hash(word):
    h = 0
    power = 1
    for ch in word:
        h = (h + ord(ch) * power) % M
        power = (power * P) % M
    return h


def simhash(freq):
    vector = [0] * BITS

    for word, weight in freq.items():
        h = poly_hash(word)
        for i in range(BITS):
            if (h >> i) & 1:
                vector[i] += weight
            else:
                vector[i] -= weight

    result = 0
    for i in range(BITS):
        if vector[i] > 0:
            result |= (1 << i)

    return result


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "head"):
            self.skip = True

    def handle_endtag(self, tag):
        if tag in ("script", "style", "head"):
            self.skip = False

    def handle_data(self, data):
        if not self.skip:
            self.text.append(data)

    def get_text(self):
        return " ".join(self.text)


def fetch_text(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode(
            resp.headers.get_content_charset() or "utf-8",
            errors="replace"
        )

    parser = TextExtractor()
    parser.feed(html)
    return parser.get_text()


def word_frequencies(text):
    words = re.findall(r"[a-z0-9]+", text.lower())
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    return freq


if len(sys.argv) != 3:
    print("Usage: python simhash.py <url1> <url2>")
    sys.exit(1)

url1, url2 = sys.argv[1], sys.argv[2]

print(f"Fetching: {url1}")
text1 = fetch_text(url1)

print(f"Fetching: {url2}")
text2 = fetch_text(url2)

h1 = simhash(word_frequencies(text1))
h2 = simhash(word_frequencies(text2))

common = BITS - bin(h1 ^ h2).count("1")

print()
print(f"Simhash 1 : {h1:064b}  ({h1})")
print(f"Simhash 2 : {h2:064b}  ({h2})")
print()
print(f"Bits in common: {common} / {BITS}")
print(f"Similarity    : {common / BITS:.2%}")
