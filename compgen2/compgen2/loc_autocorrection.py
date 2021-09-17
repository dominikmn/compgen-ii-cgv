# from Levenshtein import distance
from functools import lru_cache


from .trie_levenshtein import TrieNode


class LocCorrection:
    def __init__(self, loc_list):
        """
        :param loc_list:  list of string
        """
        self.loc_list = loc_list
        self.word_count = 0
        self.trie = TrieNode()
        self._dict2trie()

    @staticmethod
    @lru_cache(1000000)
    def from_list(loc_list):
        return LocCorrection(loc_list)

    def _dict2trie(self):
        # read dictionary file into a trie
        for word in self.loc_list:
            self.word_count += 1
            self.trie.insert(word.lower())
        # The search function returns a list of all words that are less than the given
        # maximum distance from the target word
        
    def get_best_candidates(self, word: str, max_cost: int) -> list[tuple[str, int]]:
        min_cost = 1
        while min_cost <= max_cost:
            candidates = self.search(word, min_cost)
            if candidates:
                return candidates
            min_cost += 1
        return []
    
    def search(self, word, cost, exclude_operations=None) -> list[tuple[str, int]]:
        """

        :param word: string
        :param cost: supports int, range, or dictionary (key: regex, value: range/int)
        param exclude_operations: None / subset of ["insert", "delete", "replace"]
        :return:
        """
        # build first row
        word = word.lower()
        currentRow = range(len(word) + 1)
        results = []
        # recursively search each branch of the trie
        for letter in self.trie.children:
            self._searchRecursive(
                self.trie.children[letter],
                letter,
                word,
                currentRow,
                results,
                cost,
                exclude_operations,
            )
        return results

    def _searchRecursive(
        self, node, letter, word, previousRow, results, cost, exclude_operations=None
    ):
        columns = len(word) + 1
        currentRow = [previousRow[0] + 1]
        # Build one row for the letter, with a column for each letter in the target
        # word, plus one for the empty string at column 0
        for column in range(1, columns):
            insertCost = currentRow[column - 1] + 1
            deleteCost = previousRow[column] + 1
            if word[column - 1] != letter:
                replaceCost = previousRow[column - 1] + 1
            else:
                replaceCost = previousRow[column - 1]
            mode_dict = {
                "insert": insertCost,
                "delete": deleteCost,
                "replace": replaceCost,
            }
            if exclude_operations:
                for op in exclude_operations:
                    del mode_dict[op]
            currentRow.append(min(list(mode_dict.values())))
        # if the last entry in the row indicates the optimal cost is less than the
        # defined cost, and there is a word in this trie node, then add it.
        # exact mode
        if isinstance(cost, int):
            # the cost should be exactly as the input
            defined_cost = cost
            if currentRow[-1] == defined_cost and node.word != None:
                results.append((node.word, currentRow[-1]))
            if min(currentRow) <= defined_cost:
                for letter in node.children:
                    self._searchRecursive(
                        node.children[letter],
                        letter,
                        word,
                        currentRow,
                        results,
                        defined_cost,
                        exclude_operations,
                    )
        elif isinstance(cost, tuple):
            defined_cost = range(cost[0], cost[1])
            for current_cost in defined_cost:
                if len(results) == 0:
                    if currentRow[-1] == current_cost and node.word != None:
                        results.append((node.word, currentRow[-1]))
                    if min(currentRow) <= current_cost:
                        for letter in node.children:
                            self._searchRecursive(
                                node.children[letter],
                                letter,
                                word,
                                currentRow,
                                results,
                                current_cost,
                                exclude_operations,
                            )
        else:
            raise TypeError
        # if any entries in the row are less than the maximum cost, then
        # recursively search each branch of the trie