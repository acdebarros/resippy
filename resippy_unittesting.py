# resippy.py unit testing

import unittest
from unittest.mock import patch
import sqlite3
import os
from resippy import new_recipe, view_menu, setup_database, update_menu, check_date, create_parser
import sys
from io import StringIO

# 3 tests
class testDatabaseCreation(unittest.TestCase):
    def setUp(self):
        self.db = 'resippy_test.db'
        self.connection = sqlite3.connect(self.db)
        self.cursor = self.connection.cursor()  

    def tearDown(self):
        self.connection.close()
        os.remove(self.db)
    
    def test_table_creation(self):
        setup_database(self.cursor, self.connection)

        # Check if the table exists
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='menu'")
        result = self.cursor.fetchone()
        self.assertIsNotNone(result)

    def test_table_structure(self):
        setup_database(self.cursor, self.connection)

        # Check the table structure
        self.cursor.execute("PRAGMA table_info(menu)")
        columns = self.cursor.fetchall()
        expected_columns = [
            (0, 'id', 'INTEGER', 0, None, 1),
            (1, 'name', 'TEXT', 0, None, 0),
            (2, 'drumlin_rating', 'DECIMAL', 0, None, 0),
            (3, 'ian_rating', 'DECIMAL', 0, None, 0),
            (4, 'lina_rating', 'DECIMAL', 0, None, 0),
            (5, 'last_made', 'DATE', 0, None, 0)
        ]
        self.assertEqual(columns, expected_columns)

    def test_unique_name(self):
        setup_database(self.cursor, self.connection)

        self.cursor.execute('INSERT INTO menu (name) VALUES ("Test")')
        self.connection.commit()
        
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute('INSERT INTO menu (name) VALUES ("Test")')
            self.connection.commit()

# 8 tests
class testNewRecipe(unittest.TestCase):
    @patch('resippy.cursor')
    @patch('resippy.connection')
    def test_full_successful_addition(self, mock_connection, mock_cursor):
        args = {'new': 'Spaghetti', 'drumlin_rating': 5, 'ian_rating': 4, 'lina_rating': 3, 'last_made': '01/11/2022'}
        success, message = new_recipe(args)
        self.assertTrue(success)
        self.assertEqual(message, '')
        mock_cursor.execute.assert_called_once_with('INSERT INTO menu (drumlin_rating, ian_rating, lina_rating, last_made, name) VALUES (?, ?, ?, ?, ?)', [5, 4, 3, '2022-11-01', 'Spaghetti'])
        mock_connection.commit.assert_called_once()
    
    @patch('resippy.cursor')
    @patch('resippy.connection')
    def test_minimal_addition(self, mock_connection, mock_cursor):
        args = {'new': 'Spaghetti'}
        success, message = new_recipe(args)
        self.assertTrue(success)
        self.assertEqual(message, '')
        mock_cursor.execute.assert_called_once_with("INSERT INTO menu (name) VALUES (?)", ['Spaghetti'])
        mock_connection.commit.assert_called_once()

    @patch('resippy.cursor')
    @patch('resippy.connection')
    def test_missing_name(self, mock_connection, mock_cursor):
        args = {'new': None, 'drumlin_rating': 5, 'ian_rating': 4, 'lina_rating': 3, 'last_made': '01/11/2022'}
        success, message = new_recipe(args)      
        self.assertFalse(success)  
        self.assertEqual(message, 'Recipe name missing')
        mock_cursor.execute.assert_not_called()
        mock_connection.commit.assert_not_called()

    @patch('resippy.cursor')
    @patch('resippy.connection')
    def test_ignores_none(self, mock_connection, mock_cursor):
        args = {'new': 'Spaghetti', 'drumlin_rating': None, 'ian_rating': None, 'lina_rating': 3, 'last_made': '01/11/2022'}
        success, message = new_recipe(args)
        self.assertTrue(success)
        self.assertEqual(message, '')
        mock_cursor.execute.assert_called_once_with('INSERT INTO menu (lina_rating, last_made, name) VALUES (?, ?, ?)', [3, '2022-11-01', 'Spaghetti'])
        mock_connection.commit.assert_called_once()

    @patch('resippy.cursor')
    @patch('resippy.connection')
    def test_database_error(self, mock_connection, mock_cursor):
        mock_cursor.execute.side_effect = sqlite3.DatabaseError("Database Error")
        args = {'new': 'Spaghetti'}
        success, message = new_recipe(args)
        self.assertFalse(success)
        self.assertEqual(str(message), 'The database "resippy" was not found.')

    @patch('resippy.cursor')
    @patch('resippy.connection')
    def test_correct_date_format_string(self, mock_connection, mock_cursor):
        args = {'new': 'Spaghetti', 'last_made': 'not right'}
        success, message = new_recipe(args)
        self.assertFalse(success)
        self.assertEqual(message, 'Incorrect date format for last-made date. Make sure to enter date as DD/MM/YYYY.')
        mock_cursor.execute.assert_not_called()
        mock_connection.commit.assert_not_called()

    @patch('resippy.cursor')
    @patch('resippy.connection')
    def test_correct_date_format_not_valid_date(self, mock_connection, mock_cursor):
        args = {'new': 'Spaghetti', 'last_made': '32/01/2025'}
        success, message = new_recipe(args)
        self.assertFalse(success)
        self.assertEqual(message, 'Incorrect date format for last-made date. Make sure to enter date as DD/MM/YYYY.')
        mock_cursor.execute.assert_not_called()
        mock_connection.commit.assert_not_called()

    @patch('resippy.cursor')
    @patch('resippy.connection')
    def test_repeat_entry(self, mock_connection, mock_cursor):
        mock_cursor.execute.side_effect = sqlite3.IntegrityError
        success, message = new_recipe({"new":"Spaghetti"})
        self.assertFalse(success)
        self.assertEqual(str(message), 'Spaghetti is already in the homehold menu. If you would like to update this recipe, use --update_menu instead.')
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_not_called()

