import re

SYMBOLS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
NEGATE_OPERATOR = "-"
IF_AND_ONLY_IF_OPERATOR = "<=>"
IMPLY_OPERATOR = "=>"
AND_OPERATOR = "AND"
OR_OPERATOR = "OR"


def get_precedence(op):
    """
    Get precedence of an operator
    0 if operand
    """
    if op == NEGATE_OPERATOR:
        return 5
    if op == AND_OPERATOR:
        return 4
    if op == OR_OPERATOR:
        return 3
    if op == IMPLY_OPERATOR:
        return 2
    if op == IF_AND_ONLY_IF_OPERATOR:
        return 1
    return 0


def is_symbol(s):
    return s in SYMBOLS


def is_variable(s):
    return is_symbol(s) and s.isupper()


class Expr:
    def __init__(self, op, args):
        self.op = op
        self.args = args

        if op != "":
            assert isinstance(args, list)

        if op == "":
            assert isinstance(args, str)

    @staticmethod
    def parse(str_value):
        def to_postfix_tokens(s):
            """
            Convert infix expression to postfix expression
            >>> example: "A AND B OR C" => ["A", "B", "AND", "C", "OR"]
            :param s: the infix expression
            :return: an array of tokens in reverse polish notation
            """
            res = []
            stack = []

            # sanitize the input
            s = s.strip()
            s = s.replace("(", " ( ").replace(")", " ) ")
            s = s.replace(NEGATE_OPERATOR, f" {NEGATE_OPERATOR} ")
            s = re.sub(r'\s+', ' ', s)

            i = 0
            while i < len(s):
                token = ""
                j = i
                while j < len(s) and s[j] != " ":
                    token += s[j]
                    j += 1

                if token == "":
                    i += 1
                    continue
                elif token == "(":
                    stack.append(token)
                elif token == ")":
                    while stack and stack[-1] != "(":
                        res.append(stack.pop())
                    stack.pop()
                elif get_precedence(token) == 0:
                    res.append(token)
                else:
                    while stack and get_precedence(stack[-1]) >= get_precedence(token):
                        res.append(stack.pop())
                    stack.append(token)

                i = j + 1

            while stack:
                res.append(stack.pop())

            return res

        def to_expr(tokens):
            stack = []
            for token in tokens:
                # nullary operator / operand
                if get_precedence(token) == 0:
                    stack.append(Expr("", token))
                # unary operator
                elif token == NEGATE_OPERATOR:
                    stack.append(Expr(token, [stack.pop()]))
                # binary operator
                else:
                    if len(stack) < 2:
                        raise ValueError(f"Invalid expression {str_value}")
                    right = stack.pop()
                    left = stack.pop()
                    stack.append(Expr(token, [left, right]))

            assert len(stack) == 1 and "Invalid expression"
            return stack[0]

        return to_expr(to_postfix_tokens(str_value))

    def __neg__(self):
        return Expr(NEGATE_OPERATOR, [self])

    def __str__(self):
        if self.op == "":
            return self.args[0]
        if self.op == NEGATE_OPERATOR:
            return f"{self.op}{self.args[0]}"
        return f"({self.args[0]} {self.op} {self.args[1]})"


def eliminate_biconditional(expr):
    if expr.op == "":
        return expr
    if expr.op == IF_AND_ONLY_IF_OPERATOR:
        return Expr(AND_OPERATOR, [Expr(IMPLY_OPERATOR, expr.args),
                                   Expr(IMPLY_OPERATOR, [eliminate_biconditional(expr.args[1]),
                                                         eliminate_biconditional(expr.args[0])])])
    return Expr(expr.op, [eliminate_biconditional(arg) for arg in expr.args])


def eliminate_implication(expr):
    if expr.op == "":
        return expr
    if expr.op == IMPLY_OPERATOR:
        return Expr(OR_OPERATOR, [Expr(NEGATE_OPERATOR, [eliminate_implication(expr.args[0])]),
                                  eliminate_implication(expr.args[1])])
    return Expr(expr.op, [eliminate_implication(arg) for arg in expr.args])


