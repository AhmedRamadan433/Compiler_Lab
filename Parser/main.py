import sys

# TOKENIZER (SCANNER)
class Tokens:
    def __init__(self, test_file):
        self.test_file = test_file
        self.keywords = {
            "auto", "break", "case", "char", "const", "continue", "default", "do", "main",
            "double", "else", "enum", "extern", "float", "for", "goto", "if",
            "int", "long", "register", "return", "short", "signed", "sizeof",
            "static", "struct", "switch", "typedef", "union", "unsigned", "void",
            "volatile", "while"
        }
        self.special_characters = {
            "(", ")", "{", "}", "[", "]", ";", ":", ",", "#", "\"", "'", "\\"
        }
        self.whitespace = {" ", "\t"}
        self.newline = {"\n"}
        self.ans = []

    def Scan_temp(self, temp):
        if not temp:
            return ""

        if temp in self.keywords:
            self.ans.append(f"<KEYWORD, {temp} >")
        elif temp.isidentifier():
            self.ans.append(f"<IDENTIFIER, {temp} >")
        elif temp.replace('.', '', 1).isnumeric() and temp.count('.') <= 1:
            self.ans.append(f"<NUMERIC CONSTANT, {temp} >")
        else:
            self.ans.append(temp)

        return ""

    def handle_comment(self, i):
        """Handle single-line and multi-line comments"""
        if i + 1 >= len(self.test_file):
            return None, i

        # Single-line comment
        if self.test_file[i + 1] == '/':
            comment = "//"
            i += 2
            while i < len(self.test_file) and self.test_file[i] != '\n':
                comment += self.test_file[i]
                i += 1
            self.ans.append(f"<COMMENT, {comment} >")
            return "", i + 1

        # Multi-line comment
        elif self.test_file[i + 1] == '*':
            comment = "/*"
            i += 2
            while i + 1 < len(self.test_file) and not (self.test_file[i] == '*' and self.test_file[i + 1] == '/'):
                comment += self.test_file[i]
                i += 1
            comment += "*/"
            comment = " ".join(comment.split())
            self.ans.append(f"<COMMENT, {comment} >")
            return "", i + 2

        return None, i

    def Scanner(self):
        temp = ""
        i = 0

        while i < len(self.test_file):
            c = self.test_file[i]

            """Handel division operator / and comment //"""
            if c == '/':
                result, new_i = self.handle_comment(i)
                if result is not None:
                    temp = result
                    i = new_i
                    continue
                else:
                    self.ans.append("<Operator, / >")
                    i += 1
                    continue

            # Handle operators
            elif c in "+-*%!><&|^~":
                temp = self.Scan_temp(temp)

                # two-character operators
                if i + 1 < len(self.test_file):
                    two_char = c + self.test_file[i + 1]
                    if two_char in ["++", "--", "==", "!=", ">=", "<=", "&&", "||", "+=", "-=", "*=", "/=", "%="]:
                        self.ans.append(f"<Operator, {two_char} >")
                        i += 2
                        continue

                self.ans.append(f"<Operator, {c} >")
                i += 1
                continue

            # Handle = and ==
            elif c == '=':
                temp = self.Scan_temp(temp)

                if i + 1 < len(self.test_file) and self.test_file[i + 1] == '=':
                    self.ans.append("<Operator, == >")
                    i += 2
                else:
                    self.ans.append("<Operator, = >")
                    i += 1
                continue

            # Handle character constants with "" and ''
            elif c == '"':
                string_const = '"'
                i += 1
                while i < len(self.test_file) and self.test_file[i] != '"':
                    string_const += self.test_file[i]
                    i += 1
                string_const += '"'
                self.ans.append(f"<Character CONSTANT, {string_const} >")
                i += 1
                continue

            elif c == "'":
                char_const = "'"
                i += 1
                while i < len(self.test_file) and self.test_file[i] != "'":
                    char_const += self.test_file[i]
                    i += 1
                char_const += "'"
                self.ans.append(f"<Character CONSTANT, {char_const} >")
                i += 1
                continue

            # Handle Float nums
            elif c == '.':
                # If temp has digits, this could be a float
                if temp and temp.isdigit():
                    temp += c
                    i += 1
                    # Continue reading digits after the decimal point
                    while i < len(self.test_file) and self.test_file[i].isdigit():
                        temp += self.test_file[i]
                        i += 1
                    continue
                # If next char is a digit, this could be float
                elif i + 1 < len(self.test_file) and self.test_file[i + 1].isdigit():
                    temp += c
                    i += 1
                    continue
                else:
                    # It's just a period special character
                    temp = self.Scan_temp(temp)
                    self.ans.append(f"<SPECIAL CHARACTER, {c} >")
                    i += 1
                    continue

            # Push other special characters
            elif c in self.special_characters:
                temp = self.Scan_temp(temp)
                self.ans.append(f"<SPECIAL CHARACTER, {c} >")
                i += 1
                continue

            # whitespace/newlines
            elif c in self.whitespace or c in self.newline:
                temp = self.Scan_temp(temp)
                i += 1
                continue

            else:
                temp += c
                i += 1

        # Add last token if exists
        temp = self.Scan_temp(temp)

        return self.ans


