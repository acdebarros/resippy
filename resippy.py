# resippy

import sqlite3
import sqlparse
import argparse
import atexit
from datetime import date, datetime
import re
from tabulate import tabulate
from sqlparse.tokens import Keyword
import csv

connection = sqlite3.connect('resippy_testing.db')
cursor = connection.cursor()

# Database Set-Up
def setup_database(cursor, connection):
    """
    Sets up the sqlite3 database.

    Arguments:
        connection(sqlite3.Connection object): Connection to the resippy database. 
        cursor(sqlite3.Cursor object): Cursor for the resippy database.
    """
    # Make tables if they do not already exist
    cursor.execute('CREATE TABLE IF NOT EXISTS menu (id INTEGER PRIMARY KEY, name TEXT UNIQUE, dish_type TEXT, cuisine TEXT, drumlin_rating DECIMAL, ian_rating DECIMAL, lina_rating DECIMAL, last_made DATE)')
    connection.commit()

    cursor.execute('CREATE TABLE IF NOT EXISTS ingredients (ingredient_id INTEGER PRIMARY KEY, ingredient_name TEXT UNIQUE)')
    connection.commit()
    
    cursor.execute('CREATE TABLE IF NOT EXISTS units (unit_id INTEGER PRIMARY KEY, unit_name TEXT UNIQUE)')
    connection.commit()

    cursor.execute('CREATE TABLE IF NOT EXISTS prepmethod (prepmethod_id INTEGER PRIMARY KEY, prepmethod_name TEXT UNIQUE)')
    connection.commit()

    cursor.execute('CREATE TABLE IF NOT EXISTS recipe_ingredients (matching_id INTEGER PRIMARY KEY, recipe_id INTEGER, ingredient_id INTEGER, quantity DECIMAL, unit_id INTEGER, prepmethod_id INTEGER, FOREIGN KEY (recipe_id) REFERENCES menu(id), FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id), FOREIGN KEY (unit_id) REFERENCES units(unit_id), FOREIGN KEY (prepmethod_id) REFERENCES prepmethod(prepmethod_id))')
    connection.commit()

# Menu Functions
def new_recipe(args, **kwargs):
    """
    Adds a new recipe to the database.
        
    Arguments:
        args(dict): Contains required argument --new and potential optional arguments --dish_type, --cuisine, --drumlin_rating, --lina_rating, --ian_rating, and --last_made.
    
    Raises:
        KeyError if the recipe name is missing
        AssertionError if the last_made date is not formatted correctly
        IntegrityError if the recipe already exists in the menu
        DatabaseError if something is wrong with the database

    Returns:
        If added properly, returns True and an empty string.
        If not added properly, returns False and the error.
    """
    # Parse argument
    try:
        recipe_data_template = ["new", "dish_type", "cuisine", "drumlin_rating", "lina_rating", "ian_rating", "last_made"]
        recipe_information = {k:v for k,v in args.items() if v is not None and k in recipe_data_template}
        recipe_information['name'] = recipe_information.pop('new')
        if 'last_made' in recipe_information:
            valid, e, recipe_information['last_made'] = check_date(recipe_information['last_made'])
            if not valid:
                raise AssertionError
        columns = ", ".join(recipe_information.keys())
        placeholders = ", ".join(['?'] * len(recipe_information))
        query = "INSERT INTO menu ({0}) VALUES ({1})".format(columns, placeholders)
        # Add the new recipe to the database
        try:
            cursor.execute(query, list(recipe_information.values()))
        except sqlite3.IntegrityError:
            return False, "{} is already in the homehold menu. If you would like to update this recipe, use --update_menu instead.".format(recipe_information['name'])
        connection.commit()
        return True, ''
    except KeyError:
        return False, 'Recipe name missing'
    except AssertionError:
        return False, 'Incorrect date format for last-made date. Make sure to enter date as DD/MM/YYYY.'
    except sqlite3.DatabaseError:
        return False, 'The database "resippy" was not found.'

