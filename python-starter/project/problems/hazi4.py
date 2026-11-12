# python-starter/project/problems/hazi4.py
import re
from collections import Counter

from project.problem import Problem

# A feladatban megadott kifejezés (csoportok: 1 teljes, 2 időbélyeg, 3 pid, 4 tid, 5 szint, 6 tag, 7 üzenet)
LINE_RE = re.compile(r"(([0-9-]+ [0-9:.]+) +([0-9]+) +([0-9]+) ([IDVEFAW]) (.+?):(?: (.+))?)")
JAVA_FILE_RE = re.compile(r"([\w$-]+\.java)(?=:\d+)")

# 1. feladat alpontjai (nyers sorokra)
RE_DATE = re.compile(r"^10-15 ")
RE_DATETIME = re.compile(r"^10-15 10:18:51\.")
RE_SECOND = re.compile(r"^\S+ \d\d:\d\d:51\.")
RE_LMK = re.compile(r"^\S+ \S+ +\d+ +\d+ [IDVEFAW] lowmemorykiller:")
RE_PID221 = re.compile(r"^\S+ 10:18:51\.\d+ +221 +\d+ ")
RE_ERROR = re.compile(r"^\S+ \S+ +\d+ +\d+ E ")
RE_PKGMAN_W = re.compile(r"^\S+ \S+ +\d+ +\d+ W PackageManager:")
RE_EXO_D = re.compile(r"^\S+ \S+ +\d+ +\d+ D ExoPlayer\S*:")
RE_JAVA_EW = re.compile(r"^\S+ \S+ +\d+ +\d+ [EW] .*\.java:")
RE_THREAD_MSG = re.compile(r"Thread")


class Hazi4(Problem):

    def initialize_parser(self, parser):
        parser.add_argument('--rgx', type=int, default=None,
                            help='regex feladat sorszáma (1-5)')

    def is_chosen_problem(self, args):
        return getattr(args, 'rgx', None) is not None

    def run(self, args):
        tasks = {
            1: self.task1,
            2: self.task2,
            3: self.task3,
            4: self.task4,
            5: self.task5,
        }
        if args.rgx not in tasks:
            raise SystemExit(f"Ismeretlen feladat: {args.rgx}")

        lines = self.read_lines(args.input)
        result = tasks[args.rgx](lines)

        with open(args.output, 'w', encoding='utf-8') as f:
            f.write("\n".join(result) + ("\n" if result else ""))

    # ---------- segédfüggvények ----------

    @staticmethod
    def read_lines(path):
        with open(path, encoding='utf-8', errors='replace') as f:
            return [l.rstrip("\r\n") for l in f]

    @staticmethod
    def parse(lines):
        for line in lines:
            m = LINE_RE.match(line)
            if m:
                yield m

    # ---------- feladatok ----------

    def task1(self, lines):
        counts = [0] * 10
        for line in lines:
            if RE_DATE.search(line):
                counts[0] += 1
            if RE_DATETIME.search(line):
                counts[1] += 1
            if RE_SECOND.search(line):
                counts[2] += 1
            if RE_LMK.search(line):
                counts[3] += 1
            if RE_PID221.search(line):
                counts[4] += 1
            if RE_ERROR.search(line):
                counts[5] += 1
            if RE_PKGMAN_W.search(line):
                counts[6] += 1
            if RE_EXO_D.search(line):
                counts[7] += 1
            if RE_JAVA_EW.search(line):
                counts[8] += 1
            m = LINE_RE.match(line)
            if m and m.group(7) and RE_THREAD_MSG.search(m.group(7)):
                counts[9] += 1
        return [str(c) for c in counts]

    def task2(self, lines):
        out = []
        for m in self.parse(lines):
            if m.group(5) == "E" and m.group(7):
                out.extend(JAVA_FILE_RE.findall(m.group(7)))
        return out

    def task3(self, lines):
        seen = []
        for m in self.parse(lines):
            pid = m.group(3)
            if pid not in seen:
                seen.append(pid)
        return seen

    def task4(self, lines):
        c = Counter(m.group(3) for m in self.parse(lines) if m.group(5) == "E")
        if not c:
            return []
        pid, n = c.most_common(1)[0]  # döntetlennél az először előforduló
        return [f"PID={pid} ({n} errors)"]

    def task5(self, lines):
        n = sum(1 for m in self.parse(lines)
                if m.group(5) == "E" and m.group(3) == m.group(4))
        return [str(n)]