def move_negation_inward(expr):
    if expr.op == "":
        return expr
    if expr.op == NEGATE_OPERATOR:
        # double negation
        if expr.args[0].op == NEGATE_OPERATOR:
            return move_negation_inward(expr.args[0].args[0])
        # De Morgan's Law
        if expr.args[0].op == AND_OPERATOR:
            return Expr(OR_OPERATOR, [move_negation_inward(Expr(NEGATE_OPERATOR, [expr.args[0].args[0]])),
                                      move_negation_inward(Expr(NEGATE_OPERATOR, [expr.args[0].args[1]]))])
        if expr.args[0].op == OR_OPERATOR:
            return Expr(AND_OPERATOR, [move_negation_inward(Expr(NEGATE_OPERATOR, [expr.args[0].args[0]])),
                                       move_negation_inward(Expr(NEGATE_OPERATOR, [expr.args[0].args[1]]))])
        return expr
    return Expr(expr.op, [move_negation_inward(arg) for arg in expr.args])


def distribute_and_over_or(clause_expr):
    if clause_expr.op == "":
        return clause_expr
    if clause_expr.op == OR_OPERATOR:
        assert len(clause_expr.args) == 2 and "Invalid clause_expr expression"

        e1 = clause_expr.args[0]
        e2 = clause_expr.args[1]

        e1 = distribute_and_over_or(e1)
        e2 = distribute_and_over_or(e2)

        if e1.op == "" and e2.op == "":
            literals = []
            literals.extend(e1.args.literals)
            literals.extend(e2.args.literals)
            clause_expr = ClauseExpr("", Clause(literals))
            return clause_expr
        elif e1.op == "":
            r1 = distribute_and_over_or(ClauseExpr(OR_OPERATOR, [e1, e2.args[0]]))
            r2 = distribute_and_over_or(ClauseExpr(OR_OPERATOR, [e1, e2.args[1]]))
            clause_expr = ClauseExpr(AND_OPERATOR, [r1, r2])
            return clause_expr
        elif e2.op == "":
            r1 = distribute_and_over_or(ClauseExpr(OR_OPERATOR, [e1.args[0], e2]))
            r2 = distribute_and_over_or(ClauseExpr(OR_OPERATOR, [e1.args[1], e2]))
            clause_expr = ClauseExpr(AND_OPERATOR, [r1, r2])
            return clause_expr

        v1 = distribute_and_over_or(ClauseExpr(OR_OPERATOR, [e1.args[0], e2.args[0]]))
        v2 = distribute_and_over_or(ClauseExpr(OR_OPERATOR, [e1.args[0], e2.args[1]]))
        r1 = ClauseExpr(AND_OPERATOR, [v1, v2])

        v1 = distribute_and_over_or(ClauseExpr(OR_OPERATOR, [e1.args[1], e2.args[0]]))
        v2 = distribute_and_over_or(ClauseExpr(OR_OPERATOR, [e1.args[1], e2.args[1]]))
        r2 = ClauseExpr(AND_OPERATOR, [v1, v2])

        clause_expr = ClauseExpr(OR_OPERATOR, [r1, r2])
        return clause_expr

    elif clause_expr.op == AND_OPERATOR:
        clause_expr = ClauseExpr(AND_OPERATOR, [distribute_and_over_or(arg) for arg in clause_expr.args])
        return clause_expr
    else:
        raise ValueError(f"Invalid operator {clause_expr.op}")
        pass


class Literal:
    def __init__(self, symbol, negated=False):
        if not isinstance(symbol, str):
            print(symbol)
            raise ValueError(f"Receive type {type(symbol)}. A literal must be a string")
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
    """
    A clause is a disjunction of literals
    Example: A | B | C
    class fields:
        literals: list of literals in the clause. Example: [A, B, C]
    """

    def __init__(self, literals):
        self.literals = literals
        if not isinstance(literals, list):
            raise ValueError(f"Receive type {type(literals)}. A clause must be a list")

        for literal in literals:
            if not isinstance(literal, Literal):
                raise ValueError(f"Receive type {type(literal)}. A clause must be a list of literals")

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
        return "{" + f" {OR_OPERATOR} ".join([str(l) for l in self.literals]) + "}"

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


class ClauseExpr:
    """
    like Expr but for clauses
    """

    def __init__(self, op, args):
        self.op = op
        self.args = args

        if op != "":
            assert isinstance(args, list)

    def get_tree_str(self):
        def get_string(root, indent=""):
            if root.op == "":
                return indent + str(root.args[0])
            else:
                res = ""
                for arg in root.args:
                    res += get_string(arg, indent + "  ") + "\n"
                return indent + root.op + "\n" + res

        return get_string(self)

    def __str__(self):
        if self.op == "":
            return str(self.args)
        else:
            res = ""
            for arg in self.args:
                res += f"{arg} {self.op} "
            return res[:-len(self.op) - 1]


