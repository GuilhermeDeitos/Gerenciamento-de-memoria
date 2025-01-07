#include <iostream>
#include <vector>
#include <unordered_map>
#include <deque>
#include <random>
#include <string>
#include <sstream>
#include <algorithm>
#include <fstream>

using namespace std;

// Enum para políticas de substituição
enum ReplacementPolicy {
    FIFO,
    LRU,
    RANDOM
};

// Classe TLB (Translation Lookaside Buffer)
class TLB {
private:
    size_t size;                         // Tamanho da TLB
    ReplacementPolicy policy;            // Política de substituição
    deque<string> entries;               // Entradas da TLB (FIFO ou LRU)
    unordered_map<string, int> lru_map;  // Suporte para LRU
    mt19937 rng;                         // Gerador para RANDOM
    int hits;                            // Número de hits
    int misses;                          // Número de misses

public:
    TLB(size_t size, ReplacementPolicy policy) 
        : size(size), policy(policy), hits(0), misses(0) {
        rng.seed(random_device{}());
    }

    void access(string page) {
        if (find(entries.begin(), entries.end(), page) != entries.end()) {
            hits++;
            if (policy == LRU) {
                entries.erase(remove(entries.begin(), entries.end(), page));
                entries.push_back(page);
            }
        } else {
            misses++;
            if (entries.size() < size) {
                entries.push_back(page);
            } else {
                if (policy == FIFO) {
                    entries.pop_front();
                } else if (policy == LRU) {
                    entries.pop_front();
                } else if (policy == RANDOM) {
                    uniform_int_distribution<size_t> dist(0, entries.size() - 1);
                    size_t victim = dist(rng);
                    entries.erase(entries.begin() + victim);
                }
                entries.push_back(page);
            }
        }
    }

    double getMissRate() const {
        return static_cast<double>(misses) / (hits + misses);
    }

    void reset() {
        entries.clear();
        hits = 0;
        misses = 0;
    }
};

// Função para carregar a reference string de um arquivo
vector<string> loadReferenceStringFromFile(const string& filename) {
    vector<string> referenceString;
    string page;
    ifstream file(filename);

    while (getline(file, page)) {
        referenceString.push_back(page);
    }
    return referenceString;
}

// Função para simular TLB
void simulateTLB(const vector<string>& referenceString, size_t tlbSize) {
    vector<ReplacementPolicy> policies = {FIFO, LRU, RANDOM};
    vector<string> policyNames = {"FIFO", "LRU", "RANDOM"};

    for (size_t i = 0; i < policies.size(); i++) {
        TLB tlb(tlbSize, policies[i]);
        for (const string& page : referenceString) {
            tlb.access(page);
        }
        cout << "Policy: " << policyNames[i] << ", Miss Rate: " << tlb.getMissRate() * 100 << "%" << endl;
    }
}

// Função principal
int main(int argc, char* argv[]) {
    if (argc != 3) {
        cout << "Usage: " << argv[0] << " <reference_file> <tlb_size>" << endl;
        return 1;
    }

    string referenceFile = argv[1];
    size_t tlbSize = stoi(argv[2]);

    vector<string> referenceString = loadReferenceStringFromFile(referenceFile);
    simulateTLB(referenceString, tlbSize);

    return 0;
}
