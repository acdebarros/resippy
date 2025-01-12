# resippy

import sqlite3
import argparse
import atexit
from datetime import date, datetime
import re

# Get sqlite3 database
connection = sqlite3.connect('resippy.db')
cursor = connection.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS menu (id INTEGER PRIMARY KEY, name TEXT, drumlin_rating DECIMAL, ian_rating DECIMAL, lina_rating DECIMAL, last_made DATE)')
connection.commit()

# Add New Recipe to Database
def new_recipe(args, **kwargs):
    """
    Adds a new recipe to the database.
    When a new recipe is made, I need to:
        * Add it to the menu table
        
    Arguments:
        recipe_information(dict): Information passed from the command that at the very least MUST include the recipe name. May also include drumlin_rating, lina_rating, ian_rating, and last_made values.
    """
    # Parse argument
    try:
        recipe_information = {k:v for k,v in args.items() if v is not None}
        recipe_information['name'] = recipe_information.pop('new')
        if 'last_made' in recipe_information:
            date_pattern = r"(0[1-9]|[12][0-9]|3[01])\/(0[1-9]|1[0,1,2])\/(20)\d{2}"
            assert re.match(date_pattern, recipe_information['last_made']), 'Incorrect date format for last-made date. Make sure to enter date as DD/MM/YYYY.'
            try:
                datetime.strptime(recipe_information['last_made'], "%d/%m/%Y")
            except ValueError:
                pass
            last_made = recipe_information['last_made'].split('/')
            recipe_information['last_made'] = date(int(last_made[2]), int(last_made[1]), int(last_made[0]))
        columns = ", ".join(recipe_information.keys())
        placeholders = ", ".join(['?'] * len(recipe_information))
        query = "INSERT INTO menu ({0}) VALUES ({1})".format(columns, placeholders)
        # Add the new recipe to the database
        cursor.execute(query, list(recipe_information.values()))
        connection.commit()
        return True, ''
    except KeyError:
        return False, 'Recipe name missing'
    except AssertionError:
        return False, 'Incorrect date format for last-made date. Make sure to enter date as DD/MM/YYYY.'
    except Exception as e:
        return False, e

args = {'new': None, 'drumlin_rating': 5, 'ian_rating': 4, 'lina_rating': 3, 'last_made': '01/11/2022'}
new_recipe(args)
    
def create_parser():
    """
    Creates a parser for the program.
    """
    parser = argparse.ArgumentParser()

    # Menu Parsers
    ## For adding a new recipe
    parser.add_argument('--new', help="Name of the recipe you would like to add to the menu")
    parser.add_argument('--drumlin_rating', type=float, help="Drumlin's rating of the recipe")
    parser.add_argument('--ian_rating', type=float, help="ian's rating of the recipe")
    parser.add_argument('--lina_rating', type=float, help="Lina's rating of the recipe")
    parser.add_argument('--last_made', type=str, help="Date the recipe was last made (formatted as DD/MM/YYYY)")

    return parser

def exit_handler():
    """
    Closes the SQL connection when the program is exited or otherwise ends.
    """
    connection.close()

if __name__ == "__main__":
    atexit.register(exit_handler)
    parser = create_parser()
    args = parser.parse_args()
    # Decide on Next Action
    ## Add new recipe
    if args.new:
        recipe_name = args.new
        added, error = new_recipe(vars(args))
        if added:
            print("{} has been added to the homehold menu!".format(recipe_name))
        else:
            print("An error has ocurred. Please try again. \n Error Information: {error}".format(error=error))