def build_clause_expr(expr):
    if expr.op == "":
        return ClauseExpr("", Clause([Literal(expr.args[0])]))
    elif expr.op == NEGATE_OPERATOR:
        return ClauseExpr("", Clause([Literal(expr.args[0].args[0], True)]))
    elif expr.op == OR_OPERATOR:
        return ClauseExpr(OR_OPERATOR, [build_clause_expr(expr.args[0]), build_clause_expr(expr.args[1])])
    elif expr.op == AND_OPERATOR:
        return ClauseExpr(AND_OPERATOR, [build_clause_expr(expr.args[0]), build_clause_expr(expr.args[1])])
    else:
        raise ValueError(f"Invalid operator {expr.op}")


def recursive_promote_or(clause_expr):
    if clause_expr.op == "":
        return
    elif clause_expr.op == OR_OPERATOR:
        temp_args = []
        temp_args += clause_expr.args

        for arg in temp_args:
            if arg.op == OR_OPERATOR:
                clause_expr.args.remove(arg)
                recursive_promote_or(arg)
                clause_expr.args += arg.args

        pass
    else:
        for arg in clause_expr.args:
            recursive_promote_or(arg)
    pass


def associate_or_operator(clause_expr):
    if clause_expr.op == "":
        clause_expr.args = Clause(clause_expr.args.literals)
        return
    elif clause_expr.op == OR_OPERATOR:
        temp_args = []
        temp_args += clause_expr.args
        collapsed_expr = ClauseExpr("", Clause([]))
        contain_and = False
        for arg in temp_args:
            if arg.op == AND_OPERATOR:
                contain_and = True
                break

        if not contain_and:
            # promote it to the root
            clause_expr.op = ""
            literals = []
            for arg in temp_args:
                literals.extend(arg.args.literals)
            clause_expr.args = Clause(literals)
            return

        for arg in temp_args:
            if arg.op == "":
                collapsed_expr.args.literals.extend(arg.args.literals)
                clause_expr.args.remove(arg)
            else:
                associate_or_operator(arg)

        clause_expr.args.append(collapsed_expr)
    else:
        for arg in clause_expr.args:
            associate_or_operator(arg)
    pass


def collapsed_or_operator(clause_expr):
    recursive_promote_or(clause_expr)
    associate_or_operator(clause_expr)
    pass


def promote_and_to_root(expr):
    if expr.op == "":
        return expr
    elif expr.op == AND_OPERATOR:
        return promote_and_to_root(
            Expr(AND_OPERATOR, promote_and_to_root(expr.args[0]), promote_and_to_root(expr.args[1]))
        )
    return expr


class CNFSentence:
    def __init__(self, clauses):
        self.clauses = clauses

    @staticmethod
    def parse(expr):
        res = Expr("", "")
        # step 1: eliminate biconditional
        res = eliminate_biconditional(expr)
        # step 2: eliminate implication
        res = eliminate_implication(res)
        # step 3: move negation inwards
        res = move_negation_inward(res)
        # step 4: distribute and over or
        clause_tree = build_clause_expr(res)
        collapsed_or_operator(clause_tree)
        clause_tree = distribute_and_over_or(clause_tree)
        return CNFSentence(CNFSentence._get_clauses(clause_tree))

    @staticmethod
    def _get_clauses(clause_tree):
        if clause_tree.op == "":
            return [clause_tree.args]
        res = []
        for arg in clause_tree.args:
            res += CNFSentence._get_clauses(arg)
        return res

    def __str__(self):
        return f"{' AND '.join([str(clause) for clause in self.clauses])}"

    pass


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
    clauses = kb.clauses + CNFSentence.parse(-Expr.parse(alpha)).clauses
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
    clauses = kb.clauses + CNFSentence.parse(-Expr.parse(alpha)).clauses
    while True:
        new = set()
        n = len(clauses)
        pairs = [(clauses[i], clauses[j])
                 for i in range(n) for j in range(i + 1, n)]
        new_resolvents = []
        for ci, cj in pairs:
            resolvents = pl_resolve(ci, cj)
            new_resolvents += resolvents
            new.update(resolvents)
        new_resolvents = list(set(new_resolvents))
        if any([clause.is_empty() for clause in new_resolvents]):
            new_clauses = [l for l in new_resolvents if l not in clauses]
            output.write(str(new_clauses.__len__()) + "\n")
            for clause in new_clauses:
                output.write(str(clause) + "\n")
            output.write("YES\n")
            return
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
