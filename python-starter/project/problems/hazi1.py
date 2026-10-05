from project.problem import Problem


class DfaSimulator(Problem):
    def initialize_parser(self, parser):
        # Itt adjuk hozzá a feladathoz tartozó specifikus argumentumot
        parser.add_argument("--check", type=str, help="Vesszővel elválasztott szavak listája")

    def is_chosen_problem(self, args):
        # Ez mondja meg a főprogramnak, hogy ezt a feladatot választottuk-e.
        # Ha a parancssorban szerepel a --check, akkor ez a mi feladatunk.
        return getattr(args, 'check', None) is not None

    def run(self, args):
        # A futtatandó logika, az input, output és check argumentumokkal
        input_file = args.input
        output_file = args.output
        check_words_str = args.check

        if not input_file or not output_file or not check_words_str:
            return

        # 1. Bemeneti fájl beolvasása
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            return

        if len(lines) < 4:
            return

        # Automata adatainak kinyerése
        start_state = lines[2].strip()
        accept_states = set(lines[3].split())

        # Átmenetek beolvasása
        transitions = {}
        for line in lines[4:]:
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 3:
                src, symbol, dest = parts[0], parts[1], parts[2]
                transitions[(src, symbol)] = dest

        # 2. Szavak ellenőrzése
        words_to_check = check_words_str.split(',')
        results = []

        for word in words_to_check:
            current_state = start_state
            is_valid_path = True

            for char in word:
                if (current_state, char) in transitions:
                    current_state = transitions[(current_state, char)]
                else:
                    is_valid_path = False
                    break

            if is_valid_path and current_state in accept_states:
                results.append("IGEN")
            else:
                results.append("NEM")

        # 3. Eredmények kiírása
        with open(output_file, 'w', encoding='utf-8') as f:
            for res in results:
                f.write(f"{res}\n")