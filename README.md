# resippy
A CLI recipe app for the homehold.

## Milestone 4

This update finalizes a version of resippy that works with the mealplan table of the resippy database. It can:
- Add recipes to the mealplan;
- Print the mealplan

### Usage

usage: resippy.py [-h] [--drumlin_rating DRUMLIN_RATING] [--ian_rating IAN_RATING] [--lina_rating LINA_RATING] [--last_made DD/MM/YYYY] [--cuisine CUISINE] [--dish_type DISH_TYPE] [--viewmenu] [--filter FILTER] [--order ORDERBY] [--limit LIMIT] [--printrecipe RECIPENAME] [--new RECIPENAME | --update_menu RECIPENAME | --del_recipe RECIPENAME] [--addrecipe RECIPENAME CSVPATH]

options:
-h, --help
show this help message and exit
--drumlin_rating DRUMLIN_RATING
Drumlin's rating of the recipe
--ian_rating IAN_RATING
ian's rating of the recipe
--lina_rating LINA_RATING
Lina's rating of the recipe
--last_made DD/MM/YYYY
Date the recipe was last made (formatted as DD/MM/YYYY)
--cuisine CUISINE
Cuisine the dish is from (e.g., Mexican, Thai).
--dish_type DISH_TYPE
Dish type (e.g., pasta, salad, potatoes).
--viewmenu
View the menu (printed onto the console).
--filter FILTER
Filter you would like to use. Should be formatted as an SQL condition.
--order ORDERBY
Variable you would like to order the table by (e.g., last_made), as well as ASC or DESC.
--limit LIMIT
Number of recipes you would like to limit the output to.
--printrecipe RECIPENAME
Print a recipe to the console. Include the name of the recipe you would like printed.
--new RECIPENAME
Add a new recipe. Include the name of the recipe you would like to add.
--update_menu RECIPENAME
Update a recipe. Include the name of the recipe you would like to update.
--del_recipe RECIPENAME
Delete a recipe. Include the name of the recipe you would like to delete.
--addingredients RECIPENAME CSVPATH
Add the ingredients for a recipe. Include the name of the dish and path to the .csv file containing the recipe. Recipe should be formatted with columns 'ingredient', 'quantity', 'units', and 'prepmethod'.
--addinstructions RECIPENAME TXTPATH
Add the instructions for a recipe. Include the name of the dish and path to the .txt file containing the recipe. Each instruction should be on a new line.
--rating
View the rating system (printed onto the console).
--addtomealplan WEEKDAY RECIPENAME
Day of the week and the recipe you would like to add to the meal plan.
--printmealplan       
View the existing meal plan.

### Next Steps

In the next milestone, I hope to:

- [ ] Create a new "groceries" function that generates, prints, and saves a grocery list based on what's on the meal plan;
- [ ] Add a "random" function that prints out a random recipe and can work with the filter input as well.