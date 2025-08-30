from baseparser import BaseParser
from statements import UpdateStatement
from sqltoken import TokenType
from baseparser import ParsingException

class UpdateParser(BaseParser):
    def parse(self) -> UpdateStatement:
        # --- WITH clause (optional) ---
        with_clause = None
        if self.valueMatches("WITH"):
            super().consume(TokenType.KEYWORD)
            recursive = False
            if self.valueMatches("RECURSIVE"):
                super().consume(TokenType.KEYWORD)
                recursive = True
            with_clause = self._parse_common_table_expression_list(recursive)

        # --- UPDATE keyword ---
        if not self.valueMatches("UPDATE"):
            raise ParsingException("Expected UPDATE")
        super().consume(TokenType.KEYWORD)

        # --- OR action (optional) ---
        or_action = None
        if self.valueMatches("OR"):
            super().consume(TokenType.KEYWORD)
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
            super().consume(TokenType.KEYWORD)

        # --- qualified-table-name ---
        schema_name = None
        table_token = super().consume(TokenType.IDENTIFIER)
        table_name = table_token.value
        if self.valueMatches("."):
            super().consume(TokenType.DOT)
            schema_name = table_name
            table_token = super().consume(TokenType.IDENTIFIER)
            table_name = table_token.value

        # --- SET clause ---
        if not self.valueMatches("SET"):
            raise ParsingException("Expected SET")
        super().consume(TokenType.KEYWORD)

        set_assignments = []
        while True:
            if self.valueMatches("("):
                # Column-name-list = row-value
                super().consume(TokenType.LPAREN)
                column_names = []
                while True:
                    column_token = super().consume(TokenType.IDENTIFIER)
                    column_names.append(column_token.value)
                    if self.valueMatches(","):
                        super().consume(TokenType.COMMA)
                    else:
                        break
                if not self.valueMatches(")"):
                    raise ParsingException("Expected ')' after column list")
                super().consume(TokenType.RPAREN)

                if not self.valueMatches("="):
                    raise ParsingException("Expected '=' after column list")
                super().consume(TokenType.OPERATOR)

                expr = self._parse_row_value()
                set_assignments.append({
                    'columns': column_names,
                    'expression': expr,
                    'is_column_list': True
                })
            else:
                # column = expr
                column_token = super().consume(TokenType.IDENTIFIER)
                column_name = column_token.value
                if not self.valueMatches("="):
                    raise ParsingException("Expected '=' after column name")
                super().consume(TokenType.OPERATOR)
                expr = self._parse_expression()
                set_assignments.append({
                    'columns': [column_name],
                    'expression': expr,
                    'is_column_list': False
                })

            if self.valueMatches(","):
                super().consume(TokenType.COMMA)
            else:
                break

        # --- FROM clause (optional) ---
        from_clause = None
        if self.valueMatches("FROM"):
            super().consume(TokenType.KEYWORD)
            from_clause = self._parse_from_clause()

        # --- WHERE clause (optional) ---
        where_clause = None
        if self.valueMatches("WHERE"):
            super().consume(TokenType.KEYWORD)
            where_clause = self._parse_expression()

        # --- RETURNING clause (optional) ---
        returning_clause = None
        if self.valueMatches("RETURNING"):
            super().consume(TokenType.KEYWORD)
            returning_clause = self._parse_returning_clause()

        return UpdateStatement(
            with_clause=with_clause,
            table_name=table_name,
            schema_name=schema_name,
            or_action=or_action,
            set_assignments=set_assignments,
            from_clause=from_clause,
            where_clause=where_clause,
            returning_clause=returning_clause
        )

    # --- Helpers ---

    def _parse_expression(self):
        expr_tokens = []
        paren_depth = 0
        while (self.current_token and 
               not (paren_depth == 0 and self.valueMatches(",")) and
               not (paren_depth == 0 and self.valueMatches("FROM")) and
               not (paren_depth == 0 and self.valueMatches("WHERE")) and
               not (paren_depth == 0 and self.valueMatches("RETURNING")) and
               not self.current_token.type == TokenType.EOF):
            if self.valueMatches("("):
                paren_depth += 1
            elif self.valueMatches(")"):
                paren_depth -= 1
                if paren_depth < 0:
                    break
            token = super().consume()
            expr_tokens.append(token)
        return " ".join([token.value for token in expr_tokens])

    def _parse_row_value(self):
        if self.valueMatches("("):
            super().consume(TokenType.LPAREN)
            expressions = []
            while True:
                expr = self._parse_expression()
                expressions.append(expr)
                if self.valueMatches(","):
                    super().consume(TokenType.COMMA)
                else:
                    break
            if not self.valueMatches(")"):
                raise ParsingException("Expected ')' after row value")
            super().consume(TokenType.RPAREN)
            return f"({', '.join(expressions)})"
        else:
            return self._parse_expression()

    def _parse_from_clause(self):
        # simplified: just table + optional alias
        table_token = super().consume(TokenType.IDENTIFIER)
        table_name = table_token.value
        alias = None
        if (self.current_token and 
            self.current_token.type == TokenType.IDENTIFIER and
            not self.valueMatches("WHERE") and 
            not self.valueMatches("RETURNING")):
            alias_token = super().consume(TokenType.IDENTIFIER)
            alias = alias_token.value
        return {'table_name': table_name, 'alias': alias}

    def _parse_returning_clause(self):
        if self.valueMatches("*"):
            super().consume(TokenType.OPERATOR)
            return "*"
        else:
            expressions = []
            while True:
                expr = self._parse_expression()
                expressions.append(expr)
                if self.valueMatches(","):
                    super().consume(TokenType.COMMA)
                else:
                    break
            return expressions

    def _parse_common_table_expression_list(self, recursive: bool):
        # Parses: cte [, cte ...]
        ctes = []
        while True:
            name_token = super().consume(TokenType.IDENTIFIER)
            cte_name = name_token.value

            column_names = None
            if self.valueMatches("("):
                column_names = []
                super().consume(TokenType.LPAREN)
                while True:
                    col_token = super().consume(TokenType.IDENTIFIER)
                    column_names.append(col_token.value)
                    if self.valueMatches(","):
                        super().consume(TokenType.COMMA)
                    else:
                        break
                super().consume(TokenType.RPAREN)

            if not self.valueMatches("AS"):
                raise ParsingException("Expected AS in CTE")
            super().consume(TokenType.KEYWORD)

            if not self.valueMatches("("):
                raise ParsingException("Expected '(' before CTE subquery")
            super().consume(TokenType.LPAREN)

            # For simplicity: collect tokens until matching
            
            expr = self._parse_expression()

            if not self.valueMatches(")"):
                raise ParsingException("Expected ')' after CTE subquery")
            super().consume(TokenType.RPAREN)

            ctes.append({
                "name": cte_name,
                "columns": column_names,
                "subquery": expr
            })

            if self.valueMatches(","):
                super().consume(TokenType.COMMA)
            else:
                break

        return {"recursive": recursive, "ctes": ctes}