# 3 tests
class testViewMenu(unittest.TestCase):
    @patch('resippy.cursor')
    @patch('resippy.tabulate')
    def test_basic_functionality(self, mock_tabulate, mock_cursor):
        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = [('Spaghetti', 5, 4, 3, '2023-01-01')]
        mock_cursor.description = [('name',), ('drumlin_rating',), ('ian_rating',), ('lina_rating',), ('last_made',)]
        
        captured_output = StringIO()
        sys.stdout = captured_output
        
        view_menu({})
        
        sys.stdout = sys.__stdout__
        
        self.assertTrue(mock_cursor.execute.called)
        self.assertTrue(mock_cursor.fetchall.called)
        self.assertTrue(mock_tabulate.called)
        self.assertIn('name', captured_output.getvalue())

    @patch('resippy.cursor')
    @patch('resippy.tabulate')
    def test_empty_table(self, mock_tabulate, mock_cursor):
        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = []
        mock_cursor.description = [('name',), ('drumlin_rating',), ('ian_rating',), ('lina_rating',), ('last_made',)]
        
        view_menu({})
        
        mock_tabulate.assert_called_with([], headers=['name', 'drumlin_rating', 'ian_rating', 'lina_rating', 'last_made'], tablefmt="grid", numalign='center')

    @patch('resippy.cursor')
    @patch('resippy.tabulate')
    def test_table_formatting(self, mock_tabulate, mock_cursor):
        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = [('Spaghetti', 5, 4, 3, '2023-01-01')]
        mock_cursor.description = [('name',), ('drumlin_rating',), ('ian_rating',), ('lina_rating',), ('last_made',)]
        
        view_menu({})
        
        mock_tabulate.assert_called_with(
            [('Spaghetti', 5, 4, 3, '2023-01-01')],
            headers=['name', 'drumlin_rating', 'ian_rating', 'lina_rating', 'last_made'],
            tablefmt="grid",
            numalign='center'
        )

