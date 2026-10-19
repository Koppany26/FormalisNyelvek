//
// Created by User on 2026. 10. 19..
//

#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <map>
#include <set>
#include <queue>
#include <algorithm>

using namespace std;

// Segédfüggvény egy sornyi szóközökkel elválasztott string beolvasására
vector<string> readLineTokens(ifstream& file) {
    string line;
    vector<string> tokens;
    if (getline(file, line)) {
        stringstream ss(line);
        string token;
        while (ss >> token) {
            tokens.push_back(token);
        }
    }
    return tokens;
}

int main(int argc, char* argv[]) {
    string input_file = "";
    string output_file = "";
    bool det_flag = false;

    // Parancssori argumentumok feldolgozása
    for (int i = 1; i < argc; ++i) {
        string arg = argv[i];
        if (arg == "--input" && i + 1 < argc) {
            input_file = argv[++i];
        } else if (arg == "--output" && i + 1 < argc) {
            output_file = argv[++i];
        } else if (arg == "--det") {
            det_flag = true;
        }
    }

    if (input_file.empty() || output_file.empty() || !det_flag) {
        cerr << "Hiba: Hibas parancssori argumentumok!" << endl;
        cerr << "Hasznalat: ./project --input <file> --output <file> --det" << endl;
        return 1;
    }

    ifstream fin(input_file);
    if (!fin.is_open()) {
        cerr << "Hiba: Nem lehet megnyitni a bemeneti fajlt!" << endl;
        return 1;
    }

    // NFA adatok beolvasása
    vector<string> states = readLineTokens(fin);
    vector<string> alphabet = readLineTokens(fin);
    vector<string> start_state_vec = readLineTokens(fin);
    vector<string> accept_states = readLineTokens(fin);

    if (start_state_vec.empty()) {
        cerr << "Hiba: Hianyzik a kezdoallapot!" << endl;
        return 1;
    }
    string start_state = start_state_vec[0];

    // Érvényesség ellenőrzéséhez set-ek létrehozása
    set<string> valid_states(states.begin(), states.end());
    set<string> valid_symbols(alphabet.begin(), alphabet.end());
    set<string> nfa_accept_states(accept_states.begin(), accept_states.end());

    // NFA átmenetek beolvasása: from_state -> (symbol -> set of to_states)
    map<string, map<string, set<string>>> nfa_transitions;
    string from, symbol, to;
    while (fin >> from >> symbol >> to) {
        // Hibakezelés (alapvető)
        if (valid_states.find(from) == valid_states.end() ||
            valid_states.find(to) == valid_states.end() ||
            valid_symbols.find(symbol) == valid_symbols.end()) {
            cerr << "Hiba: Ervenytelen allapot vagy szimbolum az atmeneteknel: "
                 << from << " " << symbol << " " << to << endl;
            return 1;
        }
        nfa_transitions[from][symbol].insert(to);
    }
    fin.close();

    // Determinizálás algoritmus (részhalmaz-konstrukció)
    map<set<string>, string> subset_to_name;
    vector<set<string>> id_to_subset;
    queue<int> q;

    set<string> initial_subset = {start_state};
    string start_dfa_name = "s0";
    subset_to_name[initial_subset] = start_dfa_name;
    id_to_subset.push_back(initial_subset);
    q.push(0);

    struct DfaTransition {
        string from;
        string symbol;
        string to;
    };
    vector<DfaTransition> dfa_transitions;
    int next_state_id = 1;

    while (!q.empty()) {
        int curr_id = q.front();
        q.pop();

        set<string> curr_subset = id_to_subset[curr_id];
        string curr_name = subset_to_name[curr_subset];

        for (const string& sym : alphabet) {
            set<string> next_subset;
            for (const string& state : curr_subset) {
                if (nfa_transitions[state].count(sym)) {
                    for (const string& next_state : nfa_transitions[state][sym]) {
                        next_subset.insert(next_state);
                    }
                }
            }

            if (!next_subset.empty()) {
                if (subset_to_name.find(next_subset) == subset_to_name.end()) {
                    string new_name = "s" + to_string(next_state_id++);
                    subset_to_name[next_subset] = new_name;
                    id_to_subset.push_back(next_subset);
                    q.push(next_state_id - 1);
                }
                dfa_transitions.push_back({curr_name, sym, subset_to_name[next_subset]});
            }
        }
    }

    // Eredmény kiírásának előkészítése
    vector<string> dfa_states;
    vector<string> dfa_accept_states;

    for (int i = 0; i < id_to_subset.size(); ++i) {
        string state_name = "s" + to_string(i);
        dfa_states.push_back(state_name);

        // Egy DFA állapot elfogadó, ha tartalmaz legalább egy NFA elfogadó állapotot
        bool is_accept = false;
        for (const string& s : id_to_subset[i]) {
            if (nfa_accept_states.count(s)) {
                is_accept = true;
                break;
            }
        }
        if (is_accept) {
            dfa_accept_states.push_back(state_name);
        }
    }

    // Átmenetek ábécé sorrendbe rendezése (szigorúan string lexicografikus a feladat szerint)
    sort(dfa_transitions.begin(), dfa_transitions.end(), [](const DfaTransition& a, const DfaTransition& b) {
        if (a.from != b.from) return a.from < b.from;
        if (a.symbol != b.symbol) return a.symbol < b.symbol;
        return a.to < b.to;
    });

    sort(dfa_states.begin(), dfa_states.end());
    sort(dfa_accept_states.begin(), dfa_accept_states.end());

    // Kiírás a kimeneti fájlba
    ofstream fout(output_file);
    if (!fout.is_open()) {
        cerr << "Hiba: Nem lehet megnyitni a kimeneti fajlt!" << endl;
        return 1;
    }

    // 1. Állapotok
    for (size_t i = 0; i < dfa_states.size(); ++i) {
        fout << dfa_states[i] << (i + 1 == dfa_states.size() ? "" : " ");
    }
    fout << "\n";

    // 2. Ábécé
    for (size_t i = 0; i < alphabet.size(); ++i) {
        fout << alphabet[i] << (i + 1 == alphabet.size() ? "" : " ");
    }
    fout << "\n";

    // 3. Kezdőállapot
    fout << start_dfa_name << "\n";

    // 4. Végállapotok
    for (size_t i = 0; i < dfa_accept_states.size(); ++i) {
        fout << dfa_accept_states[i] << (i + 1 == dfa_accept_states.size() ? "" : " ");
    }
    fout << "\n";

    // 5. Átmenetek
    for (const auto& t : dfa_transitions) {
        fout << t.from << " " << t.symbol << " " << t.to << "\n";
    }

    fout.close();
    return 0;
}