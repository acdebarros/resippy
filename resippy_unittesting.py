# resippy.py unit testing

import unittest
from unittest.mock import patch, MagicMock
import sqlite3
import os
from resippy import new_recipe, view_menu
import sys
from io import StringIO

class testDatabaseCreation(unittest.TestCase):
    def setUp(self):
        self.db = 'resippy_test.db'
        self.connection = sqlite3.connect(self.db)
        self.cursor = self.connection.cursor()  

    def tearDown(self):
        self.connection.close()
        os.remove(self.db)
    
    def test_table_creation(self):
        self.cursor.execute('CREATE TABLE IF NOT EXISTS menu (id INTEGER PRIMARY KEY, name TEXT, drumlin_rating INT, ian_rating INT, lina_rating INT, last_made TEXT)')
        self.connection.commit()

        # Check if the table exists
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='menu'")
        result = self.cursor.fetchone()
        self.assertIsNotNone(result)

    def test_table_structure(self):
        self.cursor.execute('CREATE TABLE IF NOT EXISTS menu (id INTEGER PRIMARY KEY, name TEXT, drumlin_rating INT, ian_rating INT, lina_rating INT, last_made TEXT)')
        self.connection.commit()

        # Check the table structure
        self.cursor.execute("PRAGMA table_info(menu)")
        columns = self.cursor.fetchall()
        expected_columns = [
            (0, 'id', 'INTEGER', 0, None, 1),
            (1, 'name', 'TEXT', 0, None, 0),
            (2, 'drumlin_rating', 'INT', 0, None, 0),
            (3, 'ian_rating', 'INT', 0, None, 0),
            (4, 'lina_rating', 'INT', 0, None, 0),
            (5, 'last_made', 'TEXT', 0, None, 0)
        ]
        self.assertEqual(columns, expected_columns)

class testNewRecipe(unittest.TestCase):

    @patch('resippy.cursor')
    @patch('resippy.connection')
    def test_successful_addition(self, mock_connection, mock_cursor):
        args = {'new': 'Spaghetti', 'drumlin_rating': 5, 'ian_rating': 4, 'lina_rating': 3, 'last_made': '01/11/2022'}
        success, message = new_recipe(args)
        self.assertTrue(success)
        self.assertEqual(message, '')
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
    
    @patch('resippy.cursor')
    @patch('resippy.connection')
    def test_minimal_addition(self, mock_connection, mock_cursor):
        args = {'new': 'Spaghetti'}
        success, message = new_recipe(args)
        self.assertTrue(success)
        self.assertEqual(message, '')
        mock_cursor.execute.assert_called_once()
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
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()

    @patch('resippy.cursor')
    @patch('resippy.connection')
    def test_database_error(self, mock_connection, mock_cursor):
        mock_cursor.execute.side_effect = Exception("Database Error")
        args = {'new': 'Spaghetti'}
        success, message = new_recipe(args)
        self.assertFalse(success)
        self.assertIsInstance(message, Exception)
        self.assertEqual(str(message), "Database Error")

    @patch('resippy.cursor')
    @patch('resippy.connection')
    def test_correct_date_format(self, mock_connection, mock_cursor):
        args = {'new': 'Spaghetti', 'last_made': 'not right'}
        success, message = new_recipe(args)
        self.assertFalse(success)
        self.assertEqual(message, 'Incorrect date format for last-made date. Make sure to enter date as DD/MM/YYYY.')
        mock_cursor.execute.assert_not_called()
        mock_connection.commit.assert_not_called()

class TestViewMenu(unittest.TestCase):
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

if __name__ == '__main__':
    unittest.main()