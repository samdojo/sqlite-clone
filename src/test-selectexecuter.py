import pytest

from baseexecuter import ExecutingException
from data import Column as OutColumn
from data import Database, Schema, Table
from selectexecuter import SelectExecuter
from selectparser import SelectStatementParser
from sqltokenizer import Tokenizer
from statements import SelectStatement


class TestSelectExecutor:
    def setup_method(self):
        self.db = Database()
        self.db["test_schema"] = Schema()
        schema = self.db["test_schema"]

        # Create test table 1 with mixed data types
        schema["users"] = Table(column_list=["id", "name", "age", "email"])
        schema["users"]["id"] = OutColumn(type=int, default=None)
        schema["users"]["name"] = OutColumn(type=str, default="")
        schema["users"]["age"] = OutColumn(type=int, default=None)
        schema["users"]["email"] = OutColumn(type=str, default="")

        # Create test table 2 with different structure
        schema["products"] = Table(column_list=["product_id", "price", "in_stock"])
        schema["products"]["product_id"] = OutColumn(type=int, default=None)
        schema["products"]["price"] = OutColumn(type=float, default=0.0)
        schema["products"]["in_stock"] = OutColumn(type=bool, default=True)

        # Create empty table
        schema["empty_table"] = Table(column_list=["col1", "col2"])
        schema["empty_table"]["col1"] = OutColumn(type=int, default=None)
        schema["empty_table"]["col2"] = OutColumn(type=str, default="")

        self.exec = SelectExecuter()
        self.tokenizer = Tokenizer()

        # Add some test data to users table
        self._add_test_data()

    def _add_test_data(self):
        """Helper method to add test data to the users table"""
        from statements import Literal

        users_table = self.db["test_schema"]["users"]

        # Add test entries
        test_data = [
            {
                "id": Literal(int, 1),
                "name": Literal(str, "Alice"),
                "age": Literal(int, 25),
                "email": Literal(str, "alice@example.com"),
            },
            {
                "id": Literal(int, 2),
                "name": Literal(str, "Bob"),
                "age": Literal(int, 30),
                "email": Literal(str, "bob@example.com"),
            },
            {
                "id": Literal(int, 3),
                "name": Literal(str, "Charlie"),
                "age": Literal(int, 35),
                "email": Literal(str, "charlie@example.com"),
            },
        ]

        for data in test_data:
            users_table.add_entry(data)

    def test_select_all_columns(self):
        """Test SELECT * returns all columns"""
        tokens = self.tokenizer.tokenize("SELECT * FROM test_schema.users")
        select_statement = SelectStatementParser(tokens).parse()
        result = self.exec.execute(self.db, select_statement)

        assert len(result) == 3
        assert all(len(row) == 4 for row in result)  # 4 columns
        assert all(
            "id" in row and "name" in row and "age" in row and "email" in row
            for row in result
        )

        # Check specific values
        assert result[0]["id"] == 1
        assert result[0]["name"] == "Alice"
        assert result[1]["id"] == 2
        assert result[1]["name"] == "Bob"

    def test_select_specific_columns(self):
        """Test SELECT with specific columns"""
        tokens = self.tokenizer.tokenize("SELECT id, name FROM test_schema.users")
        select_statement = SelectStatementParser(tokens).parse()
        result = self.exec.execute(self.db, select_statement)

        assert len(result) == 3
        assert all(len(row) == 2 for row in result)  # 2 columns
        assert all("id" in row and "name" in row for row in result)
        assert all("age" not in row and "email" not in row for row in result)

        # Check specific values
        assert result[0]["id"] == 1
        assert result[0]["name"] == "Alice"

    def test_select_single_column(self):
        """Test SELECT with single column"""
        tokens = self.tokenizer.tokenize("SELECT name FROM test_schema.users")
        select_statement = SelectStatementParser(tokens).parse()
        result = self.exec.execute(self.db, select_statement)

        assert len(result) == 3
        assert all(len(row) == 1 for row in result)  # 1 column
        assert all("name" in row for row in result)

        names = [row["name"] for row in result]
        assert "Alice" in names
        assert "Bob" in names
        assert "Charlie" in names

    def test_select_from_default_schema(self):
        """Test SELECT from default schema (None)"""
        # Add table to default schema
        self.db[None]["default_table"] = Table(column_list=["col1", "col2"])
        self.db[None]["default_table"]["col1"] = OutColumn(type=int, default=None)
        self.db[None]["default_table"]["col2"] = OutColumn(type=str, default="")

        # Add test data
        from statements import Literal

        self.db[None]["default_table"].add_entry(
            {"col1": Literal(int, 42), "col2": Literal(str, "test")}
        )

        tokens = self.tokenizer.tokenize("SELECT col1 FROM default_table")
        select_statement = SelectStatementParser(tokens).parse()
        result = self.exec.execute(self.db, select_statement)

        assert len(result) == 1
        assert result[0]["col1"] == 42

    def test_select_from_empty_table(self):
        """Test SELECT from empty table"""
        tokens = self.tokenizer.tokenize("SELECT * FROM test_schema.empty_table")
        select_statement = SelectStatementParser(tokens).parse()
        result = self.exec.execute(self.db, select_statement)

        assert result == []

    def test_table_not_found_default_schema(self):
        """Test error when table not found in default schema"""
        tokens = self.tokenizer.tokenize("SELECT * FROM nonexistent_table")
        select_statement = SelectStatementParser(tokens).parse()

        with pytest.raises(ExecutingException) as exc_info:
            self.exec.execute(self.db, select_statement)

        assert "Select table nonexistent_table not found in default schema" in str(
            exc_info.value
        )

    def test_table_not_found_named_schema(self):
        """Test error when table not found in named schema"""
        tokens = self.tokenizer.tokenize("SELECT * FROM test_schema.nonexistent_table")
        select_statement = SelectStatementParser(tokens).parse()

        with pytest.raises(ExecutingException) as exc_info:
            self.exec.execute(self.db, select_statement)

        assert "Select table nonexistent_table not found in schema test_schema" in str(
            exc_info.value
        )

    def test_invalid_columns(self):
        """Test error when selecting non-existent columns"""
        tokens = self.tokenizer.tokenize("SELECT invalid_col FROM test_schema.users")
        select_statement = SelectStatementParser(tokens).parse()

        with pytest.raises(ExecutingException) as exc_info:
            self.exec.execute(self.db, select_statement)

        assert "Column(s) ['invalid_col'] do not exist in table users" in str(
            exc_info.value
        )

    def test_multiple_invalid_columns(self):
        """Test error when selecting multiple non-existent columns"""
        tokens = self.tokenizer.tokenize(
            "SELECT invalid_col1, invalid_col2 FROM test_schema.users"
        )
        select_statement = SelectStatementParser(tokens).parse()

        with pytest.raises(ExecutingException) as exc_info:
            self.exec.execute(self.db, select_statement)

        assert "Column(s)" in str(exc_info.value)
        assert "invalid_col1" in str(exc_info.value)
        assert "invalid_col2" in str(exc_info.value)

    def test_mixed_valid_invalid_columns(self):
        """Test error when some columns exist and some don't"""
        tokens = self.tokenizer.tokenize(
            "SELECT id, invalid_col FROM test_schema.users"
        )
        select_statement = SelectStatementParser(tokens).parse()

        with pytest.raises(ExecutingException) as exc_info:
            self.exec.execute(self.db, select_statement)

        assert "Column(s) ['invalid_col'] do not exist in table users" in str(
            exc_info.value
        )

    def test_select_with_none_values(self):
        """Test SELECT with NULL values in data"""
        # Add entry with some NULL values
        from statements import Literal

        users_table = self.db["test_schema"]["users"]
        users_table.add_entry(
            {
                "id": Literal(int, 4),
                "name": Literal(str, "David"),
                "age": Literal(int, None),
                "email": Literal(str, None),
            }
        )

        tokens = self.tokenizer.tokenize("SELECT id, age FROM test_schema.users")
        select_statement = SelectStatementParser(tokens).parse()
        result = self.exec.execute(self.db, select_statement)

        assert len(result) == 4
        # Find the entry with NULL age
        david_entry = next(row for row in result if row["id"] == 4)
        assert david_entry["age"] is None

    def test_different_data_types(self):
        """Test SELECT with different data types"""
        # Add data to products table
        from statements import Literal

        products_table = self.db["test_schema"]["products"]
        products_table.add_entry(
            {
                "product_id": Literal(int, 1),
                "price": Literal(float, 19.99),
                "in_stock": Literal(bool, True),
            }
        )
        products_table.add_entry(
            {
                "product_id": Literal(int, 2),
                "price": Literal(float, 29.99),
                "in_stock": Literal(bool, False),
            }
        )

        tokens = self.tokenizer.tokenize(
            "SELECT product_id, price, in_stock FROM test_schema.products"
        )
        select_statement = SelectStatementParser(tokens).parse()
        result = self.exec.execute(self.db, select_statement)

        assert len(result) == 2
        assert all(
            "product_id" in row and "price" in row and "in_stock" in row
            for row in result
        )

        # Check data types are preserved
        assert isinstance(result[0]["product_id"], int)
        assert isinstance(result[0]["price"], float)
        assert isinstance(result[0]["in_stock"], bool)

    def test_column_order_preservation(self):
        """Test that column order is preserved in results"""
        tokens = self.tokenizer.tokenize(
            "SELECT email, id, name FROM test_schema.users"
        )
        select_statement = SelectStatementParser(tokens).parse()
        result = self.exec.execute(self.db, select_statement)

        assert len(result) == 3
        # Check that columns appear in the order specified in SELECT
        first_row_keys = list(result[0].keys())
        assert first_row_keys == ["email", "id", "name"]

    def test_empty_column_list(self):
        """Test SELECT with empty column list (should behave like SELECT *)"""
        # Create a statement with empty columns list
        select_statement = SelectStatement(
            table_name="users", schema_name="test_schema", alias=None, columns=[]
        )

        result = self.exec.execute(self.db, select_statement)

        assert len(result) == 3
        assert all(len(row) == 4 for row in result)  # All columns returned
        assert all(
            "id" in row and "name" in row and "age" in row and "email" in row
            for row in result
        )
