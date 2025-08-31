from sqltoken import Token, TokenType
from typing import List
import re

class Tokenizer:
    def __init__(self):
        self.keywords = {
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP',
            'ALTER', 'TABLE', 'INDEX', 'VIEW', 'DATABASE', 'SCHEMA', 'INTO', 'VALUES',
            'SET', 'AND', 'OR', 'NOT', 'NULL', 'IS', 'IN', 'LIKE', 'BETWEEN', 'EXISTS',
            'DISTINCT', 'ALL', 'ANY', 'SOME', 'UNION', 'INTERSECT', 'EXCEPT', 'MINUS',
            'ORDER', 'BY', 'GROUP', 'HAVING', 'LIMIT', 'OFFSET', 'JOIN', 'INNER',
            'LEFT', 'RIGHT', 'FULL', 'OUTER', 'CROSS', 'ON', 'USING', 'AS', 'CASE',
            'WHEN', 'THEN', 'ELSE', 'END', 'IF', 'DECLARE', 'BEGIN', 'COMMIT',
            'ROLLBACK', 'TRANSACTION', 'PRIMARY', 'KEY', 'FOREIGN', 'REFERENCES',
            'UNIQUE', 'CHECK', 'DEFAULT', 'AUTO_INCREMENT', 'IDENTITY', 'CONSTRAINT',
            'INT', 'INTEGER', 'VARCHAR', 'CHAR', 'TEXT', 'DATE', 'DATETIME', 'TIMESTAMP',
            'BOOLEAN', 'BOOL', 'DECIMAL', 'NUMERIC', 'FLOAT', 'DOUBLE', 'REAL', 'COUNT',
            'ASC', 'DESC', 'CURRENT_TIME', 'CURRENT_DATE', 'CURRENT_TIMESTAMP', 'TRUE',
            'FALSE', "ISNULL", "NOTNULL", "ESCAPE", "GLOB", "REGEXP", "MATCH"
        }

        self.token_patterns = [
            # Comments
            (r'--.*$', TokenType.COMMENT),
            (r'/\*.*?\*/', TokenType.COMMENT),

            # String literals (single and double quotes)
            (r"'(?:[^'\\]|\\.)*'", TokenType.STRING_LITERAL),
            (r'"(?:[^"\\]|\\.)*"', TokenType.STRING_LITERAL),

            # Number literals
            (r'\b\d+\.?\d*\b', TokenType.NUMBER_LITERAL),

            # Comparison operators (must come before single character operators)
            (r'==|<=|>=|<>|!=|<|>|=', TokenType.COMPARISON),

            # Other operators
            (r'\+|-|\*|/|%|~|\|\||&', TokenType.OPERATOR),

            # Punctuation
            (r',', TokenType.COMMA),
            (r';', TokenType.SEMICOLON),
            (r'\.', TokenType.DOT),
            (r'\(', TokenType.LPAREN),
            (r'\)', TokenType.RPAREN),

            # Identifiers (including quoted identifiers with backticks or square brackets)
            (r'`[^`]+`', TokenType.IDENTIFIER),
            (r'\[[^\]]+\]', TokenType.IDENTIFIER),
            (r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', TokenType.IDENTIFIER),

            # Whitespace
            (r'\s+', TokenType.WHITESPACE),
        ]

        # Compile patterns for better performance
        self.compiled_patterns = [(re.compile(pattern, re.MULTILINE | re.DOTALL), token_type)
                                 for pattern, token_type in self.token_patterns]

    def tokenize(self, sql: str) -> List[Token]:
        tokens = []
        position = 0
        line = 1
        line_start = 0

        while position < len(sql):
            matched = False

            for pattern, token_type in self.compiled_patterns:
                match = pattern.match(sql, position)
                if match:
                    value = match.group(0)

                    if token_type == TokenType.IDENTIFIER and value.upper() in self.keywords:
                        token_type = TokenType.KEYWORD

                    token = Token(token_type, value)

                    if (token_type != TokenType.WHITESPACE) and (token_type != TokenType.COMMENT):
                        tokens.append(token)

                    position = match.end()
                    newlines = value.count('\n')
                    if newlines > 0:
                        line += newlines
                        line_start = position - len(value.split('\n')[-1])

                    matched = True
                    break

            if not matched:
                tokens.append(Token(TokenType.UNKNOWN, sql[position]))
                position += 1

        tokens.append(Token(TokenType.EOF, ''))

        return tokens

    def print_tokens(self, tokens: List[Token]):
        """Helper function to print tokens in a readable format."""
        print(f"{'Type':<15} {'Value':<20}")
        print("-" * 55)
        for token in tokens:
            value_repr = repr(token.value) if token.value else "''"
            print(f"{token.type.value:<15} {value_repr:<20}")

# Example usage
if __name__ == "__main__":
    tokenizer = Tokenizer()

    test_query = """
    SELECT u.name, u.email, p.title
    FROM users u
    JOIN posts p ON u.id = p.user_id
    WHERE u.active = true
      AND p.created_at >= '2023-01-01'
    ORDER BY p.created_at DESC
    LIMIT 10;
    """

    print("Tokenizing query:")
    print(test_query)
    print("\nTokens:")

    tokens = tokenizer.tokenize(test_query)
    tokenizer.print_tokens(tokens)

    print(f"\nTotal tokens: {len(tokens)}")

    # Example of filtering specific token types
    keywords = [t for t in tokens if t.type == TokenType.KEYWORD]
    print(f"\nKeywords found: {[t.value for t in keywords]}")

    identifiers = [t for t in tokens if t.type == TokenType.IDENTIFIER]
    print(f"Identifiers found: {[t.value for t in identifiers]}")
