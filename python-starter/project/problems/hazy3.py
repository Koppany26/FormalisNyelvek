import sys


def load_dfa(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
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

        # Alapvető hibakezelés
        if src not in states or dest not in states:
            print(f"Error: Transition state not in state list: {src} or {dest}")
            sys.exit(1)
        if symbol not in alphabet:
            print(f"Error: Transition symbol not in alphabet: {symbol}")
            sys.exit(1)

        transitions.append((src, symbol, dest))

    return states, alphabet, start_state, accept_states, transitions


def get_state_number(state_str):
    digits = "".join([c for c in state_str if c.isdigit()])
    return int(digits) if digits else 0


def minimize_dfa(states, alphabet, start_state, accept_states, transitions):
    trans_map = {}
    for src, sym, dest in transitions:
        trans_map[(src, sym)] = dest

    # 1. Lépés: Elérhetetlen állapotok eltávolítása BFS-sel
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

    if start_state not in reachable:
        reachable.add(start_state)

    # 2. Lépés: Hopcroft/Moore particionálás
    P = [accept_states, set(states) - accept_states]
    P = [p for p in P if p]

    W = list(P)

    while W:
        A = W.pop(0)
        for sym in alphabet:
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

    state_mapping = {}
    for group in P:
        sorted_group = sorted(list(group), key=get_state_number)
        representative = sorted_group[0]
        new_name = 's' + str(get_state_number(representative))
        for state in group:
            state_mapping[state] = new_name

    new_states = sorted(list(set(state_mapping.values())), key=get_state_number)
    new_start_state = state_mapping[start_state]
    new_accept_states = sorted(list(set([state_mapping[s] for s in accept_states if s in state_mapping])), key=get_state_number)

    new_transitions = set()
    for src, sym, dest in transitions:
        if src in state_mapping and dest in state_mapping:
            new_transitions.add((state_mapping[src], sym, state_mapping[dest]))

    sorted_transitions = sorted(
        list(new_transitions),
        key=lambda x: (get_state_number(x[0]), x[1], get_state_number(x[2]))
    )

    return new_states, alphabet, new_start_state, new_accept_states, sorted_transitions


def simple_rename_dfa(states, alphabet, start_state, accept_states, transitions):
    def rename(s):
        return 's' + str(get_state_number(s))

    reachable = set([start_state])
    queue = [start_state]
    trans_map = {(src, sym): dest for src, sym, dest in transitions}
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

    new_states = sorted(list(set([rename(s) for s in states])), key=get_state_number)
    new_start_state = rename(start_state)
    new_accept_states = sorted(list(set([rename(s) for s in accept_states])), key=get_state_number)

    new_transitions = set()
    for src, sym, dest in transitions:
        if src in reachable and dest in reachable:
            new_transitions.add((rename(src), sym, rename(dest)))

    sorted_transitions = sorted(
        list(new_transitions),
        key=lambda x: (get_state_number(x[0]), x[1], get_state_number(x[2]))
    )
    return new_states, alphabet, new_start_state, new_accept_states, sorted_transitions


def write_dfa(filepath, states, alphabet, start_state, accept_states, transitions):
    if not filepath:
        return
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(" ".join(states) + "\n")
        f.write(" ".join(alphabet) + "\n")
        f.write(start_state + "\n")
        f.write(" ".join(accept_states) + "\n")
        for src, sym, dest in transitions:
            f.write(f"{src} {sym} {dest}\n")


def main():
    # Egyszerű manuális argumentumkezelés argparse nélkül (sys.argv alapú)
    input_file = None
    output_file = None
    mini = False

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--input' and i + 1 < len(sys.argv):
            input_file = sys.argv[i + 1]
            i += 1
        elif arg == '--output' and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 1
        elif arg == '--mini':
            mini = True
        i += 1

    if not input_file:
        sys.exit(0)

    states, alphabet, start_state, accept_states, transitions = load_dfa(input_file)

    if mini:
        n_s, n_a, n_st, n_acc, n_t = minimize_dfa(states, alphabet, start_state, accept_states, transitions)
        write_dfa(output_file, n_s, n_a, n_st, n_acc, n_t)
    else:
        n_s, n_a, n_st, n_acc, n_t = simple_rename_dfa(states, alphabet, start_state, accept_states, transitions)
        write_dfa(output_file, n_s, n_a, n_st, n_acc, n_t)


if __name__ == "__main__":
    main()