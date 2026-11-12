import re
from collections import Counter
from project.problem import Problem


class RegexProblem(Problem):

    def initialize_parser(self, parser):
        parser.add_argument(
            "--rgx",
            type=int,
            choices=[1, 2, 3, 4, 5],
            help="Regex task number (1-5)",
        )

    def is_chosen_problem(self, args):
        return args.rgx is not None

    def run(self, args):
        with open(args.input, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        solvers = {
            1: self._solve_task_1,
            2: self._solve_task_2,
            3: self._solve_task_3,
            4: self._solve_task_4,
            5: self._solve_task_5,
        }

        output_lines = solvers[args.rgx](lines)

        with open(args.output, "w", encoding="utf-8") as f:
            if output_lines:
                f.write("\n".join(output_lines) + "\n")

    def _solve_task_1(self, lines: list[str]) -> list[str]:
        # Alap logcat struktúra a feladat megjegyzése alapján:
        # ^([0-9-]+ [0-9:.]+) +([0-9]+) +([0-9]+) ([IDVEFAW]) (.+?):(?: (.+))?$
        patterns = [
            # 1. az összes sort, amelyik 10. hónap 15-én jött létre
            re.compile(r"^10-15 "),
            # 2. az összes sort, amelyik 10. hónap 15-én 10 óra 18 perc és 51 másodperckor jött létre
            re.compile(r"^10-15 10:18:51\."),
            # 3. az összes sort, amelyik 51 másodperckor jött létre (mindegy a perc)
            re.compile(r"^[0-9-]+ [0-9]{2}:[0-9]{2}:51\."),
            # 4. az összes lowmemorykiller taget tartalmazó sor
            re.compile(r"^[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ [IDVEFAW] lowmemorykiller:"),
            # 5. az összes 10:18:51-kor keletkező 221-es process id-jú sort
            re.compile(r"^[0-9-]+ 10:18:51\.[0-9]+ +221 +[0-9]+ [IDVEFAW] "),
            # 6. az összes hibát tartalmazó sort (E)
            re.compile(r"^[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ E "),
            # 7. az összes warningot (W) amit a PackageManager küld
            re.compile(r"^[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ W PackageManager:"),
            # 8. az összes ExoPlayer-es debug (D) infót
            re.compile(r"^[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ D ExoPlayer:"),
            # 9. az összes java állomány pozíciót tartalmazó hibát és warningot (EW .java:)
            re.compile(r"^[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ [EW] .+?\.java:"),
            # 10. az összes olyan sort, ami tartalmazza a Thread szót a message részben (nem a tagben)
            re.compile(r"^[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ [IDVEFAW] .+?:\s+.*\bThread\b"),
        ]
        return [str(sum(1 for line in lines if p.search(line))) for p in patterns]

    def _solve_task_2(self, lines: list[str]) -> list[str]:
        pattern = re.compile(
            r"^[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ E .+?:\s*.*\(([A-Za-z0-9_$]+\.java):[0-9]+\)"
        )
        results = []
        for line in lines:
            match = pattern.search(line)
            if match:
                results.append(match.group(1))
        return results

    def _solve_task_3(self, lines: list[str]) -> list[str]:
        pattern = re.compile(r"^[0-9-]+ [0-9:.]+ +([0-9]+) +[0-9]+ [IDVEFAW] ")
        seen = set()
        results = []
        for line in lines:
            match = pattern.search(line)
            if match:
                pid = match.group(1)
                if pid not in seen:
                    seen.add(pid)
                    results.append(pid)
        return results

    def _solve_task_4(self, lines: list[str]) -> list[str]:
        pattern = re.compile(r"^[0-9-]+ [0-9:.]+ +([0-9]+) +[0-9]+ E ")
        error_counts = Counter()
        for line in lines:
            match = pattern.search(line)
            if match:
                error_counts[match.group(1)] += 1

        if not error_counts:
            return ["PID=None (0 errors)"]

        top_pid, count = error_counts.most_common(1)[0]
        return [f"PID={top_pid} ({count} errors)"]

    def _solve_task_5(self, lines: list[str]) -> list[str]:
        pattern = re.compile(r"^[0-9-]+ [0-9:.]+ +([0-9]+) +\1 E ")
        count = sum(1 for line in lines if pattern.search(line))
        return [str(count)]