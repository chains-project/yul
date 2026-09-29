import io
import os
import tempfile
import unittest

from tabular import Table, load_csv, load_csvs, write_csv


class LoaderTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def _write(self, name, text):
        path = os.path.join(self.tmpdir, name)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
        return path

    def test_load_from_path(self):
        path = self._write("basic.csv", "name,age\nalice,30\nbob,25\n")
        table = load_csv(path)
        self.assertEqual(table.headers, ["name", "age"])
        self.assertEqual(table.rows, [["alice", "30"], ["bob", "25"]])

    def test_headers_are_stripped(self):
        path = self._write("spaces.csv", " name , age \nalice,30\n")
        table = load_csv(path)
        self.assertEqual(table.headers, ["name", "age"])

    def test_load_from_stream(self):
        table = load_csv(io.StringIO("a,b\n1,2\n3,4\n"))
        self.assertEqual(table.shape, (2, 2))

    def test_semicolon_delimiter(self):
        path = self._write("semi.csv", "a;b\n1;2\n")
        table = load_csv(path, delimiter=";")
        self.assertEqual(table.headers, ["a", "b"])
        self.assertEqual(table.rows, [["1", "2"]])

    def test_sniffed_delimiter(self):
        path = self._write("sniff.csv", "a\tb\tc\n1\t2\t3\n")
        table = load_csv(path, delimiter=None)
        self.assertEqual(table.headers, ["a", "b", "c"])

    def test_no_header(self):
        path = self._write("noheader.csv", "1,2\n3,4\n")
        table = load_csv(path, has_header=False)
        self.assertEqual(table.headers, ["column_1", "column_2"])
        self.assertEqual(table.rows, [["1", "2"], ["3", "4"]])

    def test_empty_file(self):
        path = self._write("empty.csv", "")
        table = load_csv(path)
        self.assertEqual(table.headers, [])
        self.assertEqual(table.rows, [])

    def test_write_returns_string(self):
        table = Table(["a", "b"], [[1, 2]])
        text = write_csv(table)
        self.assertEqual(text, "a,b\r\n1,2\r\n")

    def test_write_to_path_roundtrip(self):
        table = Table(["a", "b"], [["1", "2"], ["3", "4"]])
        path = os.path.join(self.tmpdir, "out.csv")
        self.assertIsNone(write_csv(table, path))
        self.assertEqual(load_csv(path), table)

    def test_write_to_stream(self):
        buffer = io.StringIO()
        write_csv(Table(["a"], [["1"]]), buffer)
        self.assertEqual(buffer.getvalue(), "a\r\n1\r\n")

    def test_load_csvs_stacks(self):
        one = io.StringIO("a,b\n1,2\n")
        two = io.StringIO("a,b\n3,4\n")
        table = load_csvs([one, two])
        self.assertEqual(table.rows, [["1", "2"], ["3", "4"]])

    def test_load_csvs_header_mismatch_raises(self):
        with self.assertRaises(ValueError):
            load_csvs([io.StringIO("a,b\n1,2\n"), io.StringIO("a,c\n3,4\n")])


if __name__ == "__main__":
    unittest.main()