# 8 tests
class testUpdateMenu(unittest.TestCase):
    @patch('resippy.connection')
    @patch('resippy.cursor')
    def test_basic_functionality(self, mock_cursor, mock_connection):
        args = {'update_menu':"Spaghetti", "drumlin_rating":1}
        mock_cursor.fetchall.return_value = [(1,)]
        success, message = update_menu(args)
        self.assertTrue(success)
        self.assertEqual(message, "")
        self.assertEqual(mock_cursor.execute.call_count, 2)
        mock_connection.commit.assert_called_once()
        
    @patch('resippy.connection')
    @patch('resippy.cursor')
    def test_not_in_menu(self, mock_cursor, mock_connection):
        args = {'update_menu':"Spaghetti", "drumlin_rating":1}
        mock_cursor.fetchall.return_value = []
        success, message = update_menu(args)
        self.assertFalse(success)
        self.assertEqual(message, "Spaghetti was not found in the menu. If you would like to add it, please use --new.")
        mock_connection.commit.assert_not_called()
        mock_cursor.execute.assert_called_once()

    @patch('resippy.connection')
    @patch('resippy.cursor')
    def test_missing_additional_arguments(self, mock_cursor, mock_connection):
        args = {'update_menu':"Spaghetti"}
        mock_cursor.fetchall.return_value = [(1,)]
        success, message = update_menu(args)
        self.assertFalse(success)
        self.assertEqual(message, "Please include the information you need to update (either a rating or a last-made date).")
        mock_connection.commit.assert_not_called()
        mock_cursor.execute.assert_called_once()
        
    @patch('resippy.cursor')
    @patch('resippy.connection')
    def test_missing_name(self, mock_connection, mock_cursor):
        args = {'update_menu': None, 'drumlin_rating': 5, 'ian_rating': 4, 'lina_rating': 3, 'last_made': '01/11/2022'}
        success, message = update_menu(args)      
        self.assertFalse(success)  
        self.assertEqual(message, 'Recipe name missing!')
        mock_cursor.execute.assert_not_called()
        mock_connection.commit.assert_not_called()

    @patch('resippy.cursor')
    @patch('resippy.connection')
    def test_ignores_none(self, mock_connection, mock_cursor):
        args = {'update_menu': 'Spaghetti', 'drumlin_rating': None, 'ian_rating': None, 'lina_rating': 3, 'last_made': '01/11/2022'}
        mock_cursor.fetchall.return_value = [(1,)]
        success, message = update_menu(args)
        self.assertTrue(success)
        self.assertEqual(message, '')
        self.assertEqual(mock_cursor.execute.call_count, 2)
        mock_connection.commit.assert_called_once()

    @patch('resippy.cursor')
    @patch('resippy.connection')
    def test_database_error(self, mock_connection, mock_cursor):
        mock_cursor.fetchall.return_value = [(1,)]
        mock_cursor.execute.side_effect = sqlite3.DatabaseError("Database Error")
        args = {'update_menu': 'Spaghetti', 'drumlin_rating': 5}
        success, message = update_menu(args)
        self.assertFalse(success)
        self.assertEqual(str(message), 'The database "resippy" was not found.')

    @patch('resippy.cursor')
    @patch('resippy.connection')
    def test_correct_date_format_string(self, mock_connection, mock_cursor):
        args = {'update_menu': 'Spaghetti', 'last_made': 'not right'}
        mock_cursor.fetchall.return_value = [(1,)]
        success, message = update_menu(args)
        self.assertFalse(success)
        self.assertEqual(message, 'Incorrect date format for last-made date. Make sure to enter date as DD/MM/YYYY.')
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_not_called()

    @patch('resippy.cursor')
    @patch('resippy.connection')
    def test_correct_date_format_not_valid_date(self, mock_connection, mock_cursor):
        args = {'update_menu': 'Spaghetti', 'last_made': '32/01/2025'}
        mock_cursor.fetchall.return_value = [(1,)]
        success, message = update_menu(args)
        self.assertFalse(success)
        self.assertEqual(message, 'Incorrect date format for last-made date. Make sure to enter date as DD/MM/YYYY.')
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_not_called()

# 4 tests
class testCheckDate(unittest.TestCase):
    def test_correct_pattern(self):
        input_date = "01/11/2022"
        success, message, output_date = check_date(input_date)
        self.assertTrue(success)
        self.assertEqual(message, "")
        self.assertEqual(output_date, "2022-11-01")

    def test_not_string(self):
        input_date = "date"
        success, message, output_date = check_date(input_date)
        self.assertFalse(success)
        self.assertEqual(message, "Incorrect date format for last-made date. Make sure to enter date as DD/MM/YYYY.")
        self.assertEqual(output_date, "")

    def test_wrong_format(self):
        input_date = "2022/11/01"
        success, message, output_date = check_date(input_date)
        self.assertFalse(success)
        self.assertEqual(message, "Incorrect date format for last-made date. Make sure to enter date as DD/MM/YYYY.")
        self.assertEqual(output_date, "")

    def test_not_valid_date(self):
        input_date = "30/02/2022"
        success, message, output_date = check_date(input_date)
        self.assertFalse(success)
        self.assertEqual(message, "Date out of range for month. Please double-check last-made date, and input it as DD/MM/YYYY.")
        self.assertEqual(output_date, "")

# 3 tests
class testCreateParser(unittest.TestCase):
    def setUp(self):
        self.parser = create_parser()

    def test_parser_arguments(self):
        parsed = self.parser.parse_args(['--new', 'Spaghetti', '--drumlin_rating', '5', '--ian_rating', '5', '--lina_rating', '5', '--last_made', "2019", '--viewmenu'])
        self.assertEqual(parsed.new, "Spaghetti")
        self.assertEqual(parsed.drumlin_rating, 5)
        self.assertEqual(parsed.ian_rating, 5)
        self.assertEqual(parsed.lina_rating, 5)
        self.assertEqual(parsed.last_made, "2019")
        self.assertTrue(parsed.viewmenu)

    def test_parser_mutually_exclusive(self):
        with self.assertRaises(SystemExit):
            parsed = self.parser.parse_args(['--new', 'Spaghetti', '--del_recipe', "Curry"])
    
    def test_parser_rating_values(self):
        with self.assertRaises(SystemExit):
            parsed = self.parser.parse_args(['--ian_rating', '70'])

if __name__ == '__main__':
    unittest.main()