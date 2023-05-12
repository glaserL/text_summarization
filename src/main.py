from tqdm import tqdm
from typing import List, Iterable
from sys import stderr
from subprocess import Popen, PIPE

parse_to_graph_call = ["./lib/conll-rdf/run.sh", "CoNLLStreamExtractor"]
column_names = [
    "ID",
    "WORD",
    "LEMMA",
    "UPOS",
    "XPOS",
    "FEATS",
    "HEAD",
    "EDGE",
    "IGNORE",
    "PRED",
    "PRED-ARGs",
]

entire_call = parse_to_graph_call + ["http://ignore.me/"] + column_names


def conll_sentences(lines: Iterable[str]):
    buffer = ""
    for line in lines:
        line = line
        if line.strip() == "" and len(buffer):
            yield buffer
            buffer = line
        else:
            buffer += line
    yield buffer


class CoNllStreamExtractor:
    def __init__(self) -> None:
        print(f"Creating call {entire_call}")
        self.process = Popen(
            entire_call, stdin=PIPE, stdout=PIPE, stderr=stderr, universal_newlines=True
        )

    def send(self, sentence):
        self.process.stdin.write(sentence)
        self.process.stdin.write('\n#_END_')
        self.process.stdin.write('\n\n')
        self.process.stdin.flush()

    def recieve(self):
        buffer = ""
        while True:
            line = self.process.stdout.readline()
            buffer += line
            if buffer == "" or "#_END_" in line:
                break
        return buffer
        


stream = CoNllStreamExtractor()


ConllSentence = List[str]
with open("data/propbank/contracts/contracts_proposition_bank.conllx") as f:
    sentences = conll_sentences(f)
    for sent in tqdm(sentences):
        stream.send(sent)
        result = stream.recieve()
        print(result)