def view_menu(args, **kwargs):
    """
    Prints out the menu onto the console for easy viewing.

    Args:
        args(dict): Contains potential optional arguments --order, --limit, and/or --filter.
    """
    # Set Up Query
    sql_query = "SELECT * FROM menu"
    # Get Filter
    if args['filter'] != None:
        sql_query += " WHERE "
        sql_query += args['filter']
    if args['order'] != None:
        sql_query += " ORDER BY "
        sql_query += args['order']
    if args['limit'] != None:
        sql_query += " LIMIT "
        sql_query += args['limit']

    cursor.execute(sql_query)
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
    try:
        if args['update_menu'] == None:
            return False, "Recipe name missing!"
        cursor.execute("SELECT id FROM menu WHERE name=?", (args['update_menu'],))
        recipe_id = cursor.fetchall()
        if len(recipe_id) == 1:
            recipe_id = recipe_id[0][0]
        else:
            return False, "{} was not found in the menu. If you would like to add it, please use --new.".format(args['update_menu'])
        # Find new updates from args
        potential_arguments = ["dish_type", "cuisine", "drumlin_rating", "lina_rating", "ian_rating", "last_made"]
        updates = {k:v for k, v in args.items() if v is not None and k in potential_arguments}
        if len(updates) == 0:
            return False, "Please include the information you need to update (either a rating or a last-made date)."
        if "last_made" in updates:
            valid, e, updates['last_made'] = check_date(updates['last_made'])
            if not valid:
                return valid, e
            else:
                updates['last_made'] = '"{update}"'.format(update=updates['last_made'])
        updates_query = ""
        if "cuisine" in updates:
            updates["cuisine"] = '"{cuisine}"'.format(cuisine=updates['cuisine'])
        if "dish_type" in updates:
            updates["dish_type"] = '"{dish_type}"'.format(dish_type=updates['dish_type'])
        for update in updates.keys():
            updates_query += "{column}={new_value},".format(column=update, new_value=updates[update])
        updates_query = updates_query[:-1]
        condition_query = "id={recipe_id}".format(recipe_id=recipe_id)
        query = "UPDATE menu SET {updates} WHERE {condition}".format(updates=updates_query, condition=condition_query)
    # Add the new recipe to the database
        cursor.execute(query)
        connection.commit()
        return True, ''
    except sqlite3.DatabaseError:
        return False, 'The database "resippy" was not found.'

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

def add_recipe(args, recipe_id, **kwargs):
    """
    Reads a .csv ingredients list into the database.

    Args:
        args (dict): Contains required argument --addrecipe.
        recipe_id (int): ID number for the recipe (output from check_recipe_input)

    Returns:
        True and an empty string if the recipe is successfully added.
        False and a string containing the error if the recipe is not successfully added.
    """
    # get path & recipe name
    try:
        path = args['addrecipe'][1]
        recipe_name = args['addrecipe'][0]
        assert recipe_name != ''
        assert path != ''
    except IndexError:
        raise argparse.ArgumentTypeError("The proper arguments were not passed to --addrecipe.")
    except AssertionError:
        raise argparse.ArgumentTypeError("Either the recipe name or the path to the .csv is missing. Please try again.\nPassed Arguments: {args}".format(args=args['addrecipe']))
    # Check that the recipe is not already in the database
    check_existing_query = "SELECT * FROM recipe_ingredients WHERE recipe_id=?"
    cursor.execute(check_existing_query, (recipe_id,))
    if len(cursor.fetchall()) > 0:
        readd = input("A recipe for {r} is already in the database. Would you like to replace it? [Y/N] ".format(r=recipe_name))
        if readd.upper() == "Y":
            remove_recipe_query = "DELETE FROM recipe_ingredients WHERE recipe_id=?"
            cursor.execute(remove_recipe_query, (recipe_id,))
            connection.commit()
        else:
            return False, "The recipe for {} already exists in the database. It has not been altered.".format(recipe_name)
    # Open the .csv
    try:
        with open(path, newline='') as csvfile:
            recipe = csv.reader(csvfile)
            headers = next(recipe)
            for ingredient in recipe:
                ing_id = None
                prep_id = None
                unit_id = None
                ingredient_information = {'recipe_id': recipe_id}
                # Get ingredient id
                if ingredient[0] != "":
                    ing_query = "SELECT ingredient_id FROM ingredients WHERE ingredient_name=?"
                    while ing_id == None:
                        try:
                            cursor.execute(ing_query, (ingredient[0],))
                            ingredient_information["ingredient_id"] = cursor.fetchall()[0][0]
                            ing_id = True
                        except IndexError:
                            # Ingredient does not exist in table: create it
                            ing_make_query = "INSERT INTO ingredients (ingredient_name) VALUES (?)"
                            cursor.execute(ing_make_query, (ingredient[0],))
                            connection.commit()
                else:
                    return False, "One or more of the ingredients is missing a name. Please check the .csv file and then try again."
                # Ensure quantity is an integer
                try:
                    ingredient_information["quantity"] = float(ingredient[1])
                except ValueError:
                    return False, "One or more of the ingredients has a non-numerical quantity. Please check the .csv file and then try again."
                # Get unit ID
                if ingredient[2] != "":
                    unit_query = "SELECT unit_id FROM units WHERE unit_name=?"
                    while unit_id == None:
                        try:
                            cursor.execute(unit_query, (ingredient[2],))
                            ingredient_information["unit_id"] = cursor.fetchall()[0][0]
                            unit_id = True
                        except IndexError:
                            # Unit does not exist in table: create it
                            unit_make_query = "INSERT INTO units (unit_name) VALUES (?)"
                            cursor.execute(unit_make_query, (ingredient[2],))
                            connection.commit()
                # Get prepmethod ID
                if ingredient[3] != "":
                    prep_query = "SELECT prepmethod_id FROM prepmethod WHERE prepmethod_name=?"
                    while prep_id == None:
                        try:
                            cursor.execute(prep_query, (ingredient[3],))
                            ingredient_information['prepmethod_id'] = cursor.fetchall()[0][0]
                            prep_id = True
                        except IndexError:
                            prep_make_query = "INSERT INTO prepmethod (prepmethod_name) VALUES (?)"
                            cursor.execute(prep_make_query, (ingredient[3],))
                            connection.commit()
                # Make a line in the recipe_ingredients table
                columns = ", ".join(ingredient_information.keys())
                placeholders = ", ".join(['?'] * len(ingredient_information))
                rec_ing_query = "INSERT INTO recipe_ingredients ({c}) VALUES ({v})".format(c=columns, v=placeholders)
                cursor.execute(rec_ing_query, list(ingredient_information.values()))
                connection.commit()
    except FileNotFoundError:
        return False, "Error: The file containing the recipe was not found. Please enter the path to the csv file containing the recipe."
    except csv.Error:
        return False, "Error: The file containing the recipe could not be read. Please fix the file and try again."
    return True, ""

