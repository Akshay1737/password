#include <bits/stdc++.h>
#include <chrono>
using namespace std;
using namespace std::chrono;

// ===== Settings =====
const int MAX_LEN = 12;
const string SUFFIX_ALPHABET = "0123456789!@#$*/";
const long long MAX_FILE_SIZE = 500LL * 1024 * 1024; // 500 MB

// Generate all case permutations of a string
void case_variants(const string &word, vector<string> &results, int index = 0, string current = "") {
    if (index == word.size()) {
        results.push_back(current);
        return;
    }
    char ch = word[index];
    if (isalpha(ch)) {
        case_variants(word, results, index + 1, current + (char)tolower(ch));
        case_variants(word, results, index + 1, current + (char)toupper(ch));
    } else {
        case_variants(word, results, index + 1, current + ch);
    }
}

// Generate all suffixes up to max_extra length
void generate_suffixes(int max_extra, vector<string> &suffixes) {
    suffixes.push_back(""); // empty suffix
    for (int len = 1; len <= max_extra; len++) {
        int n = SUFFIX_ALPHABET.size();
        vector<int> indices(len, 0);
        while (true) {
            string s;
            for (int i = 0; i < len; i++) s += SUFFIX_ALPHABET[indices[i]];
            suffixes.push_back(s);
            // increment indices
            int pos = len - 1;
            while (pos >= 0) {
                indices[pos]++;
                if (indices[pos] < n) break;
                indices[pos] = 0;
                pos--;
            }
            if (pos < 0) break;
        }
    }
}

int main() {
    string input;
    cout << "Enter base strings separated by commas (e.g., akshay,hello): ";
    getline(cin, input);
    vector<string> words;
    stringstream ss(input);
    string token;
    while (getline(ss, token, ',')) {
        token.erase(remove(token.begin(), token.end(), ' '), token.end());
        if (!token.empty()) words.push_back(token);
    }
    if (words.empty()) {
        cout << "No valid input.\n";
        return 0;
    }

    // Count total combinations and estimated memory
    long long total_combos = 0;
    long long total_bytes = 0;
    for (string w : words) {
        int alpha_count = count_if(w.begin(), w.end(), ::isalpha);
        long long base_variants = 1LL << alpha_count;
        int max_extra = max(0, MAX_LEN - (int)w.size());
        long long A = SUFFIX_ALPHABET.size();
        long long suffix_combos = 0;
        long long bytes = 0;
        for (int k = 0; k <= max_extra; k++) {
            long long c = pow(A, k);
            suffix_combos += c;
            bytes += (w.size() + k + 1) * c; // +1 for newline
        }
        total_combos += base_variants * suffix_combos;
        total_bytes += base_variants * bytes;
        cout << "'" << w << "': " << base_variants * suffix_combos << " combos, ~" << (double)(base_variants * bytes) / (1024*1024*1024) << " GB\n";
    }
    cout << "\nTOTAL: " << total_combos << " combos, ~" << (double)total_bytes / (1024*1024*1024) << " GB\n";

    char proceed;
    cout << "Proceed to generate? (y/n): ";
    cin >> proceed;
    if (proceed != 'y') return 0;

    // Generate passwords and write to files
    auto start = high_resolution_clock::now();
    long long processed = 0;
    long long written_bytes = 0;
    int file_index = 1;
    ofstream fout("passwords_1.txt");

    for (string w : words) {
        vector<string> base_variants;
        case_variants(w, base_variants);
        int max_extra = max(0, MAX_LEN - (int)w.size());
        vector<string> suffixes;
        generate_suffixes(max_extra, suffixes);

        for (string base : base_variants) {
            for (string suf : suffixes) {
                string line = base + suf + "\n";
                fout << line;
                written_bytes += line.size();
                processed++;

                if (written_bytes > MAX_FILE_SIZE) {
                    fout.close();
                    file_index++;
                    written_bytes = 0;
                    fout.open("passwords_" + to_string(file_index) + ".txt");
                }

                if (processed % 10000 == 0) {
                    auto now = high_resolution_clock::now();
                    double elapsed = duration<double>(now - start).count();
                    double remaining = elapsed / processed * (total_combos - processed);
                    cout << "Progress: " << processed << "/" << total_combos 
                         << " | Elapsed: " << elapsed << "s | Remaining: " << remaining << "s\r";
                    cout.flush();
                }
            }
        }
    }
    fout.close();
    auto end = high_resolution_clock::now();
    cout << "\n✅ Done! Files: passwords_1.txt to passwords_" << file_index << ".txt\n";
    cout << "⏱ Total time: " << duration<double>(end - start).count() << "s\n";

    return 0;
}
