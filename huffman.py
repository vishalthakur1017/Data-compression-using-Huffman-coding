import heapq
from collections import Counter, namedtuple
from tkinter import *
from tkinter import filedialog, messagebox
import os
import pickle
import matplotlib.pyplot as plt
import networkx as nx

# Huffman Node 


class Node(namedtuple("Node", ["char", "freq", "left", "right"])):
    def __lt__(self, other):
        return self.freq < other.freq

#  Huffman Coding 


class HuffmanCoding:
    def __init__(self):
        self.codes = {}
        self.reverse_codes = {}

    def build_tree(self, text):
        freq = Counter(text)
        heap = [Node(ch, fr, None, None) for ch, fr in freq.items()]
        heapq.heapify(heap)
        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            merged = Node(None, left.freq + right.freq, left, right)
            heapq.heappush(heap, merged)
        return heap[0]

    def generate_codes(self, node, prefix=""):
        if node is None:
            return
        if node.char:
            self.codes[node.char] = prefix
            self.reverse_codes[prefix] = node.char
        else:
            self.generate_codes(node.left, prefix + "0")
            self.generate_codes(node.right, prefix + "1")

    def encode(self, text):
        tree = self.build_tree(text)
        self.generate_codes(tree)
        encoded_text = ''.join(self.codes[ch] for ch in text)
        return encoded_text, tree

    def decode(self, encoded_text, tree):
        decoded = []
        node = tree
        for bit in encoded_text:
            node = node.left if bit == "0" else node.right
            if node.char:
                decoded.append(node.char)
                node = tree
        return ''.join(decoded)

#  GUI App 


class HuffmanApp:
    def __init__(self, root):
        self.root = root
        self.root.title(" Huffman Compression")
        self.root.geometry("900x650")
        self.huffman = HuffmanCoding()
        self.last_encoded = ""
        self.tree = None

        Label(root, text="Huffman Coding - Advanced Project",
              font=("Arial", 16, "bold")).pack(pady=10)

        self.text_area = Text(root, width=100, height=15, wrap=WORD)
        self.text_area.pack(padx=10, pady=10)

        btn_frame = Frame(root)
        btn_frame.pack(pady=10)
        Button(btn_frame, text="Open File", command=self.load_file,
               bg="#64B5F6").grid(row=0, column=0, padx=10)
        Button(btn_frame, text="Compress", command=self.compress_text,
               bg="#43A047").grid(row=0, column=1, padx=10)
        Button(btn_frame, text="Decompress", command=self.decompress_text,
               bg="#FB8C00").grid(row=0, column=2, padx=10)
        Button(btn_frame, text="Frequency Chart", command=self.show_chart,
               bg="#7986CB").grid(row=0, column=3, padx=10)
        Button(btn_frame, text="Huffman Tree", command=self.show_tree,
               bg="#FF7043").grid(row=0, column=4, padx=10)

        self.output_label = Label(root, text="", font=("Arial", 12))
        self.output_label.pack(pady=10)

    #Load File
    def load_file(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt")])
        if filepath:
            with open(filepath, "r", encoding="utf-8") as f:
                data = f.read()
                self.text_area.delete(1.0, END)
                self.text_area.insert(END, data)
                messagebox.showinfo(
                    "File Loaded", f"{os.path.basename(filepath)} loaded!")

    # Compress
    def compress_text(self):
        text = self.text_area.get(1.0, END).strip()
        if not text:
            messagebox.showerror("Error", "No text to compress!")
            return
        encoded, tree = self.huffman.encode(text)
        self.last_encoded = encoded
        self.tree = tree
        with open("compressed.bin", "wb") as f:
            pickle.dump((encoded, tree), f)
        original_bits = len(text) * 8
        compressed_bits = len(encoded)
        ratio = (1 - compressed_bits / original_bits) * 100
        self.output_label.config(
            text=f"Compressed! Original: {original_bits} bits | Compressed: {compressed_bits} bits | Ratio: {ratio:.2f}%")

    # Decompress
    def decompress_text(self):
        if not self.last_encoded:
            messagebox.showerror("Error", "No data compressed yet!")
            return
        decoded = self.huffman.decode(self.last_encoded, self.tree)
        self.text_area.delete(1.0, END)
        self.text_area.insert(END, decoded)
        with open("decompressed.txt", "w", encoding="utf-8") as f:
            f.write(decoded)
        self.output_label.config(
            text="Decompression Successful! Saved as decompressed.txt")

    # Frequency Chart
    def show_chart(self):
        text = self.text_area.get(1.0, END).strip()
        if not text:
            messagebox.showerror("Error", "No text to show chart!")
            return
        freq = Counter(text)
        chars = list(freq.keys())
        counts = list(freq.values())
        plt.figure(figsize=(12, 6))
        plt.bar(chars, counts, color='skyblue')
        plt.title("Character Frequency")
        plt.xlabel("Characters")
        plt.ylabel("Frequency")
        plt.show()

    #  Huffman Tree
    def show_tree(self):
        if not self.tree:
            messagebox.showerror(
                "Error", "No tree to display! Compress first.")
            return

        G = nx.DiGraph()

        def add_edges(node, parent=None):
            if node:
                # unique label
                node_label = node.char if node.char else f"{node.freq}-{id(node)}"
                if parent:
                    G.add_edge(parent, node_label)
                add_edges(node.left, node_label)
                add_edges(node.right, node_label)

        add_edges(self.tree)
        plt.figure(figsize=(12, 6))
        pos = nx.spring_layout(G, k=0.5, seed=42)
        nx.draw(G, pos, with_labels=True, node_size=2000,
                node_color='lightgreen', font_size=10, arrows=True)
        plt.title("Huffman Tree")
        plt.show()


#  Run App 
if __name__ == "__main__":
    root = Tk()
    app = HuffmanApp(root)
    root.mainloop()
