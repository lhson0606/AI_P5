# AI_P5
Intro2AI course
propositional logic, CNF and pl_resolution

# Description
Source code for the 5th problem of the Introduction to Artificial Intelligence course at HCMUS.

# Running program
1. The program is contained in folder `src`
2. Input propositional logic in `IO/Input.txt`
3. Run the program by running the file in `main.py`
4. The result will be saved in `IO/Output.txt`

# Syntax
SYMBOLS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
NEGATE_OPERATOR = "-"
IF_AND_ONLY_IF_OPERATOR = "<=>"
IMPLY_OPERATOR = "=>"
AND_OPERATOR = "AND"
OR_OPERATOR = "OR"
Operators and operands are separated by a space.

# Operators precedence (decreasingly):
-, AND ,OR ,=> ,<=>

# Installation & Usage
1. Clone the repository by running `git clone https://github.com/lhson0606/AI_P5.git`
2. Change directory to the repository by running `cd AI_P5`
3. Install .venv by running `python -m venv .venv`
4. Install dependencies by running `pip install -r requirements.txt`
5. Input propositional logic in `Input.txt`
6. Mark folder `src` as the source root
7. Run the program by running the file in `src/main.py`
8. The result will be printed in the console and saved in `Output.txt`