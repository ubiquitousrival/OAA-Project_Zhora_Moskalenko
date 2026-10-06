import re
import sys

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True

    def contains(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end

    def print_tree(self):
        print("[root]")
        self._print_tree_recursive(self.root, "")

    def _print_tree_recursive(self, node, prefix):
        keys = sorted(node.children.keys())
        for i, char in enumerate(keys):
            is_last = (i == len(keys) - 1)
            connector = "L-- " if is_last else "|-- "
            print(f"{prefix}{connector}\"{char}\"")
            
            extension = "    " if is_last else "|   "
            self._print_tree_recursive(node.children[char], prefix + extension)

    def get_all_words(self, node=None, prefix=""):
        if node is None:
            node = self.root
        
        words = []
        if node.is_end:
            words.append(prefix)
            
        for char in sorted(node.children.keys()):
            words.extend(self.get_all_words(node.children[char], prefix + char))
        return words

    def search_match(self, pattern, node=None, current_word="", idx=0):
        if node is None:
            node = self.root

        if idx == len(pattern):
            return [current_word] if node.is_end else []

        char = pattern[idx]
        words = []

        if char == '*':
            return self.get_all_words(node, current_word)
        elif char == '?':
            for child_char in sorted(node.children.keys()):
                words.extend(self.search_match(pattern, node.children[child_char], current_word + child_char, idx + 1))
        else:
            if char in node.children:
                words.extend(self.search_match(pattern, node.children[char], current_word + char, idx + 1))
        
        return words