# PARSER
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = None
        if self.tokens:
            self.current_token = self.tokens[0]

    def advance(self):
        """Move to the next token in the token list"""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def skip_comments(self):
        """Skip over any comment tokens"""
        while self.current_token and self.current_token.startswith("<COMMENT"):
            self.advance()

    def match(self, expected):
        """Check if the current token matches what we're looking for"""
        self.skip_comments()
        if not self.current_token:
            return False
        # For single character special symbols
        if len(expected) == 1 and expected in "(){}[];,":
            return f", {expected} >" in self.current_token
        return expected in self.current_token

    def expect(self, expected, error_msg):
        """Print Expected Token"""
        self.skip_comments()
        if not self.match(expected):
            raise SyntaxError(f"{error_msg}. Found: {self.current_token}")
        self.advance()

    # Grammar Rules

    def parse_program(self):
        """Program → FunctionList"""
        self.parse_function_list()

    def parse_function_list(self):
        """FunctionList → Function FunctionList | ε"""
        while self.current_token:
            self.skip_comments()
            if not self.current_token:
                break
            self.parse_function()

    def parse_function(self):
        """Function → Type IDENTIFIER ( ) { StatementList }"""
        # Check return type (int, void, etc.)
        self.parse_type()

        # Check function name (main or any identifier)
        self.skip_comments()
        if not (self.match("IDENTIFIER") or self.match("main")):
            raise SyntaxError(f"Expected function name. Found: {self.current_token}")
        self.advance()

        # Check (
        self.expect("(", "Expected '('")

        # Check )
        self.expect(")", "Expected ')'")

        # Check {
        self.expect("{", "Expected '{'")

        # Check all statements in the function
        self.parse_statement_list()

        # Check }
        self.expect("}", "Expected '}'")

    def parse_type(self):
        """Type → int | void | float | double | char"""
        self.skip_comments()
        if self.match("int") or self.match("void") or self.match("float") or \
                self.match("double") or self.match("char"):
            self.advance()
        else:
            raise SyntaxError(f"Expected type keyword. Found: {self.current_token}")

    def parse_statement_list(self):
        """StatementList → Statement StatementList | ε"""
        while self.current_token and not self.match("}"):
            self.skip_comments()
            if self.match("}"):
                break
            self.parse_statement()

    def parse_statement(self):
        """Statement → Declaration | Assignment | IfStatement | ReturnStatement"""
        self.skip_comments()

        # Check if we reached end of block
        if self.match("}"):
            return

        # Check what kind of statement this is
        if self.match("int") or self.match("float") or self.match("double") or \
                self.match("char") or self.match("void"):
            self.parse_declaration()

        elif self.match("if"):
            self.parse_if_statement()

        elif self.match("return"):
            self.parse_return_statement()

        elif self.match("IDENTIFIER"):
            self.parse_assignment()

        else:
            raise SyntaxError(f"Unexpected token in statement: {self.current_token}")

    def parse_declaration(self):
        """Declaration → Type IDENTIFIER MoreVars ;"""
        self.parse_type()
        self.expect("IDENTIFIER", "Expected variable name")
        self.parse_more_vars()
        self.skip_comments()
        self.expect(";", "Expected ';'")

    def parse_more_vars(self):
        """MoreVars → , IDENTIFIER MoreVars | ε"""
        self.skip_comments()
        while self.match(","):
            self.advance()
            self.skip_comments()
            if not self.match("IDENTIFIER"):
                raise SyntaxError(f"Expected variable name after ','. Found: {self.current_token}")
            self.advance()
            self.skip_comments()

    def parse_assignment(self):
        """Assignment → IDENTIFIER = Expression ;"""
        self.expect("IDENTIFIER", "Expected identifier")
        self.expect("=", "Expected '='")
        self.parse_expression()
        self.expect(";", "Expected ';'")

    def parse_if_statement(self):
        """IfStatement → if ( Condition ) { StatementList } ElsePart"""
        self.expect("if", "Expected 'if'")
        self.expect("(", "Expected '('")
        self.parse_condition()
        self.expect(")", "Expected ')'")
        self.expect("{", "Expected '{'")
        self.parse_statement_list()
        self.expect("}", "Expected '}'")
        self.parse_else_part()

    def parse_else_part(self):
        """ElsePart → else { StatementList } | ε"""
        self.skip_comments()
        if self.match("else"):
            self.advance()
            self.expect("{", "Expected '{'")
            self.parse_statement_list()
            self.expect("}", "Expected '}'")

    def parse_return_statement(self):
        """ReturnStatement → return Expression ;"""
        self.expect("return", "Expected 'return'")
        self.parse_expression()
        self.expect(";", "Expected ';'")

    def parse_condition(self):
        """Condition → Expression RelOp Expression"""
        self.parse_expression()

        # Check if we have a comparison operator
        self.skip_comments()
        if not (self.match("==") or self.match("!=") or self.match("<") or
                self.match(">") or self.match("<=") or self.match(">=")):
            raise SyntaxError(
                f"Expected comparison operator in if condition. Found: {self.current_token}")

        self.parse_relop()
        self.parse_expression()

    def parse_relop(self):
        """RelOp → == | != | < | > | <= | >="""
        self.skip_comments()
        if self.match("==") or self.match("!=") or self.match("<") or \
                self.match(">") or self.match("<=") or self.match(">="):
            self.advance()
        else:
            raise SyntaxError(f"Expected comparison operator (==, !=, <, >, <=, >=). Found: {self.current_token}")

    def parse_expression(self):
        """Expression → Term MoreTerms"""
        self.parse_term()
        self.parse_more_terms()

    def parse_more_terms(self):
        """MoreTerms → + Term MoreTerms | - Term MoreTerms | ε"""
        self.skip_comments()
        while self.match("+ >") or self.match("- >"):
            self.advance()
            self.parse_term()

        # Check if there's a number/identifier without operator
        self.skip_comments()
        if self.match("IDENTIFIER") or self.match("NUMERIC CONSTANT"):
            raise SyntaxError(
                f"Missing operator before {self.current_token}")

    def parse_term(self):
        """Term → Factor MoreFactors"""
        self.parse_factor()
        self.parse_more_factors()

    def parse_more_factors(self):
        """MoreFactors → * Factor MoreFactors | / Factor MoreFactors | ε"""
        self.skip_comments()
        while self.match("* >") or self.match("/ >"):
            self.advance()
            self.parse_factor()

    def parse_factor(self):
        """Factor → IDENTIFIER | NUMERIC_CONSTANT | ( Expression )"""
        self.skip_comments()

        if self.match("IDENTIFIER") or self.match("NUMERIC CONSTANT"):
            self.advance()
        elif self.match("("):
            self.advance()
            self.parse_expression()
            self.expect(")", "Expected ')'")
        else:
            raise SyntaxError(f"Expected identifier, number, or '('. Found: {self.current_token}")


# MAIN PROGRAM
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python compiler.py <source_file.c> [output_tokens.txt]")
        sys.exit(1)

    source_file = sys.argv[1]

    try:
        # Step 1: Read source code
        print(f"Reading source file: {source_file}")
        with open(source_file, "r", encoding="utf-8") as f:
            source_code = f.read()

        # Step 2: Tokenize (Lexical Analysis)
        tokenizer = Tokens(source_code)
        token_list = tokenizer.Scanner()

        # Optional: Save tokens to file
        if len(sys.argv) >= 3:
            output_file = sys.argv[2]
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("\n".join(token_list))
            print(f"Tokens saved to: {output_file}")

        # Step 3: Parse (Syntax Analysis)
        parser = Parser(token_list)
        parser.parse_program()

        print("\nCOMPILATION SUCCESSFUL!")

    except FileNotFoundError:
        print(f"Error: File '{source_file}' not found")
        sys.exit(1)
    except SyntaxError as e:
        print(f"Syntax Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)