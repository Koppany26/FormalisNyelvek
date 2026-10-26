import argparse
import sys
from project.problem import Problem
from collections import defaultdict


def parse_args():
    parser = argparse.ArgumentParser(description='DFA minimizer')
    parser.add_argument('--input', type=str, required=True, help='Input file path')
    parser.add_argument('--output', type=str, required=True, help='Output file path')
    parser.add_argument('--mini', action='store_true', help='Flag to minimize the automaton')
    return parser.parse_args()


def load_dfa(filepath):
    try:
        with open(filepath, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)

    if len(lines) < 4:
        print("Invalid input format.")
        sys.exit(1)

    states = lines[0].split()
    alphabet = lines[1].split()
    start_state = lines[2].strip()
    accept_states = lines[3].split()

    transitions = []
    for line in lines[4:]:
        parts = line.split()
        if len(parts) != 3:
            print(f"Invalid transition format: {line}")
            sys.exit(1)
        src, symbol, dest = parts

        # Alapvető hibakezelés (Error handling)
        if src not in states or dest not in states:
            print(f"Error: Transition state not in state list: {src} or {dest}")
            sys.exit(1)
        if symbol not in alphabet:
            print(f"Error: Transition symbol not in alphabet: {symbol}")
            sys.exit(1)

        transitions.append((src, symbol, dest))

    return states, alphabet, start_state, accept_states, transitions


def get_state_number(state_str):
    # Kinyeri a számot a qX vagy sX formátumból
    return int(state_str[1:])


def minimize_dfa(states, alphabet, start_state, accept_states, transitions):
    # Átmenetek gyors eléréséhez: (state, symbol) -> dest
    trans_map = {}
    for src, sym, dest in transitions:
        trans_map[(src, sym)] = dest

    # 1. Lépés: Elérhetetlen állapotok eltávolítása
    reachable = set([start_state])
    queue = [start_state]
    while queue:
        curr = queue.pop(0)
        for sym in alphabet:
            if (curr, sym) in trans_map:
                dest = trans_map[(curr, sym)]
                if dest not in reachable:
                    reachable.add(dest)
                    queue.append(dest)

    states = [s for s in states if s in reachable]
    accept_states = set([s for s in accept_states if s in reachable])

    # 2. Lépés: Ekvivalencia osztályok (Hopcroft / Moore féle particionálás)
    # Kezdeti partíciók: elfogadó és nem elfogadó állapotok
    P = [accept_states, set(states) - accept_states]
    P = [p for p in P if p]  # Üres halmazokat kivesszük

    W = list(P)

    while W:
        A = W.pop(0)
        for sym in alphabet:
            # Mely állapotokból jutunk A-ba a sym jellel?
            X = set([s for s in states if trans_map.get((s, sym)) in A])

            new_P = []
            for Y in P:
                intersection = Y.intersection(X)
                difference = Y.difference(X)

                if intersection and difference:
                    new_P.append(intersection)
                    new_P.append(difference)
                    if Y in W:
                        W.remove(Y)
                        W.append(intersection)
                        W.append(difference)
                    else:
                        if len(intersection) <= len(difference):
                            W.append(intersection)
                        else:
                            W.append(difference)
                else:
                    new_P.append(Y)
            P = new_P

    # Csoportok azonosítása. Minden csoporthoz kiválasztjuk a legkisebb indexűt névnek.
    # Az állapotokat q1 -> 1-ként rendezzük, így könnyű megtalálni a legkisebbet.
    state_mapping = {}
    for group in P:
        sorted_group = sorted(list(group), key=get_state_number)
        representative = sorted_group[0]
        # Az új név 's' + a szám
        new_name = 's' + str(get_state_number(representative))
        for state in group:
            state_mapping[state] = new_name

    # Új komponensek generálása
    new_states = sorted(list(set(state_mapping.values())), key=get_state_number)
    new_start_state = state_mapping[start_state]
    new_accept_states = sorted(list(set([state_mapping[s] for s in accept_states])), key=get_state_number)

    # Új átmenetek generálása
    new_transitions = set()
    for src, sym, dest in transitions:
        if src in state_mapping and dest in state_mapping:
            new_transitions.add((state_mapping[src], sym, state_mapping[dest]))

    # Átmenetek rendezése: forrás, szimbólum, cél (ábécé sorrend a specifikáció szerint, de 'sX' formátumban
    # a feladat sorszám szerinti vagy string szerinti rendezést kér-e? A string szerinti 's10' < 's2' elronthatja,
    # de a python default string rendezése q0 1 q2 formátumra van kitalálva. Mi a biztonság kedvéért a számok szerint rendezünk az s után, majd szimbólum.
    # A feladat ezt írja: "először a kiindulási állapotok alapján, majd az átmenet címkéje...".

    sorted_transitions = sorted(list(new_transitions),
                                key=lambda x: (get_state_number(x[0]), x[1], get_state_number(x[2])))

    return new_states, alphabet, new_start_state, new_accept_states, sorted_transitions


def simple_rename_dfa(states, alphabet, start_state, accept_states, transitions):
    def rename(s):
        return 's' + str(get_state_number(s))

    new_states = [rename(s) for s in states]
    new_start_state = rename(start_state)
    new_accept_states = [rename(s) for s in accept_states]

    new_transitions = set()
    for src, sym, dest in transitions:
        new_transitions.add((rename(src), sym, rename(dest)))

    sorted_transitions = sorted(list(new_transitions),
                                key=lambda x: (get_state_number(x[0]), x[1], get_state_number(x[2])))
    return new_states, alphabet, new_start_state, new_accept_states, sorted_transitions


def write_dfa(filepath, states, alphabet, start_state, accept_states, transitions):
    with open(filepath, 'w') as f:
        f.write(" ".join(states) + "\n")
        f.write(" ".join(alphabet) + "\n")
        f.write(start_state + "\n")
        f.write(" ".join(accept_states) + "\n")
        for src, sym, dest in transitions:
            f.write(f"{src} {sym} {dest}\n")


def main():
    args = parse_args()

    states, alphabet, start_state, accept_states, transitions = load_dfa(args.input)

    if args.mini:
        n_s, n_a, n_st, n_acc, n_t = minimize_dfa(states, alphabet, start_state, accept_states, transitions)
    else:
        # Ha a --mini nincs megadva, feltételezzük, hogy csak át kell nevezni
        n_s, n_a, n_st, n_acc, n_t = simple_rename_dfa(states, alphabet, start_state, accept_states, transitions)

    write_dfa(args.output, n_s, n_a, n_st, n_acc, n_t)


if __name__ == "__main__":
    main()