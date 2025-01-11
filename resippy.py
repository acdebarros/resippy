# resippy

import sqlite3
import argparse
import atexit

# Get sqlite3 database
connection = sqlite3.connect('resippy.db')
cursor = connection.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS menu (id INTEGER PRIMARY KEY, name TEXT, drumlin_rating INT, ian_rating INT, lina_rating INT, last_made TEXT)')
connection.commit()

# Add New Recipe to Database
def new_recipe(args, **kwargs):
    """
    Adds a new recipe to the database.
    When a new recipe is made, I need to:
        * Add it to the menu table
        * Create a new ingredients table for it
        * 

    Arguments:
        recipe_information(dict): Information passed from the command that at the very least MUST include the recipe name. May also include drumlin_rating, lina_rating, ian_rating, and last_made values.
        mode(str): One of 'manual' or 'URL'

    """
    # Parse argument
    recipe_information = {k:v for k,v in args.items() if v is not None}
    recipe_information['name'] = recipe_information.pop('new')
    columns = ", ".join(recipe_information.keys())
    placeholders = ", ".join(['?'] * len(recipe_information))
    query = "INSERT INTO menu ({0}) VALUES ({1})".format(columns, placeholders)
    try:
        # Add the new recipe to the database
        cursor.execute(query, list(recipe_information.values()))
        connection.commit()
        return True, ''
    except Exception as e:
        return False, e
    
def create_parser():
    """
    Creates a parser for the program.
    """
    parser = argparse.ArgumentParser()

    # Menu Parsers
    ## For adding a new recipe
    parser.add_argument('--new', help="Name of the recipe you would like to add to the menu")
    parser.add_argument('--drumlin_rating', type=int, help="Drumlin's rating of the recipe")
    parser.add_argument('--ian_rating', type=int, help="ian's rating of the recipe")
    parser.add_argument('--lina_rating', type=int, help="Lina's rating of the recipe")
    parser.add_argument('--last_made', type=int, help="Date the recipe was last made")

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
            print("An error has ocurred. Please try again. \n Error Information: {error}".format(error))

