# resippy
A CLI recipe app for the homehold.

## Milestone 2

This update finalizes a version of resippy that works solely with the SQL "menu" table in the resippy.db database. It can:
- Add new recipes to the menu, with additional information on cuisine, dish type, ratings, and 'last-made' date;
- Print out the whole menu into the console;
- Filters, orders, and limits the printed menu in the console using SQL queries;
- Update existing recipe values with different dish types, cuisines, ratings, and last-made dates;
- Delete recipes from the menu

### Usage

usage: resippy.py [-h] [--drumlin_rating DRUMLIN_RATING] [--ian_rating IAN_RATING] [--lina_rating LINA_RATING]
[--last_made LAST_MADE] [--viewmenu]
[--new NEW | --update_menu UPDATE_MENU | --del_recipe DEL_RECIPE]

options:
-h, --help
show this help message and exit
--drumlin_rating DRUMLIN_RATING
Drumlin's rating of the recipe
--ian_rating IAN_RATING
ian's rating of the recipe
--lina_rating LINA_RATING
Lina's rating of the recipe
--last_made LAST_MADE
Date the recipe was last made (formatted as DD/MM/YYYY)
--cuisine CUISINE
Cuisine the dish is from (e.g., Mexican, Thai).
--dish_type DISH_TYPE
Dish type (e.g., pasta, salad, potatoes).
--viewmenu
View the menu (printed onto the console)
--filter FILTER
Filter you would like to use. Should be formatted as an SQL condition.
--order ORDER
Variable you would like to order the table by (e.g., last_made), as well as ASC or DESC.
--limit LIMIT
Number of recipes you would like to limit the output to.
--new NEW
Add a new recipe. Include the name of the recipe you would like to add.
--update_menu UPDATE_MENU
Update a recipe. Include the name of the recipe you would like to update.
--del_recipe DEL_RECIPE
Delete a recipe. Include the name of the recipe you would like to delete.

### Next Steps

In the next milestone, I hope to:

- [ ] Create four new tables: 'recipe_ingredients", "ingredients", "units", and "prepmethod";
- [ ] Add ingredients to these tables, connecting back to the menu using the recipe's id;
- [ ] Update the ingredients in a recipe;
- [ ] Print out all the ingredients for a given recipe
- [ ] Add a "Cuisine" column to the menu table that includes options such as "Mexican", "Thai", etc.