# Helper Functions
def check_date(input_date):
    """Ensures that a last_made argument date is in the correct format. Also reformats it.

    Args:
        date (str): The last_made argument passed through the console.
    
    Returns:
        True, an empty string, and the date formatted as a datetime object if the date was correct format.
        False, an error message, and an empty string if the date was out of range or in the incorrect format.    
    """
    date_pattern = r"(0[1-9]|[12][0-9]|3[01])\/(0[1-9]|1[0,1,2])\/(20)\d{2}"
    try:
        if not re.match(date_pattern, input_date):
            raise ValueError
        else:
            try:
                formatted_date = datetime.strptime(input_date, "%d/%m/%Y").strftime('%Y-%m-%d')
                return True, "", formatted_date
            except:
                return False, "Date out of range for month. Please double-check last-made date, and input it as DD/MM/YYYY.", ''
    except ValueError:
        return False, 'Incorrect date format for last-made date. Make sure to enter date as DD/MM/YYYY.', ''

def check_rating(rating):
    """
    Checks whether a provided rating is in the correct range.

    Args:
        rating(string): The rating provided by the user.

    Raises:
        argparse.ArgumentTypeError if the rating is not a number or if it is not between 1.0 and 5.0.
    
    Returns:
        rating(float): The rating reformatted as a float.
    """
    try: 
        rating = float(rating.strip())
    except ValueError:
        raise argparse.ArgumentTypeError("Invalid rating {r}. Ratings must be numbers between 1 and 5.".format(r=rating))
    if not 1.0 <= rating <= 5.0:
        raise argparse.ArgumentTypeError("Invalid rating {r}. Ratings must be numbers between 1 and 5.".format(r=rating))
    return rating

