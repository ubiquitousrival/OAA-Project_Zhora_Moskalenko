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

class Interpreter:
    def __init__(self):
        self.sets = {}
        self.id_pattern = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$")

    def validate_identifier(self, name):
        return bool(self.id_pattern.match(name))

    def execute(self, command_text):
        cmd = command_text.strip()
        if not cmd:
            return

        create_re = re.compile(r"^CREATE\s+([a-zA-Z0-9_]+)$", re.IGNORECASE)
        insert_re = re.compile(r"^INSERT\s+([a-zA-Z0-9_]+)\s+\"([^\"]*)\"$", re.IGNORECASE)
        contains_re = re.compile(r"^CONTAINS\s+([a-zA-Z0-9_]+)\s+\"([^\"]*)\"$", re.IGNORECASE)
        print_re = re.compile(r"^PRINT_TREE\s+([a-zA-Z0-9_]+)$", re.IGNORECASE)
        
        search_match = re.match(r"^SEARCH\s+([a-zA-Z0-9_]+)(.*)$", cmd, re.IGNORECASE)

        if m := create_re.match(cmd):
            self._cmd_create(m.group(1))
        elif m := insert_re.match(cmd):
            self._cmd_insert(m.group(1), m.group(2))
        elif m := contains_re.match(cmd):
            self._cmd_contains(m.group(1), m.group(2))
        elif m := print_re.match(cmd):
            self._cmd_print_tree(m.group(1))
        elif search_match:
            self._cmd_search(search_match.group(1), search_match.group(2).strip())
        else:
            print("Error: Invalid command syntax")

    def _cmd_create(self, name):
        if not self.validate_identifier(name):
            print(f"Error: Invalid set name '{name}'")
            return
        if name in self.sets:
            print(f"Error: Set '{name}' already exists")
        else:
            self.sets[name] = Trie()
            print(f"Set {name} has been created")

    def _cmd_insert(self, name, value):
        if name not in self.sets:
            print(f"Error: Set '{name}' does not exist")
            return
        self.sets[name].insert(value)
        print(f"String has been added to {name}.")

    def _cmd_contains(self, name, value):
        if name not in self.sets:
            print(f"Error: Set '{name}' does not exist")
            return
        result = self.sets[name].contains(value)
        print("TRUE" if result else "FALSE")

    def _cmd_print_tree(self, name):
        if name not in self.sets:
            print(f"Error: Set '{name}' does not exist")
            return
        self.sets[name].print_tree()

    def _cmd_search(self, name, options_str):
        if name not in self.sets:
            print(f"Error: Set '{name}' does not exist")
            return

        descending = False
        
        tokens = options_str.split()
        if tokens and tokens[-1].upper() == "DESC":
            descending = True
            options_str = " ".join(tokens[:-1])
        elif tokens and tokens[-1].upper() == "ASC":
            options_str = " ".join(tokens[:-1])

        result_words = []
        if not options_str:
            result_words = self.sets[name].get_all_words()
        elif options_str.upper().startswith("WHERE"):
            condition = options_str[6:].strip()
            
            between_re = re.compile(r"^BETWEEN\s+\"([^\"]*)\"\s*,\s*\"([^\"]*)\"$", re.IGNORECASE)
            match_re = re.compile(r"^MATCH\s+\"([^\"]*)\"$", re.IGNORECASE)
            
            if m := between_re.match(condition):
                start_val, end_val = m.group(1), m.group(2)
                all_words = self.sets[name].get_all_words()
                result_words = [w for w in all_words if start_val <= w <= end_val]
            elif m := match_re.match(condition):
                pattern = m.group(1)
                result_words = self.sets[name].search_match(pattern)
            else:
                print("Error: Invalid WHERE clause syntax")
                return
        else:
            print("Error: Invalid SEARCH syntax")
            return

        if descending:
            result_words.reverse()
            
        for w in result_words:
            print(f'"{w}"')


if __name__ == "__main__":
    interpreter = Interpreter()
    buffer = ""
    print("Trie Set Database. Enter commands")
    
    try:
        for line in sys.stdin:
            if ';' in line:
                idx = line.find(';')
                buffer += " " + line[:idx]
                interpreter.execute(buffer)
                buffer = ""
            else:
                buffer += " " + line.strip()
    except EOFError:
        pass