from rdflib import Graph
from rdflib.plugins.parsers.notation3 import BadSyntax
from typing import List, Iterable
from sys import stderr
from subprocess import Popen, PIPE, DEVNULL

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

entire_call = parse_to_graph_call + ["http://ignore.me#"] + column_names


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
            entire_call,
            stdin=PIPE,
            stdout=PIPE,
            stderr=DEVNULL,
            universal_newlines=True,
        )

    def send(self, sentence):
        self.process.stdin.write(sentence)
        self.process.stdin.write("\n#_END_")
        self.process.stdin.write("\n\n")
        self.process.stdin.flush()

    def recieve(self):
        buffer = ""
        while True:
            line = self.process.stdout.readline()
            buffer += line
            if buffer == "" or "#_END_" in line:
                break
        return buffer


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


stream = CoNllStreamExtractor()

sucess_counter = 0
failure_counter = 0
ConllSentence = List[str]
with open("data/propbank/contracts/contracts_proposition_bank.conllx") as f:
    sentences = conll_sentences(f)
    for sent in sentences:
        stream.send(sent)
        result = stream.recieve()
        # print(f"{bcolors.WARNING}{ result }{bcolors.ENDC}")
        g = Graph()
        try:
            g.parse(data=result, format="ttl")
            sucess_counter += 1
        except BadSyntax:
            failure_counter += 1
print(sucess_counter)
print(failure_counter)
