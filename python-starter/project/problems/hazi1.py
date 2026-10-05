import argparse
import sys


def main():
    # Parancssori argumentumok beállítása
    parser = argparse.ArgumentParser(description="DFA Szimulátor")
    parser.add_argument("--input", required=True, help="A bemeneti fájl, amely tartalmazza az automata adatait.")
    parser.add_argument("--output", required=True, help="A kimeneti fájl, amelybe az eredményeket írja.")
    parser.add_argument("--check", required=True, help="Vesszővel elválasztott szavak listája (pl. a,ab,abc).")
    args = parser.parse_args()

    # 1. Bemeneti fájl beolvasása
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print(f"Hiba: A '{args.input}' fájl nem található.")
        sys.exit(1)

    if len(lines) < 4:
        print("Hiba: A bemeneti fájl formátuma érvénytelen (túl kevés sor).")
        sys.exit(1)

    # Automata adatainak kinyerése
    # states = lines[0].split()  # Nincs rá szükség a szimulációhoz
    # alphabet = lines[1].split() # Nincs rá szükség a szimulációhoz
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
    words_to_check = args.check.split(',')
    results = []

    for word in words_to_check:
        current_state = start_state
        is_valid_path = True

        for char in word:
            # Ha van átmenet az adott állapotból a beolvasott karakterrel
            if (current_state, char) in transitions:
                current_state = transitions[(current_state, char)]
            else:
                # Nincs átmenet, az automata elakad (elutasítja a szót)
                is_valid_path = False
                break

        # Ha végig tudtunk menni a szón, és a végső állapot elfogadó állapot
        if is_valid_path and current_state in accept_states:
            results.append("IGEN")
        else:
            results.append("NEM")

    # 3. Eredmények kiírása a fájlba
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            for res in results:
                f.write(f"{res}\n")
    except IOError:
        print(f"Hiba: Nem sikerült írni a '{args.output}' fájlba.")
        sys.exit(1)


if __name__ == "__main__":
    main()