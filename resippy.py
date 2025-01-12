# resippy

# Next steps:
## Add delete function
## Update new_recipe so that it can't add a recipe that's already in the table
## Update update_menu so that it can't update a recipe that doesn't already exist in the table
## Finish unittesting for Version 1

import sqlite3
import argparse
import atexit
from datetime import date, datetime
import re
from tabulate import tabulate

# Database Set-Up
def get_database():
    """
    Accesses the sqlite3 database.
    """
    # Connect to database & create cursor
    connection = sqlite3.connect('resippy.db')
    cursor = connection.cursor()
    # Make tables if they do not already exist
    cursor.execute('CREATE TABLE IF NOT EXISTS menu (id INTEGER PRIMARY KEY, name TEXT, drumlin_rating DECIMAL, ian_rating DECIMAL, lina_rating DECIMAL, last_made DATE, UNIQUE(id, name))')
    connection.commit()

# Menu Functions
def new_recipe(args, **kwargs):
    """
    Adds a new recipe to the database.
        
    Arguments:
        args(dict): Contains required argument --new and potential optional arguments --drumlin_rating, --lina_rating, --ian_rating, and --last_made.
    
    Raises:
        KeyError if the recipe name is missing
        AssertionError if the last_made date is not formatted correctly
        Database Error if something is wrong with the database

    Returns:
        If added properly, returns True and an empty string.
        If not added properly, returns False and the error.
    """
    # Parse argument
    try:
        recipe_arguments = ['new', 'drumlin_rating', 'lina_rating', 'ian_rating', 'last_made']
        recipe_information = {k:v for k,v in args.items() if v is not None and k in recipe_arguments}
        recipe_information['name'] = recipe_information.pop('new')
        if 'last_made' in recipe_information:
            valid, e, recipe_information['last_made'] = check_date(recipe_information['last_made'])
            if not valid:
                raise AssertionError
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
    
    Returns:
        True and an empty string if the recipe is updated correctly.
        False and the error if the last_made date is incorrect.
    """
    # Get Current Recipe Values
    cursor.execute("SELECT id FROM menu WHERE name=?", (args['update_menu'],))
    recipe_id = cursor.fetchall()
    recipe_id = recipe_id[0][0]

    # Find new updates from args
    potential_arguments = ["drumlin_rating", "lina_rating", "ian_rating", "last_made"]
    updates = {k:v for k, v in args.items() if v is not None and k in potential_arguments}

    if "last_made" in updates:
        valid, e, updates['last_made'] = check_date(updates['last_made'])
        if not valid:
            return valid, e
        else:
            updates['last_made'] = '"{update}"'.format(update=updates['last_made'])
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

def delete_recipe(args, **kwargs):
    """Deletes a recipe from the menu.

    Args:
        args (dict): Contains required argument --del_recipe and potential optional arguments --drumlin_rating, --lina_rating, --ian_rating, and --last_made.
        
    Returns:
        True and an empty string if the recipe is deleted
        False and an error string if the recipe was not found in the menu
    """
    # Get Recipe ID
    cursor.execute("SELECT id FROM menu WHERE name=?", (args['del_recipe'],))
    recipe_id = cursor.fetchall()
    if len(recipe_id) == 1:
        recipe_id = recipe_id[0][0]
        id_query = "id=" + str(recipe_id)
    elif len(recipe_id) == 0:
        return False, "{} was not found in the menu. Please try again.".format(args['del_recipe'])
   
    # Delete Query
    query = "DELETE FROM menu WHERE {id}".format(id=id_query)
    cursor.execute(query)
    connection.commit()
    return True, ''

# Helper Functions
def check_date(input_date):
    """Ensures that a last_made argument date is in the correct format. Also reformats it.

    Args:
        date (str): The last_made argument passed through the console.
    """
    date_pattern = r"(0[1-9]|[12][0-9]|3[01])\/(0[1-9]|1[0,1,2])\/(20)\d{2}"
    try:
        if not re.match(date_pattern, input_date):
            raise ValueError
        else:
            formatted_date = datetime.strptime(input_date, "%d/%m/%Y").strftime('%Y-%m-%d')
            return True, "", formatted_date
    except ValueError:
        return False, 'Incorrect date format for last-made date. Make sure to enter date as DD/MM/YYYY.', ''

# I/O Functions
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
    parser.add_argument('--del_recipe', help="Name of the recipe you would like to delete from the menu")
    return parser

def exit_handler():
    """
    Closes the SQL connection when the program is exited or otherwise ends.
    """
    connection.close()

if __name__ == "__main__":
    # Set up parser & exit handler
    atexit.register(exit_handler)
    parser = create_parser()
    args = parser.parse_args()
    # Get Database
    get_database()
    # Decide on Next Action
    ## Add new recipe
    if args.new:
        recipe_name = args.new
        added, error = new_recipe(vars(args))
        if added:
            print("{} has been added to the homehold menu!".format(recipe_name))
        else:
            print("An error has ocurred. Please try again. \n Error Information: {error}".format(error=error))
    ## View Menu
    if args.viewmenu:
        view_menu(vars(args))
    ## Update Menu
    if args.update_menu:
        updated, error = update_menu(vars(args))
        if updated:
            print("{} has been updated in the homehold menu!".format(args.update_menu))
        else:
            print("An error has ocurred. Please try again. \n Error Information: {error}".format(error=error))
    ## Delete a Recipe
    if args.del_recipe:
        confirm = input("{} will be permanently deleted from the homehold menu. Are you sure you would like to continue? [Y/N]  ".format(args.del_recipe))
        deleted = False
        while not deleted:
            if confirm.strip().upper() == "Y":
                deleted, error = delete_recipe(vars(args))
                if deleted:
                    print("{} has been deleted from the menu.".format(args.del_recipe))
                else:
                    print("An error has ocurred. Please try again. \n Error Information: {error}".format(error=error))
                    deleted = True
            elif confirm.strip().upper() == "N":
                deleted = True
            else:
                confirm = input("Unrecognized argument. Please enter Y or N. \n {} will be permanently deleted from the homehold menu. Are you sure you would like to continue? [Y/N]  ".format(args.del_recipe))
