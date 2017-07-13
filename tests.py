import builtins
import unittest
import unittest.mock as mock

import worklog_db

from entry import Entry
from peewee import *
from playhouse.test_utils import test_database


TEST_DB = SqliteDatabase(':memory:')
TEST_DB.connect()
TEST_DB.create_tables([Entry], safe=True)

DATA = {
    "date": "2017-07-12",
    "employee_name": "Mike",
    "minutes": 13,
    "task_name": "Servicing Bikes",
    "notes": "Need to strip bike apart"
}


def mock_input_name(employee_name):
    return 'Ivan'


def mock_input_date(date):
    return '2011-12-12'


def mock_input_task_name(task_name):
    return 'Bike maintenance'


def mock_input_minutes(minutes):
    return 10


def mock_input_notes(notes):
    return 'Greasy'


class GetUserInputsTestCase(unittest.TestCase):

    def test_get_name(self):
        self.saved_input = builtins.input
        builtins.input = mock_input_name
        answer = worklog_db.get_employee_name()
        self.assertEqual(answer, 'Ivan')

    def test_get_name_blank(self):
        self.saved_input = builtins.input
        builtins.input = mock_input_name
        answer = worklog_db.get_employee_name()
        self.assertNotEqual(answer, ValueError)

    def test_get_date(self):
        self.saved_input = builtins.input
        builtins.input = mock_input_date
        answer = worklog_db.get_date()
        self.assertEqual(answer, '2011-12-12')

    def test_get_invalid_date(self):
        self.saved_input = builtins.input
        builtins.input = mock_input_date
        answer = worklog_db.get_date()
        self.assertNotEqual(answer, ValueError)

    def test_get_task_name(self):
        self.saved_input = builtins.input
        builtins.input = mock_input_task_name
        answer = worklog_db.get_task_name()
        self.assertEqual(answer, 'Bike maintenance')

    def test_get_minutes(self):
        self.saved_input = builtins.input
        builtins.input = mock_input_minutes
        answer = worklog_db.get_time_spent()
        self.assertEqual(answer, 10)

    def test_get_invalid_minutes(self):
        with mock.patch('builtins.input', answer="Hello", return_value=10):
            self.assertRaises(ValueError)
            assert worklog_db.get_time_spent()

    def test_get_notes(self):
        self.saved_input = builtins.input
        builtins.input = mock_input_notes
        answer = worklog_db.get_notes()
        self.assertEqual(answer, 'Greasy')

    def test_convert_string_to_datetime(self):
        self.saved_input = builtins.input
        builtins.input = mock_input_notes
        answer = worklog_db.convert_string_to_datetime('2017-07-12')
        self.assertNotEqual(answer, '2017-07-12')


class TestDBEntriesTestCase(unittest.TestCase):
    @staticmethod
    def create_entries():
        Entry.create(
            employee_name=DATA["employee_name"],
            minutes=DATA["minutes"],
            task_name=DATA["task_name"],
            notes=DATA["notes"],
            date=DATA["date"]
        )

    def test_get_employee_name(self):
        with mock.patch('builtins.input', side_effect=["", "Ivan"], return_value=DATA["employee_name"]):
            self.assertNotEqual(worklog_db.get_employee_name(), DATA["employee_name"])

    def test_get_task_name(self):
        with mock.patch('builtins.input', side_effect=["", "Swimming"], return_value=DATA["task_name"]):
            self.assertNotEqual(worklog_db.get_task_name(), DATA["task_name"])

    def test_get_time_spent(self):
        with mock.patch('builtins.input', side_effect=["1", 45], return_value=DATA["minutes"]):
            self.assertRaises(ValueError)
            self.assertNotEqual(worklog_db.get_time_spent(), DATA["minutes"])

    def test_get_notes(self):
        with mock.patch('builtins.input', side_effect=DATA["notes"]):
            self.assertNotEqual(worklog_db.get_notes(), DATA["notes"])

    def test_get_date(self):
        with mock.patch('builtins.input', side_effect=["13/07/2017", "2017-07-13"], return_value=DATA["date"]):
            self.assertRaises(ValueError)
            self.assertNotEqual(worklog_db.get_date(), DATA["date"])

    def test_add_entry(self):
        with mock.patch('builtins.input', side_effect=["2017-07-13", "Ivan", "Swimming", 45, "Triathlon training", "y", ""], return_value=DATA):
            self.assertNotEqual(worklog_db.add_entry()["task_name"], DATA["task_name"])

        with mock.patch('builtins.input', side_effect=["2017-07-13", "Ivan", "Swimming", 45, "Triathlon training", "n", ""], return_value=DATA):
            self.assertEqual(worklog_db.add_entry(), None)

    def test_search_entries(self):
        with test_database(TEST_DB, (Entry,)):
            self.create_entries()
            with mock.patch('builtins.input', side_effect=["a", "Mike", "e"]):
                self.assertTrue(worklog_db.search_entries())

            with mock.patch('builtins.input', side_effect=["b", "2017-07-12", "e"]):
                self.assertTrue(worklog_db.search_entries())

            with mock.patch('builtins.input', side_effect=["c", 13, "e"]):
                self.assertTrue(worklog_db.search_entries())

            with mock.patch('builtins.input',side_effect=["a", ".", "y", "e"]):
                self.assertEqual(worklog_db.search_entries(), None)

            with mock.patch('builtins.input', side_effect=["d", "Servicing Bikes", "e"]):
                self.assertTrue(worklog_db.search_entries())

    def test_check_employee_name_match(self):
        with test_database(TEST_DB, (Entry,)):
            self.create_entries()
            Entry.create(**DATA)
            entries = Entry.select()

            with mock.patch('builtins.input', side_effect=["Mike"]):
                test = worklog_db.check_employee_name_match(entries)
                self.assertEqual(test.count(), 2)

    def test_display_nav_options(self):
        p = "[P] - Previous entry"
        n = "[N] - Next entry"
        q = "[Q] - Return to Main Menu"

        with test_database(TEST_DB, (Entry,)):
            self.create_entries()
            entries = Entry.select()
            Entry.create(**DATA)
            index = 0
            menu = [n, q]

            worklog_db.display_nav_options(index, entries)
            self.assertNotIn(p, menu)

if __name__ == '__main__':
    unittest.main()


# python3 -m unittest tests.py
# coverage run tests.py
# coverage report
# coverage report -m
