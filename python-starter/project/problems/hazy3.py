# python-starter/project/problems/hazi3.py
import re
import sys

from project.problem import Problem


def natural_key(name):
    """q2 < q10 természetes sorrend."""
    return [int(t) if t.isdigit() else t for t in re.split(r'(\d+)', name)]


def new_name(name):
    """q1 -> s1"""
    return 's' + name[1:] if name.startswith('q') else 's' + name


class Hazi3(Problem):

    def initialize_parser(self, parser):
        parser.add_argument('--mini', action='store_true',
                            help='determinisztikus automata minimalizálása')

    def is_chosen_problem(self, args):
        return bool(getattr(args, 'mini', False))

    def run(self, args):
        try:
            automaton = self.read_automaton(args.input)
        except ValueError as e:
            print(f"Hiba: {e}", file=sys.stderr)
            raise SystemExit(1)

        result = self.minimize(*automaton)

        with open(args.output, 'w', encoding='utf-8') as f:
            f.write("\n".join(result) + "\n")

    # ---------- beolvasás ----------

    @staticmethod
    def read_automaton(path):
        with open(path, encoding='utf-8') as f:
            lines = [l.strip() for l in f.read().splitlines()]

        if len(lines) < 3:
            raise ValueError("hiányos bemeneti fájl")

        states = lines[0].split()
        alphabet = lines[1].split()
        start_tokens = lines[2].split()
        if len(start_tokens) != 1:
            raise ValueError("pontosan egy kezdőállapot szükséges")
        start = start_tokens[0]
        finals = lines[3].split() if len(lines) > 3 else []

        state_set = set(states)
        symbol_set = set(alphabet)

        if start not in state_set:
            raise ValueError(f"ismeretlen kezdőállapot: {start}")
        for q in finals:
            if q not in state_set:
                raise ValueError(f"ismeretlen végállapot: {q}")

        delta = {}
        for line in lines[4:]:
            if not line:
                continue
            parts = line.replace(',', ' ').split()
            if len(parts) != 3:
                raise ValueError(f"hibás átmenet: {line}")
            src, sym, dst = parts
            if src not in state_set or dst not in state_set:
                raise ValueError(f"ismeretlen állapot az átmenetben: {line}")
            if sym not in symbol_set:
                raise ValueError(f"ismeretlen jel az átmenetben: {line}")
            if (src, sym) in delta and delta[(src, sym)] != dst:
                raise ValueError(f"nem determinisztikus átmenet: {line}")
            delta[(src, sym)] = dst

        return states, alphabet, start, finals, delta

    # ---------- minimalizálás ----------

    @staticmethod
    def minimize(states, alphabet, start, finals, delta):
        symbols = sorted(alphabet)
        final_set = set(finals)

        # elérhetetlen állapotok elhagyása
        reachable = {start}
        stack = [start]
        while stack:
            q = stack.pop()
            for a in symbols:
                t = delta.get((q, a))
                if t is not None and t not in reachable:
                    reachable.add(t)
                    stack.append(t)
        states = [q for q in states if q in reachable]

        # partíciófinomítás (hiányzó átmenet = -1 osztály)
        cls = {q: (1 if q in final_set else 0) for q in states}
        while True:
            sigs = {}
            new_cls = {}
            for q in states:
                sig = (cls[q],) + tuple(
                    cls[delta[(q, a)]] if (q, a) in delta else -1
                    for a in symbols)
                new_cls[q] = sigs.setdefault(sig, len(sigs))
            if len(set(new_cls.values())) == len(set(cls.values())):
                cls = new_cls
                break
            cls = new_cls

        # osztályok legkisebb nevű képviselővel
        groups = {}
        for q in states:
            groups.setdefault(cls[q], []).append(q)
        rep = {}
        for members in groups.values():
            smallest = min(members, key=natural_key)
            for q in members:
                rep[q] = new_name(smallest)

        new_states = sorted(set(rep.values()), key=natural_key)
        new_start = rep[start]
        new_finals = sorted({rep[q] for q in states if q in final_set},
                            key=natural_key)

        transitions = set()
        for (src, sym), dst in delta.items():
            if src in rep and dst in rep:
                transitions.add((rep[src], sym, rep[dst]))
        transitions = sorted(
            transitions,
            key=lambda t: (natural_key(t[0]), t[1], natural_key(t[2])))

        out = [
            " ".join(new_states),
            " ".join(alphabet),
            new_start,
            " ".join(new_finals),
        ]
        out.extend(f"{s} {a} {d}" for s, a, d in transitions)
        return out