import unittest
import json
from zss import simple_distance
from zss_json import json_to_tree, count_nodes, tree_error_rate


class TestJson2Tree(unittest.TestCase):
    def test_json_to_tree(self):
        json_str = """
        {"a": ["b", "c"]}
        """
        json_obj = json.loads(json_str)
        tree = json_to_tree(json_obj)
        self.assertEqual(tree.label, "a")
        self.assertEqual(tree.children[0].label, "b")
        self.assertEqual(tree.children[1].label, "c")

    def test_simple_distance(self):
        json_str1 = """
        {"a": ["b", "c"]}
        """
        json_str2 = """
        {"a": ["b", "d"]}
        """
        json_obj1 = json.loads(json_str1)
        json_obj2 = json.loads(json_str2)
        tree1 = json_to_tree(json_obj1)
        tree2 = json_to_tree(json_obj2)
        self.assertEqual(simple_distance(tree1, tree2), 1)

    def test_simple_distance_2(self):
        """More nodes."""
        json_str1 = """
        {"a": ["b", "c"]}
        """
        json_str2 = """
        {"a": ["b", "c", "d"]}
        """
        json_obj1 = json.loads(json_str1)
        json_obj2 = json.loads(json_str2)
        tree1 = json_to_tree(json_obj1)
        tree2 = json_to_tree(json_obj2)
        self.assertEqual(simple_distance(tree1, tree2), 1)

    def test_simple_distance_3(self):
        """Fewer nodes."""
        json_str1 = """
        {"a": ["b", "c"]}
        """
        json_str2 = """
        {"a": "b"}
        """
        json_obj1 = json.loads(json_str1)
        json_obj2 = json.loads(json_str2)
        tree1 = json_to_tree(json_obj1)
        tree2 = json_to_tree(json_obj2)
        self.assertEqual(simple_distance(tree1, tree2), 1)

    def test_simple_distance_4(self):
        """Different root."""
        json_str1 = """
        {"a": ["b", "c"]}
        """
        json_str2 = """
        {"d": ["b", "c"]}
        """
        json_obj1 = json.loads(json_str1)
        json_obj2 = json.loads(json_str2)
        tree1 = json_to_tree(json_obj1)
        tree2 = json_to_tree(json_obj2)
        self.assertEqual(simple_distance(tree1, tree2), 1)

    def test_simple_distance_5(self):
        """Different depth.
        Tree 1:
        - a
            - b
            - c
        
        Tree 2:
        - a
            - b
                - c

        The cost should be 2 (delete c, add c).
        """
        json_str1 = """
        {"a": ["b", "c"]}
        """
        json_str2 = """
        {"a": {"b": "c"}}
        """
        json_obj1 = json.loads(json_str1)
        json_obj2 = json.loads(json_str2)
        tree1 = json_to_tree(json_obj1)
        tree2 = json_to_tree(json_obj2)
        self.assertEqual(simple_distance(tree1, tree2), 2)

    def test_dictionary_1(self):
        """Dictionary case.
        Tree 1:
        - entry
            - english
                - hello
            - spanish
                - hola
        
        Tree 2:
        - entry
            - english
                - hello
            - spanish
                - buenos días

        The cost should be 2 (relabel "hola" to "buenos días").
        """
        json_str1 = """
        {"entry": {"english": "hello", "spanish": "hola"}}
        """
        json_str2 = """
        {"entry": {"english": "hello", "spanish": "buenos días"}}
        """
        json_obj1 = json.loads(json_str1)
        json_obj2 = json.loads(json_str2)
        tree1 = json_to_tree(json_obj1)
        tree2 = json_to_tree(json_obj2)
        # print()
        # print_tree(tree1)
        # print_tree(tree2)
        self.assertEqual(simple_distance(tree1, tree2), 1)

    def test_dictionary_2(self):
        """Dictionary case.
        Tree 1:
        - entry
            - english
                - hello
            - spanish
                - hola
        
        Tree 2:
        - entry
            - english
                - hello
            - spanish
                - buenos días
                - hola

        The cost should be 2 (add "buenos días").
        """
        json_str1 = """
        {"entry": {"english": "hello", "spanish": "hola"}}
        """
        json_str2 = """
        {"entry": {"english": "hello", "spanish": ["buenos días", "hola"]}}
        """
        json_obj1 = json.loads(json_str1)
        json_obj2 = json.loads(json_str2)
        tree1 = json_to_tree(json_obj1)
        tree2 = json_to_tree(json_obj2)
        self.assertEqual(simple_distance(tree1, tree2), 1)

    def test_dictionary_3(self):
        """Dictionary case.
        Tree 1:
        - entry
            - english
                - word
                    - dog
                - pronunciation
                    - dɔɡ
            - spanish
                - word
                    - perro
                - pronunciation
                    - pero
        
        Tree 2:
        - entry
            - english
                - word
                    - cat
                - pronunciation
                    - kæt
            - spanish
                - word
                    - gato
                - pronunciation
                    - gato

        The cost should be 4.
        """
        json_str1 = """
        {"entry": {"english": {"word": "dog", "pronunciation": "dɔɡ"}, "spanish": {"word": "perro", "pronunciation": "pero"}}}
        """
        json_str2 = """
        {"entry": {"english": {"word": "cat", "pronunciation": "kæt"}, "spanish": {"word": "gato", "pronunciation": "gato"}}}
        """
        json_obj1 = json.loads(json_str1)
        json_obj2 = json.loads(json_str2)
        tree1 = json_to_tree(json_obj1)
        tree2 = json_to_tree(json_obj2)
        self.assertEqual(simple_distance(tree1, tree2), 4)

    def test_count_nodes_1(self):
        json_str = """
        {"a": ["b", "c"]}
        """
        json_obj = json.loads(json_str)
        tree = json_to_tree(json_obj)
        self.assertEqual(count_nodes(tree), 3)

    def test_count_nodes_2(self):
        """Dictionary case.
        Tree 1:
        - entry
            - english
                - word
                    - dog
                - pronunciation
                    - dɔɡ
            - spanish
                - word
                    - perro
                - pronunciation
                    - pero
        """
        json_str = """
        {"entry": {"english": {"word": "dog", "pronunciation": "dɔɡ"}, "spanish": {"word": "perro", "pronunciation": "pero"}}}
        """
        json_obj = json.loads(json_str)
        tree = json_to_tree(json_obj)
        self.assertEqual(count_nodes(tree), 11)

    def test_tree_error_rate(self):
        json_str1 = """
        {"a": ["b", "c"]}
        """
        json_str2 = """
        {"a": ["b", "d"]}
        """
        json_obj1 = json.loads(json_str1)
        json_obj2 = json.loads(json_str2)
        tree1 = json_to_tree(json_obj1)
        tree2 = json_to_tree(json_obj2)
        self.assertEqual(tree_error_rate(tree1, tree2), 1 / 3)

    def test_tree_error_rate_2(self):
        """Dictionary case.
        Tree 1:
        - entry
            - english
                - word
                    - dog
                - pronunciation
                    - dɔɡ
            - spanish
                - word
                    - perro
                - pronunciation
                    - pero
        
        Tree 2:
        - entry
            - english
                - word
                    - cat
                - pronunciation
                    - kæt
            - spanish
                - word
                    - gato
                - pronunciation
                    - gato

        The tree error rate should be 4 / 11.
        """
        json_str1 = """
        {"entry": {"english": {"word": "dog", "pronunciation": "dɔɡ"}, "spanish": {"word": "perro", "pronunciation": "pero"}}}
        """
        json_str2 = """
        {"entry": {"english": {"word": "cat", "pronunciation": "kæt"}, "spanish": {"word": "gato", "pronunciation": "gato"}}}
        """
        json_obj1 = json.loads(json_str1)
        json_obj2 = json.loads(json_str2)
        tree1 = json_to_tree(json_obj1)
        tree2 = json_to_tree(json_obj2)
        self.assertEqual(tree_error_rate(tree1, tree2), 4 / 11)

    def test_tree_error_rate_3(self):
        """Dictionary case, with missing info.
        Tree 1:
        - entry
            - english
                - word
                    - dog
                - pronunciation
                    - dɔɡ
            - spanish
                - word
                    - perro
                - pronunciation
                    - pero
        
        Tree 2:
        - entry
            - english
                - word
                    - cat
            - spanish
                - word
                    - gato

        The errors are:
        - relabel 'dog' with 'cat'
        - delete 'dɔɡ'
        - delete 'pronunciation'
        - relabel 'perro' with 'gato'
        - delete 'pronunciation'
        - delete 'pero'
        so the tree error rate should be 6 / 11.
        """
        json_str1 = """
        {"entry": {"english": {"word": "dog", "pronunciation": "dɔɡ"}, "spanish": {"word": "perro", "pronunciation": "pero"}}}
        """
        json_str2 = """
        {"entry": {"english": {"word": "cat"}, "spanish": {"word": "gato"}}}
        """
        json_obj1 = json.loads(json_str1)
        json_obj2 = json.loads(json_str2)
        tree1 = json_to_tree(json_obj1)
        tree2 = json_to_tree(json_obj2)
        self.assertEqual(tree_error_rate(tree1, tree2), 6 / 11)

    def test_tree_error_rate_with_string_bonus_1(self):
        """Tree error rate with substring bonus.
        Tree 1:
        - entry
            - english
                - word
                    - dog
                - pronunciation
                    - dɔɡ
            - spanish
                - word
                    - perro
                - pronunciation
                    - pero
        
        Tree 2:
        - entry
            - english
                - word
                    - dog
                - pronunciation
                    - doɡ
            - spanish
                - word
                    - perro
                - pronunciation
                    - pero

        The errors are:
        - relabel 'dog' with 'dɔg', whose CER is 1/3
        so the tree error rate should be 1/3 / 11 = 1 / 33.
        """
        json_str1 = """
        {"entry": {"english": {"word": "dog", "pronunciation": "dɔɡ"}, "spanish": {"word": "perro", "pronunciation": "pero"}}}
        """
        json_str2 = """
        {"entry": {"english": {"word": "dog", "pronunciation": "doɡ"}, "spanish": {"word": "perro", "pronunciation": "pero"}}}
        """
        json_obj1 = json.loads(json_str1)
        json_obj2 = json.loads(json_str2)
        tree1 = json_to_tree(json_obj1)
        tree2 = json_to_tree(json_obj2)
        self.assertAlmostEqual(tree_error_rate(tree1, tree2, substring_bonus=True), 1 / 33)

    def test_tree_error_rate_with_string_bonus_2(self):
        """Tree error rate with substring bonus.
        Tree 1:
        - entry
            - english
                - word
                    - dog
                - pronunciation
                    - dɔɡ
            - spanish
                - word
                    - perro
                - pronunciation
                    - pero
        
        Tree 2:
        - entry
            - english
                - word
                    - dog
                - pronunciation
                    - doɡ
            - spanish
                - word
                    - perra
                - pronunciation
                    - pera

        The errors are:
        - relabel 'dɔɡ' with 'dɔɡ', whose CER is 1/3
        - relabel 'perro' with 'perra', whose CER is 1/5
        - relabel 'pero' with 'pera', whose CER is 1/4
        so the tree error rate should be (1/3 + 1/5 + 1/4) / 11 = 47 / 660.
        """
        json_str1 = """
        {"entry": {"english": {"word": "dog", "pronunciation": "dɔɡ"}, "spanish": {"word": "perro", "pronunciation": "pero"}}}
        """
        json_str2 = """
        {"entry": {"english": {"word": "dog", "pronunciation": "doɡ"}, "spanish": {"word": "perra", "pronunciation": "pera"}}}
        """
        json_obj1 = json.loads(json_str1)
        json_obj2 = json.loads(json_str2)
        tree1 = json_to_tree(json_obj1)
        tree2 = json_to_tree(json_obj2)
        self.assertAlmostEqual(tree_error_rate(tree1, tree2, substring_bonus=True), 47 / 660)


if __name__ == "__main__":
    unittest.main()