def check_filter(filter):
    """Checks whether the filter input by the user is in the right format.

    Args:
        filter(string): Filter provided by the user; should be formatted as an SQL query.
    
    Raises:
        ValueError if there is no WHERE query within the SQL query.
        ArgumentTypeError if the variable is not in the menu, or if the comparison value is not in the correct format for that variable.
    
    Returns:
        sql_query(string): Filter formatted as an SQL query.
    """
    # Create & parse SQL query
    query = "SELECT * FROM menu WHERE "
    query += filter
    sql_query = sqlparse.parse(query)[0]
    where_query = None

    # Get the WHERE part of the query
    for token in sql_query.tokens:
        if isinstance(token, sqlparse.sql.Where):
            where_query = token

    if where_query is None:
        raise ValueError("No WHERE clause found in the SQL query.")
    
    # Get comparisons from the WHERE part of the query
    comparisons = []
    for token in where_query.tokens:
        if isinstance(token, sqlparse.sql.Comparison):
            comparisons.append(token)
    
    # Find valid variable names
    cursor.execute("SELECT name FROM pragma_table_info('menu')")
    retrieved_columns = cursor.fetchall()
    valid_columns = []
    for col in retrieved_columns:
        valid_columns.append(col[0])
    
    # Iterate over comparisons to validate them
    for comparison in comparisons:
        if comparison.left.normalized not in valid_columns:
            raise argparse.ArgumentTypeError("Invalid filter: the variable {v} was not found in the menu.".format(v=comparison.left.normalized))
        if comparison.left.normalized in ['drumlin_rating', 'lina_rating', 'ian_rating']:
            try:
                float(comparison.right.normalized)
            except ValueError:
                raise argparse.ArgumentTypeError("Invalid rating {r}. Ratings must be numbers between 1 and 5.".format(r=comparison.right.normalized))
            check_rating(comparison.right.normalized)
        elif comparison.left.normalized == "last_made":
            date_correct, message, formatted_date = check_date(comparison.right.normalized)
            if not date_correct:
                raise argparse.ArgumentTypeError(message)
    
    sql_query = sql_query.value
    sql_query = sql_query.split("WHERE")
    sql_query = sql_query[1].strip()

    return sql_query

def check_order(order):
    """_summary_

    Args:
        order (str): A string that should contain a variable and then either ASC or DESC.

    Returns:
        sql_query: Order statement organized as an SQL query.
    """
    # Create & parse SQL query
    query = "SELECT * FROM menu ORDER BY "
    query += order
    sql_query = sqlparse.parse(query)[0]
    order_query = ""

    # Get the ORDER BY part of the query
    order_by_tokens = []
    order_by_found = False

    # Iterate through tokens to find ORDER BY and collect subsequent tokens
    for token in sql_query.tokens:
        if token.ttype is Keyword and token.value.upper() == "ORDER BY":
            order_by_found = True
            continue
        if order_by_found:
            # Stop collecting if we hit another keyword like LIMIT or OFFSET
            if token.ttype is Keyword:
                break
            if not token.is_whitespace:
                order_by_tokens.append(token.value)
    
    # Check validity of order_by statements
    # Find valid variable names
    cursor.execute("SELECT name FROM pragma_table_info('menu')")
    retrieved_columns = cursor.fetchall()
    valid_columns = []
    for col in retrieved_columns:
        valid_columns.append(col[0])    
    for token in order_by_tokens:
        tokens = token.split(",")
        for order in tokens:
            parts_of_query = order.split()
            col_name = parts_of_query[0]
            direction = parts_of_query[1]
            # Check variable
            if col_name not in valid_columns:
                raise argparse.ArgumentTypeError("Invalid ORDER BY statement: the column {c} does not exist in the menu table.".format(c=col_name))
            # Check direction
            if direction not in ["ASC", "DESC"]:
                raise argparse.ArgumentTypeError("Invalid ORDER BY statement: direction must be one of ASC or DESC.")
            # Format for query
            order_query += col_name 
            order_query += " "
            order_query += direction
            order_query += ", "
        
    order_query = order_query[:-2]
    return order_query

def check_limit(limit):
    """_summary_

    Args:
        limit (_type_): _description_

    Returns:
        _type_: _description_
    """
    try:
        int(limit)
    except ValueError:
        raise argparse.ArgumentTypeError("Invalid limit: Limit must be an integer.")
    if int(limit) < 1:
        raise argparse.ArgumentTypeError("Invalid limit: Limit must be 1 or greater.")
    
    return limit

def check_recipe_input(recipe_args):
    """Checks whether a recipe name exists in the menu, and whether the .csv file opens and has the correct headers.

    Args:
        recipe_args (list): Contains two strings: the name of the recipe, and the path to the .csv file.
    Returns:
        recipe_id (int): The recipe's ID number in the menu.
        path (str): The path to the recipe's .csv file.
    """
    name = recipe_args[0]
    path = recipe_args[1]

    # Check that the recipe exists in the menu
    sql_query = "SELECT id FROM menu WHERE name="
    sql_query += "'" + name + "'"

    cursor.execute(sql_query)
    try:
        id = cursor.fetchall()[0][0]
    except IndexError:
        raise argparse.ArgumentTypeError("Error: The recipe {r} does not exist in the menu. Please use --new to add it to the menu before adding its ingredients.".format(r=name))

    # Now check CSV
    req_headers = ['ingredient', 'quantity', 'units', 'prepmethod']
    found_headers = []
    try:
        with open(path, newline='') as csvfile:
            csv_reader = csv.reader(csvfile)
            headers = next(csv_reader)
            if len(headers) != 4:
                raise argparse.ArgumentTypeError("Error: The recipe file does not have the correct amount of headers. Please ensure the csv file contains the headers 'ingredient', 'quantity', 'units', and 'prepmethod'.")
            for i in range(0,4):
                h = headers[i]
                if h in req_headers:
                    found_headers.append(h)
                else:
                    raise argparse.ArgumentTypeError("Error: One or more of the headers in the recipe file is incorrect. Please ensure the csv file contains the headers 'ingredient', 'quantity', 'units', and 'prepmethod'.")
    except FileNotFoundError:
        raise argparse.ArgumentTypeError("Error: The file containing the recipe was not found. Please enter the path to the csv file containing the recipe.")

    return id, path

