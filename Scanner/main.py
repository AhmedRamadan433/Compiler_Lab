import sys
################################################################
class Tokens:
    def __init__(self, test_file):
        self.test_file = test_file
        self.keywords = {
            "auto", "break", "case", "char", "const", "continue", "default", "do","main",
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
            comment=" ".join(comment.split())
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

            #Handle character constants with "" and ''
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

################################################################
if len(sys.argv) < 3:
    print("usage: python main.py File.c <Destination_File>")
    sys.exit(1)
file_path = sys.argv[1]
opened_file=""
with open(file_path, "r", encoding="utf-8") as f:
    opened_file=f.read()
tokens=Tokens(opened_file)
ans="\n".join(tokens.Scanner())
res_path=sys.argv[2]
with open(res_path,"w",encoding="utf-8")as f:
    f.write(ans)
