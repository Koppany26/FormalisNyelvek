import re
import evaluate_formal as g   # az import nem futtatja le a teszteket

EXPECTED = [15554, 2816, 2825, 10, 1, 3196, 104, 54, 645, 244]
LINE_RE = re.compile(r"(([0-9-]+ [0-9:.]+) +([0-9]+) +([0-9]+) ([IDVEFAW]) (.+?):(?: (.+))?)")

lines = g.N.replace("\r\n", "\n").split("\n")
parsed = [m for m in map(LINE_RE.match, lines) if m]
print("sorok:", len(lines), "illeszkedo:", len(parsed))

def raw(rx):
    return lambda: sum(bool(re.search(rx, l)) for l in lines)

def par(fn):
    return lambda: sum(1 for m in parsed if fn(m))

P = r"^\S+ \S+ +\d+ +\d+ "
V = [
 [("raw ^10-15 ", raw(r"^10-15 ")),
  ("parsed ts", par(lambda m: re.match(r"10-15 ", m.group(2)))),
  ("barhol 10-15", raw(r"10-15"))],
 [("^10-15 10:18:51", raw(r"^10-15 10:18:51\.")),
  ("parsed ts", par(lambda m: re.match(r"10-15 10:18:51\.", m.group(2)))),
  ("barhol", raw(r"10-15 10:18:51"))],
 [("barmely datum/perc", raw(r"^\S+ \d\d:\d\d:51\.")),
  ("10-15 10:xx:51", raw(r"^10-15 10:\d\d:51\.")),
  ("parsed :51.", par(lambda m: re.search(r":51\.", m.group(2)))),
  ("barhol :51.", raw(r":51\."))],
 [("tag lmk", par(lambda m: m.group(6).strip() == "lowmemorykiller")),
  ("barhol lmk", raw(r"lowmemorykiller")),
  ("tag tartalmaz", par(lambda m: "lowmemorykiller" in m.group(6)))],
 [("10:18:51 es pid 221 (barmely datum)", par(lambda m: re.search(r"10:18:51\.", m.group(2)) and m.group(3) == "221")),
  ("csak 10-15", par(lambda m: re.match(r"10-15 10:18:51\.", m.group(2)) and m.group(3) == "221")),
  ("pid vagy tid 221", par(lambda m: re.search(r"10:18:51\.", m.group(2)) and "221" in (m.group(3), m.group(4))))],
 [("E szint", par(lambda m: m.group(5) == "E")),
  ("raw ' E '", raw(r" E ")),
  ("raw E sor", raw(P + r"E "))],
 [("W + tag PackageManager", par(lambda m: m.group(5) == "W" and m.group(6).strip() == "PackageManager")),
  ("W + tag tartalmaz", par(lambda m: m.group(5) == "W" and "PackageManager" in m.group(6))),
  ("W + barhol", par(lambda m: m.group(5) == "W" and "PackageManager" in m.group(1)))],
 [("D + tag ExoPlayer*", par(lambda m: m.group(5) == "D" and m.group(6).startswith("ExoPlayer"))),
  ("D + tag pontos", par(lambda m: m.group(5) == "D" and m.group(6).strip() == "ExoPlayer")),
  ("D + tag tartalmaz", par(lambda m: m.group(5) == "D" and "ExoPlayer" in m.group(6))),
  ("D + barhol", par(lambda m: m.group(5) == "D" and "ExoPlayer" in m.group(1)))],
 [("EW + .java: egesz sor", par(lambda m: m.group(5) in "EW" and ".java:" in m.group(1))),
  ("EW + .java: uzenet", par(lambda m: m.group(5) in "EW" and m.group(7) and ".java:" in m.group(7))),
  ("EW + .java", par(lambda m: m.group(5) in "EW" and ".java" in m.group(1))),
  ("csak E + .java:", par(lambda m: m.group(5) == "E" and ".java:" in m.group(1)))],
 [("Thread uzenet", par(lambda m: m.group(7) and "Thread" in m.group(7))),
  ("\\bThread\\b", par(lambda m: m.group(7) and re.search(r"\bThread\b", m.group(7)))),
  ("ignorecase", par(lambda m: m.group(7) and re.search(r"(?i)thread", m.group(7)))),
  ("egesz sor", par(lambda m: "Thread" in m.group(1)))],
]

for i, variants in enumerate(V):
    print(f"\n{i+1}. alpont, elvart: {EXPECTED[i]}")
    for name, fn in variants:
        n = fn()
        print(f"   {'OK ' if n == EXPECTED[i] else '   '} {name}: {n}")