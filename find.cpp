#include <bits/stdc++.h>
using namespace std;

bool search_in_files(const string &base_filename, const string &query, string &found_file) {
    int file_index = 1;
    while (true) {
        string filename = base_filename + "_" + to_string(file_index) + ".txt";
        ifstream fin(filename);
        if (!fin) break; // no more files
        string line;
        while (getline(fin, line)) {
            if (line == query) {
                found_file = filename;
                return true;
            }
        }
        file_index++;
    }
    return false;
}

int main() {
    string query;
    cout << "Enter string to search: ";
    getline(cin, query);
    string found_file;
    bool found = search_in_files("passwords", query, found_file);
    if (found)
        cout << "✅ '" << query << "' found in '" << found_file << "'\n";
    else
        cout << "❌ '" << query << "' NOT found in any file\n";
    return 0;
}

