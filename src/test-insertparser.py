import pytest

from sqltokenizer import Tokenizer
from sqltoken import Token, TokenType
from baseparser import ParsingException
from insertparser import InsertStatementParser
from statements import Expression, Literal
from statements import InsertStatement


def make_tokens(pairs):
    """Build tokens without running the tokenizer (useful for 'extra tokens' test)."""
    return [Token(value=v, type=t) for v, t in pairs]


def test_insert_with_schema_alias_and_columns():
    sql = "INSERT INTO main.users AS u (id, name) VALUES (1, 'alice')"
    tokens = Tokenizer().tokenize(sql)
    parser = InsertStatementParser(tokens)
    stmt = parser.parse()
    expected = InsertStatement(
        table_name="users",
        schema_name="main",
        alias="u",
        column_names=["id", "name"],
        values=stmt.values,
    )

    assert stmt == expected

    assert stmt.schema_name == "main"
    assert stmt.table_name == "users"
    assert stmt.alias == "u"
    assert stmt.column_names == ["id", "name"]

    assert isinstance(stmt.values, list) and len(stmt.values) == 2
    v1, v2 = stmt.values

    # 1 → Expression(route=1, lead_expr=Literal(dtype=int, value=1))
    assert isinstance(v1, Expression) and v1.route == 1
    assert isinstance(v1.lead_expr, Literal)
    assert v1.lead_expr.dtype is int and v1.lead_expr.value == 1

    # 'alice' → Expression(route=1, lead_expr=Literal(dtype=str, value="alice"))
    assert isinstance(v2, Expression) and v2.route == 1
    assert isinstance(v2.lead_expr, Literal)
    assert v2.lead_expr.dtype is str and v2.lead_expr.value == "alice"


def test_insert_without_schema_alias_or_column_list():
    """
    INSERT INTO users VALUES (2, 'bob')
    Expect: schema=None, alias=None, column_names=None (means 'all columns'),
            values = [2, 'bob'].
    """
    sql = "INSERT INTO users VALUES (2, 'bob')"
    tokens = Tokenizer().tokenize(sql)
    parser = InsertStatementParser(tokens)
    stmt = parser.parse()

    assert stmt.schema_name is None
    assert stmt.table_name == "users"
    assert stmt.alias is None
    assert stmt.column_names is None

    assert isinstance(stmt.values, list) and len(stmt.values) == 2
    v1, v2 = stmt.values
    assert isinstance(v1.lead_expr, Literal) and v1.lead_expr.dtype is int and v1.lead_expr.value == 2
    assert isinstance(v2.lead_expr, Literal) and v2.lead_expr.dtype is str and v2.lead_expr.value == "bob"


def test_insert_missing_comma_in_values_raises():
    """
    VALUES list must be comma-separated. ExpressionParser already raises on malformed tuples.
    """
    sql = "INSERT INTO users VALUES (1 'oops')"
    tokens = Tokenizer().tokenize(sql)
    parser = InsertStatementParser(tokens)
    with pytest.raises(ParsingException):
        parser.parse()


def test_insert_extra_tokens_after_statement_are_leftover():
    """
    Match the style of the 'extra tokens remain' assertion from DropTable tests.
    We build tokens manually (no EOF) so it's easy to see leftovers.
    """
    tokens = make_tokens([
        ("INSERT", TokenType.KEYWORD),
        ("INTO", TokenType.KEYWORD),
        ("users", TokenType.IDENTIFIER),
        ("VALUES", TokenType.KEYWORD),
        ("(", TokenType.LPAREN),
        ("1", TokenType.NUMBER_LITERAL),
        (",", TokenType.COMMA),
        ("'x'", TokenType.STRING_LITERAL),
        (")", TokenType.RPAREN),
        ("junk", TokenType.IDENTIFIER),  # <-- extra stuff
    ])
    parser = InsertStatementParser(tokens)
    stmt = parser.parse()

    assert stmt.table_name == "users"

    assert parser.tokens  # not empty
