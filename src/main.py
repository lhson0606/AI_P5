from logic import *

INPUT_FILE_PATH = "IO/Input.txt"
OUTPUT_FILE_PATH = "IO/Output.txt"


def input_data(kb, file_path):
    with open(file_path, 'r') as file:
        query = file.readline().strip()
        n = int(file.readline())
        for _ in range(n):
            str_clause = file.readline().strip()
            clause = Clause.parse(str_clause)
            kb.tell(clause)
            # print(sentence)
        # print(query)
        # print(kb.clauses)
        return query, kb


def output_data(kb, query, file_path):
    with open(file_path, 'w') as file:
        pl_resolution_to_file(kb, query, file)


def main():
    kb = PropKB()
    query, kb = input_data(kb, INPUT_FILE_PATH)
    output_data(kb, query, OUTPUT_FILE_PATH)
    # print(CNFSentence.parse(-Expr.parse("A <=> B")))
    # print(CNFSentence.parse(Expr.parse("A OR (B AND C)")))
    # print(CNFSentence.parse(-Expr.parse("A OR (B AND C)")))
    # print(CNFSentence.parse(-Expr.parse("(-A AND (B OR -C) AND D) OR E")))
    # print(CNFSentence.parse(-Expr.parse("-( A => B )")))
    # print(CNFSentence.parse(Expr.parse("( - A AND ( B OR - C ) => D ) <=> E")))
    # print(CNFSentence.parse(Expr.parse(" ( C OR (- A OR B) ) AND (A OR C OR B)")))
    # print (CNFSentence.parse(Expr.parse("A OR (B AND C) OR D")))


if __name__ == '__main__':
    main()