# I/O Functions
def create_parser():
    """
    Creates a parser for the program.
    """
    parser = argparse.ArgumentParser()

    # Menu Parsers
    ## For adding a new recipe
    parser.add_argument('--drumlin_rating', type=check_rating, help="Drumlin's rating of the recipe")
    parser.add_argument('--ian_rating', type=check_rating, help="ian's rating of the recipe")
    parser.add_argument('--lina_rating', type=check_rating, help="Lina's rating of the recipe")
    parser.add_argument('--last_made', type=str, help="Date the recipe was last made (formatted as DD/MM/YYYY)")
    parser.add_argument('--cuisine', type=str, help="Cuisine the dish is from (e.g., Mexican, Thai).")
    parser.add_argument('--dish_type', type=str, help="Dish type (e.g., pasta, salad, potatoes).")
    parser.add_argument('--viewmenu', action="store_true", help="View the menu.")
    parser.add_argument('--filter', type=check_filter,  help="Filter you would like to use. Should be formatted as an SQL condition.")
    parser.add_argument('--order', type=check_order, help="Variable you would like to order the table by (e.g., last_made), as well as ASC or DESC.")
    parser.add_argument('--limit', type=check_limit, help="Number of recipes you would like to limit the output to.")
    menu_exclusives = parser.add_mutually_exclusive_group()
    menu_exclusives.add_argument('--new', help="Name of the recipe you would like to add to the menu")
    menu_exclusives.add_argument('--update_menu', help="Name of the recipe you would like to update in the menu")
    menu_exclusives.add_argument('--del_recipe', help="Name of the recipe you would like to delete from the menu")
    recipe_exclusives = parser.add_mutually_exclusive_group()
    recipe_exclusives.add_argument('--addrecipe', nargs=2, type=str, help="Name of the dish and path to the .csv file containing the recipe. Recipe should be formatted with columns 'ingredient', 'quantity', 'units', and 'prepmethod'.")
    return parser

def exit_handler():
    """
    Closes the SQL connection when the program is exited or otherwise ends.
    """
    connection.close()

if __name__ == "__main__":
    # Set up parser & exit handler
    parser = create_parser()
    args = parser.parse_args()
    # Get Database
    setup_database(cursor, connection)
    # Set up exit handler
    atexit.register(exit_handler)
    # Decide on Next Action
    ## Add new recipe
    if args.new:
        recipe_name = args.new
        added, error = new_recipe(vars(args))
        if added:
            print("{} has been added to the homehold menu!".format(recipe_name))
        else:
            print("An error has ocurred. Please try again. \nError Information: {error}".format(error=error))
    ## View Menu
    if args.viewmenu:
        view_menu(vars(args))
    ## Update Menu
    if args.update_menu:
        updated, error = update_menu(vars(args))
        if updated:
            print("{} has been updated in the homehold menu!".format(args.update_menu))
        else:
            print("An error has ocurred. Please try again. \nError Information: {error}".format(error=error))
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
                    print("An error has ocurred. Please try again. \nError Information: {error}".format(error=error))
                    deleted = True
            elif confirm.strip().upper() == "N":
                deleted = True
            else:
                confirm = input("Unrecognized argument. Please enter Y or N. \n{} will be permanently deleted from the homehold menu. Are you sure you would like to continue? [Y/N]  ".format(args.del_recipe))
    if args.addrecipe:
        recipe_id, recipe_path = check_recipe_input(args.addrecipe)
        added, error = add_recipe(vars(args), recipe_id)
        if added:
            print("The recipe for {} has been added to the homehold menu!".format(args.addrecipe[0]))
        else:
            print("An error has occurred. Please try again. \nError Information: {error}".format(error=error))