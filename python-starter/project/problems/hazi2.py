from project.problem import Problem
import sys
import collections


class DeterminizalasProblem(Problem):

    def initialize_parser(self, parser):
        """
        Hozzáadjuk a specifikus parancssori argumentumot ehhez a feladathoz.
        Az --input és --output argumentumokat a main.py már hozzáadta.
        """
        parser.add_argument('--det', action='store_true', help='Jelezzuk, hogy determinizalni kell az adott automatat')

    def is_chosen_problem(self, args):
        """
        Eldöntjük, hogy ez a feladat lett-e kiválasztva a parancssorból.
        """
        return args.det

    def run(self, args):
        """
        A feladat tényleges végrehajtása.
        """
        input_file = args.input
        output_file = args.output

        if not input_file or not output_file:
            print("Hiba: Az --input es --output argumentumok megadasa kotelezo a --det melle!", file=sys.stderr)
            sys.exit(1)

        # 1. Fájl beolvasása
        try:
            with open(input_file, 'r', encoding='utf-8') as fin:
                lines = [line.strip() for line in fin if line.strip()]
        except IOError:
            print("Hiba: Nem lehet megnyitni a bemeneti fajlt!", file=sys.stderr)
            sys.exit(1)

        if len(lines) < 4:
            print("Hiba: Hianyos bemeneti fajl!", file=sys.stderr)
            sys.exit(1)

        # 2. NFA adatok feldolgozása
        states = lines[0].split()
        alphabet = lines[1].split()
        start_state = lines[2].split()[0]
        accept_states = lines[3].split()

        valid_states = set(states)
        valid_symbols = set(alphabet)
        nfa_accept_states = set(accept_states)

        # nfa_transitions[from_state][symbol] = set(to_states)
        nfa_transitions = collections.defaultdict(lambda: collections.defaultdict(set))

        for line in lines[4:]:
            parts = line.split()
            if len(parts) == 3:
                from_state, symbol, to_state = parts
                # Alapvető hibakezelés
                if from_state not in valid_states or to_state not in valid_states or symbol not in valid_symbols:
                    print(f"Hiba: Ervenytelen allapot vagy szimbolum: {from_state} {symbol} {to_state}",
                          file=sys.stderr)
                    sys.exit(1)

                nfa_transitions[from_state][symbol].add(to_state)

        # 3. Determinizálás (részhalmaz-konstrukció)
        subset_to_name = {}
        id_to_subset = []

        initial_subset = frozenset([start_state])
        subset_to_name[initial_subset] = "s0"
        id_to_subset.append(initial_subset)

        queue = collections.deque([0])
        dfa_transitions = []
        next_state_id = 1

        while queue:
            curr_id = queue.popleft()
            curr_subset = id_to_subset[curr_id]
            curr_name = subset_to_name[curr_subset]

            for sym in alphabet:
                next_subset = set()
                for state in curr_subset:
                    if sym in nfa_transitions[state]:
                        next_subset.update(nfa_transitions[state][sym])

                if next_subset:
                    next_subset_frozen = frozenset(next_subset)
                    if next_subset_frozen not in subset_to_name:
                        new_name = f"s{next_state_id}"
                        subset_to_name[next_subset_frozen] = new_name
                        id_to_subset.append(next_subset_frozen)
                        queue.append(next_state_id)
                        next_state_id += 1

                    dfa_transitions.append((curr_name, sym, subset_to_name[next_subset_frozen]))

        # 4. DFA adatok előkészítése a kiíráshoz
        dfa_states = [f"s{i}" for i in range(len(id_to_subset))]

        dfa_accept_states = []
        for i, subset in enumerate(id_to_subset):
            # Ha a részhalmaz tartalmaz NFA végállapotot, akkor a DFA állapot is végállapot
            if not nfa_accept_states.isdisjoint(subset):
                dfa_accept_states.append(f"s{i}")

        # Lexikografikus rendezés a kimenethez
        dfa_states.sort()
        dfa_accept_states.sort()
        dfa_transitions.sort(key=lambda x: (x[0], x[1], x[2]))

        # 5. Eredmény kiírása a fájlba
        try:
            with open(output_file, 'w', encoding='utf-8') as fout:
                fout.write(" ".join(dfa_states) + "\n")
                fout.write(" ".join(alphabet) + "\n")
                fout.write("s0\n")
                fout.write(" ".join(dfa_accept_states) + "\n")

                for from_st, sym, to_st in dfa_transitions:
                    fout.write(f"{from_st} {sym} {to_st}\n")
        except IOError:
            print("Hiba: Nem lehet megnyitni a kimeneti fajlt!", file=sys.stderr)
            sys.exit(1)