class Table:
    def __init__(self, columns, rows):
        self.columns = list(columns)
        self.rows = [dict(row) for row in rows]

    def __len__(self):
        return len(self.rows)

    def __iter__(self):
        return iter(self.rows)

    def __getitem__(self, index):
        return self.rows[index]

    def __eq__(self, other):
        if not isinstance(other, Table):
            return NotImplemented
        return self.columns == other.columns and self.rows == other.rows

    def __repr__(self):
        return f"Table(columns={self.columns!r}, rows={len(self.rows)})"

    def copy(self):
        return Table(self.columns, self.rows)

    def column(self, name):
        self._check_column(name)
        return [row[name] for row in self.rows]

    def select(self, *columns):
        for name in columns:
            self._check_column(name)
        rows = [{name: row[name] for name in columns} for row in self.rows]
        return Table(columns, rows)

    def filter(self, predicate):
        return Table(self.columns, [row for row in self.rows if predicate(row)])

    def to_dicts(self):
        return [dict(row) for row in self.rows]

    def _check_column(self, name):
        if name not in self.columns:
            raise KeyError(f"unknown column: {name!r}")
