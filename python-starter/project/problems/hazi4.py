import argparse
import re
from collections import Counter


def solve_task_1(lines: list[str]) -> list[str]:
    patterns = [
        # 1. 10. hónap 15-én jött létre
        re.compile(r"^10-15\b"),
        # 2. 10. hónap 15-én 10 óra 18 perc és 51 másodperckor jött létre
        re.compile(r"^10-15 10:18:51\."),
        # 3. 51 másodperckor jött létre (mindegy a perc)
        re.compile(r"^\d{2}-\d{2} \d{2}:\d{2}:51\."),
        # 4. összes lowmemorykiller taget tartalmazó sor
        re.compile(r"^\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+\s+\d+\s+\d+\s+[IDVEFAW]\s+lowmemorykiller\s*:"),
        # 5. összes 10:18:51-kor keletkező 221-es process id-jú sor
        re.compile(r"^\d{2}-\d{2} 10:18:51\.\d+\s+221\s+"),
        # 6. összes hibát tartalmazó sor (E)
        re.compile(r"^\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+\s+\d+\s+\d+\s+E\s+"),
        # 7. összes warning (W) amit a PackageManager küld
        re.compile(r"^\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+\s+\d+\s+\d+\s+W\s+PackageManager\s*:"),
        # 8. összes ExoPlayer-es debug (D) infó
        re.compile(r"^\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+\s+\d+\s+\d+\s+D\s+ExoPlayer[^:]*:"),
        # 9. összes java állomány pozíciót tartalmazó hiba és warning (E/W és .java:)
        re.compile(r"^\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+\s+\d+\s+\d+\s+[EW]\s+.*?\b[\w$]+\.java:\d+"),
        # 10. összes olyan sor, ami tartalmazza a Thread szót a message részben (nem a tagben)
        re.compile(r"^\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+\s+\d+\s+\d+\s+[IDVEFAW]\s+[^:]+:\s*.*\bThread\b"),
    ]

    results = []
    for pattern in patterns:
        count = sum(1 for line in lines if pattern.search(line))
        results.append(str(count))

    return results


def solve_task_2(lines: list[str]) -> list[str]:
    # Hibasorokból (E) kiszedi a .java fájlneveket a stack trace-ből (pl. HashMap.java)
    pattern = re.compile(
        r"^[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ E .+?:\s*.*\(([A-Za-z0-9_$]+\.java):[0-9]+\)"
    )
    results = []
    for line in lines:
        match = pattern.search(line)
        if match:
            results.append(match.group(1))
    return results


def solve_task_3(lines: list[str]) -> list[str]:
    # Különböző process id-k előfordulási sorrendben
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


def solve_task_4(lines: list[str]) -> list[str]:
    # A legtöbb errort (E) tartalmazó process id
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


def solve_task_5(lines: list[str]) -> list[str]:
    # Fő szálon történt hibák (E) száma, ahol PID == TID (visszahivatkozás: \1)
    pattern = re.compile(r"^[0-9-]+ [0-9:.]+ +([0-9]+) +\1 E ")
    count = sum(1 for line in lines if pattern.search(line))
    return [str(count)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Logcat elemző regexek segítségével.")
    parser.add_argument("--input", required=True, help="Bemeneti logfájl útvonala")
    parser.add_argument("--output", required=True, help="Kimeneti fájl útvonala")
    parser.add_argument("--rgx", required=True, type=int, choices=[1, 2, 3, 4, 5], help="Feladat sorszáma (1-5)")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    solvers = {
        1: solve_task_1,
        2: solve_task_2,
        3: solve_task_3,
        4: solve_task_4,
        5: solve_task_5,
    }

    output_lines = solvers[args.rgx](lines)

    with open(args.output, "w", encoding="utf-8") as f:
        if output_lines:
            f.write("\n".join(output_lines) + "\n")


if __name__ == "__main__":
    main()