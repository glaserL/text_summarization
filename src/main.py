from rdflib import Graph
from rdflib.plugins.parsers.notation3 import BadSyntax
from typing import List, Iterable, Optional, Tuple
from sys import stderr
from subprocess import Popen, PIPE, DEVNULL


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


class CoNLLRDFProcess:
    def __init__(self, args: List[str]):
        prefix = ["./lib/conll-rdf/run.sh", self.__class__.__name__]
        call = prefix + args
        print(f"Starting process {call}")
        self.process = Popen(
            call,
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


class CoNLLStreamExtractor(CoNLLRDFProcess):
    def __init__(self, base_uri: str, columns: List[str]) -> None:
        args = [base_uri] + columns
        super().__init__(args)


class CoNLLRDFUpdater(CoNLLRDFProcess):
    def __init__(
        self,
        model: Tuple[str, str],
        update_files: List[str],
        threads: Optional[int] = None,
        custom=True,
    ):
        
        args = []
        args += list(model)
        if threads is not None:
            args += ["-threads", threads]
        if custom:
            args += ["-custom"]
        if update_files:
            args += ["-updates"]
            args += update_files
        super().__init__(args)



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


stream = CoNLLStreamExtractor("http://ignore.me#", column_names)
update_files = ["empty_sparql.sparql"]
updater = CoNLLRDFUpdater([], update_files)
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
