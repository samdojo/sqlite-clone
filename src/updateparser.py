from typing import List, Optional
from baseparser import BaseParser, ParsingException
from statements import UpdateStatement
from sqltoken import TokenType
from qualifiedtablenameparser import QualifiedTableNameParser
from columnnamelistparser import ColumnNameListParser
from expressionparser import ExpressionParser
from tableorsubqueryparser import TableOrSubQueryParser


class UpdateParser(BaseParser):
    """
    Parser for UPDATE statements (AST only, no execution).
    """

    def parse(self) -> UpdateStatement:
        # --- WITH clause (optional) ---
        if self.valueMatches("WITH"):
            self.consume(TokenType.KEYWORD)
            if self.valueMatches("RECURSIVE"):
                self.consume(TokenType.KEYWORD)
            raise ParsingException("Common Table Expressions (WITH clause) are not supported yet")

        # --- UPDATE keyword ---
        if not self.valueMatches("UPDATE"):
            raise ParsingException("Expected UPDATE")
        self.consume(TokenType.KEYWORD)

        # --- OR action (optional) ---
        or_action = None
        if self.valueMatches("OR"):
            self.consume(TokenType.KEYWORD)
            if self.valueMatches("ABORT"):
                or_action = "ABORT"
            elif self.valueMatches("FAIL"):
                or_action = "FAIL"
            elif self.valueMatches("IGNORE"):
                or_action = "IGNORE"
            elif self.valueMatches("REPLACE"):
                or_action = "REPLACE"
            elif self.valueMatches("ROLLBACK"):
                or_action = "ROLLBACK"
            else:
                raise ParsingException("Expected ABORT, FAIL, IGNORE, REPLACE, or ROLLBACK after OR")
            self.consume(TokenType.KEYWORD)

        # --- Qualified table name ---
        table_parser = QualifiedTableNameParser(self.tokens)
        table = table_parser.parse()
        self.tokens = table_parser.tokens

        # --- SET clause ---
        if not self.valueMatches("SET"):
            raise ParsingException("Expected SET in UPDATE statement")
        self.consume(TokenType.KEYWORD)

        set_assignments = []
        while True:
            if self.valueMatches("("):
                # Column-name-list = row-value
                col_parser = ColumnNameListParser(self.tokens)
                column_names = col_parser.parse()
                self.tokens = col_parser.tokens

                if not self.valueMatches("="):
                    raise ParsingException("Expected '=' after column name list")
                self.consume(TokenType.EQ)

                expr_parser = ExpressionParser(self.tokens)
                expr = expr_parser.parse()
                self.tokens = expr_parser.tokens

                set_assignments.append({
                    'columns': column_names,
                    'expression': expr,
                    'is_column_list': True
                })
            else:
                # Single column = expression
                if not self.typeMatches(TokenType.IDENTIFIER):
                    raise ParsingException("Expected column name in SET assignment")
                column_name = self.consume(TokenType.IDENTIFIER).value

                if not self.valueMatches("="):
                    raise ParsingException("Expected '=' in SET assignment")
                self.consume(TokenType.EQ)

                expr_parser = ExpressionParser(self.tokens)
                expr = expr_parser.parse()
                self.tokens = expr_parser.tokens

                set_assignments.append({
                    'columns': [column_name],
                    'expression': expr,
                    'is_column_list': False
                })

            if self.typeMatches(TokenType.COMMA):
                self.consume(TokenType.COMMA)
                continue
            break

        # --- FROM clause (optional) ---
        from_clause = None
        if self.valueMatches("FROM"):
            self.consume(TokenType.KEYWORD)
            from_parser = TableOrSubQueryParser(self.tokens)
            from_clause = from_parser.parse()
            self.tokens = from_parser.tokens

        # --- WHERE clause (optional) ---
        where_expr = None
        if self.valueMatches("WHERE"):
            self.consume(TokenType.KEYWORD)
            expr_parser = ExpressionParser(self.tokens)
            where_expr = expr_parser.parse()
            self.tokens = expr_parser.tokens

        # --- RETURNING clause (optional) ---
        returning_exprs = None
        if self.valueMatches("RETURNING"):
            self.consume(TokenType.KEYWORD)
            expressions = []
            while True:
                expr_parser = ExpressionParser(self.tokens)
                expr = expr_parser.parse()
                self.tokens = expr_parser.tokens
                expressions.append(expr)
                if self.typeMatches(TokenType.COMMA):
                    self.consume(TokenType.COMMA)
                    continue
                break
            returning_exprs = expressions

        return UpdateStatement(
            table=table,
            set_assignments=set_assignments,
            from_clause=from_clause,
            where_expr=where_expr,
            returning_exprs=returning_exprs,
            or_action=or_action,
        )
