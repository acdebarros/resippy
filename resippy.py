# resippy

import sqlite3
import argparse
import atexit
from datetime import date, datetime
import re
from tabulate import tabulate

# Get sqlite3 database
connection = sqlite3.connect('resippy.db')
cursor = connection.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS menu (id INTEGER PRIMARY KEY, name TEXT, drumlin_rating DECIMAL, ian_rating DECIMAL, lina_rating DECIMAL, last_made DATE)')
connection.commit()

# Add New Recipe to Database
def new_recipe(args, **kwargs):
    """
    Adds a new recipe to the database.
        
    Arguments:
        args(dict): Contains required argument --new and potential optional arguments --drumlin_rating, --lina_rating, --ian_rating, and --last_made.
    
    Returns:
        If added properly, returns True and an empty string.
        If not added properly, returns False and the error.
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

def view_menu(args, **kwargs):
    """
    Prints out the menu onto the console for easy viewing.

    Args:
        args(dict): Contains potential optional arguments --order, --limit, and/or --filter.
    """
    # Get Menu
    cursor.execute("SELECT * FROM menu")
    menu = cursor.fetchall()
    
    # Print the headings
    headers = [description[0] for description in cursor.description]
    print(tabulate(menu, headers=headers, tablefmt="grid", numalign='center'))

def update_menu(args, **kwargs):
    """Updates an entry in the menu.

    Args:
        args (dict): Contains required argument --update_menu and potential optional arguments --drumlin_rating, --lina_rating, --ian_rating, and --last_made.
    """
    # Get Current Recipe Values
    cursor.execute("SELECT id FROM menu WHERE name=?", (args['update_menu'],))
    recipe_id = cursor.fetchall()
    recipe_id = recipe_id[0][0]

    # Find new updates from args
    potential_updates = {k:v for k, v in args.items() if v is not None}
    potential_arguments = ["drumlin_rating", "lina_rating", "ian_rating", "last_made"]
    updates = {k:v for k, v in potential_updates.items() if k in potential_arguments}
    if "last_made" in updates:
        date_pattern = r"(0[1-9]|[12][0-9]|3[01])\/(0[1-9]|1[0,1,2])\/(20)\d{2}"
        try:
            datetime.strptime(updates['last_made'], "%d/%m/%Y")
            if not re.match(date_pattern, updates['last_made']):
                raise ValueError
        except ValueError:
            return False, 'Incorrect date format for last-made date. Make sure to enter date as DD/MM/YYYY.'
        last_made = updates['last_made'].split('/')
        updates['last_made'] = date(int(last_made[2]), int(last_made[1]), int(last_made[0]))
    updates_query = ""
    for update in updates.keys():
        updates_query += "{column}={new_value},".format(column=update, new_value=updates[update])
        updates_query = updates_query[:-1]
    condition_query = "id={recipe_id}".format(recipe_id=recipe_id)
    query = "UPDATE menu SET {updates} WHERE {condition}".format(updates=updates_query, condition=condition_query)

    # Add the new recipe to the database
    cursor.execute(query)
    connection.commit()
    return True, ''
    

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
    parser.add_argument('--viewmenu', action="store_true", help="View the menu.")
    parser.add_argument('--update_menu', help="Name of the recipe you would like to update in the menu")
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
    if args.viewmenu:
        view_menu(vars(args))
    if args.update_menu:
        updated, error = update_menu(vars(args))
        if updated:
            print("{} has been updated in the homehold menu!".format(args.update_menu))
        else:
            print("An error has ocurred. Please try again. \n Error Information: {error}".format(error=error))
