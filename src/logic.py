SYMBOLS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
NEGATE_OPERATOR = "-"
OR_OPERATOR = "OR"


def is_symbol(s):
    return s in SYMBOLS


def is_variable(s):
    return is_symbol(s) and s.isupper()


class Literal:
    def __init__(self, symbol, negated=False):
        if not is_symbol(symbol):
            raise ValueError(f"Receive symbol {symbol}. A literal must be [A-Z]")
        self.symbol = symbol
        self.negated = negated

    def __neg__(self):
        return Literal(self.symbol, not self.negated)

    def __eq__(self, other):
        return self.symbol == other.symbol and self.negated == other.negated

    def __hash__(self):
        return hash((self.symbol, self.negated))

    def __str__(self):
        return f"{NEGATE_OPERATOR if self.negated else ''}{self.symbol}"

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def parse(str_value):
        str_value = str_value.strip()
        if str_value.startswith(NEGATE_OPERATOR):
            return Literal(str_value[1:], True)
        return Literal(str_value, False)

    def __lt__(self, other):
        if not isinstance(other, Literal):
            return NotImplemented
        if self.symbol != other.symbol:
            return self.symbol < other.symbol
        return self.negated < other.negated


class Clause:
    def __init__(self, literals):
        self.literals = literals

    @staticmethod
    def parse(str_value):
        literals = []
        for literal in str_value.split(OR_OPERATOR):
            literal = literal.strip()
            if literal.startswith(NEGATE_OPERATOR):
                literals.append(Literal(literal[1:], True))
            else:
                literals.append(Literal(literal, False))
        return Clause(literals)

    def is_empty(self):
        return len(self.literals) == 0

    def __str__(self):
        if self.is_empty():
            return "{}"
        return f" {OR_OPERATOR} ".join([str(l) for l in self.literals])

    def is_tautology(self):
        for i in range(len(self.literals)):
            for j in range(i + 1, len(self.literals)):
                if self.literals[i].symbol == self.literals[j].symbol and self.literals[i].negated != self.literals[j].negated:
                    return True
        return False

    def __eq__(self, other):
        if not isinstance(other, Clause):
            return False
        return set(self.literals) == set(other.literals)

    def __hash__(self):
        return hash(tuple(sorted(self.literals)))

    def simplify(self):
        literals = set()
        for literal in self.literals:
            if -literal in literals:
                return Clause([])
            literals.add(literal)
        return Clause(list(literals))

    def negate_all(self):
        return Clause([-literal for literal in self.literals])


def pl_resolve(ci, cj):
    resolvents = []
    for di in ci.literals:
        for dj in cj.literals:
            if di.symbol == dj.symbol and di.negated != dj.negated:
                data = [l1 for l1 in ci.literals if l1 != di] + [l2 for l2 in cj.literals if l2 != dj]
                clause = Clause(data)
                if not clause.is_tautology():
                    resolvents.append(clause.simplify())
    return resolvents


def pl_resolution(kb, alpha):
    raise NotImplementedError
    clauses = kb.clauses + [-Clause.parse(alpha)]
    new = set()
    while True:
        n = len(clauses)
        pairs = [(clauses[i], clauses[j]) for i in range(n) for j in range(i + 1, n)]
        for ci, cj in pairs:
            resolvents = pl_resolve(ci, cj)
            if any([clause.is_empty() for clause in resolvents]):
                return True
            new.update(resolvents)
        if new.issubset(set(clauses)):
            return False
        clauses = list(set(clauses + list(new)))


def pl_resolution_to_file(kb, alpha, output):
    clauses = kb.clauses + [Clause.parse(alpha).negate_all()]
    while True:
        new = set()
        n = len(clauses)
        pairs = [(clauses[i], clauses[j])
                 for i in range(n) for j in range(i + 1, n)]
        for ci, cj in pairs:
            resolvents = pl_resolve(ci, cj)
            if any([clause.is_empty() for clause in resolvents]):
                new_clauses = [l for l in resolvents if l not in clauses]
                output.write(str(new_clauses.__len__()) + "\n")
                for clause in new_clauses:
                    output.write(str(clause) + "\n")
                output.write("YES\n")
                return
            new.update(resolvents)
        if new.issubset(set(clauses)):
            output.write("NO\n")
            return
        new_clauses = [l for l in new if l not in clauses]
        clauses += new_clauses
        output.write(str(new_clauses.__len__()) + "\n")
        for clause in new_clauses:
            output.write(str(clause) + "\n")


# KB class represents a knowledge base for propositional logic
# Note: Only support CNF clauses
class PropKB:
    def __init__(self):
        self.clauses = []

    def tell(self, clause):
        self.clauses.append(clause)

    def ask(self, query):
        return True

    def ask_generator(self, query, output):
        output.write("OK\n")