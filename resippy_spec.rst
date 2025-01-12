=============================
resippy program specification
=============================

Description
===========
The program is for use by the homehold. Its purpose is to store the recipes we use, as well as our ratings of them and a calendar of when we've cooked them. 

Desired --help
==============
usage: resippy [--version] [--addnew] [--viewrecipe] [--viewmenu]

--version: Current version of the program.

Menu
----
-n, --new: Add a new recipe to the database. Must be followed by the recipe name. Additional optional arguments: [--drumlin_rating], [--ian_rating], [--lina_rating], [--last_made] (if these are not provided, they will be NULL in the table)
--viewmenu: View the whole menu. Additional optional arguments:
	-o, --order: 
	-l, --limit:
	-f, --filter:
-t, --toprecipes: View the menu organized by rating. Must be followed by one of "drumlin", "ian", or "lina". Additional optional arguments:
	-l, --limit:
-u, --update_menu: Update the menu. Must be followed by the recipe name and one of the following: [-drumlin_rating], [-ian_rating], [-lina_rating], [-last_made]
-d, --delete: Delete a recipe from the menu. Must be followed by the recipe name. User will be prompted to confirm [Y/N].
--random: Prints out a random meal from the menu. Additional arguments:
	-f, --filter:

Recipe
------
-i, --ingredients: Prints out the ingredients for a recipe. Must be followed by the recipe name.
--addingredient: Adds an ingredient to the ingredients table. Must be followed by the ingredient name. Additional arguments:
	--unit:
	--quantity:
	--prepmethod:
--viewingredients: View the ingredients for a recipe printed out onto the screen. Must be followed by the recipe name.
--addinstructions: Adds instructions to the instructions table. Must be followed by the file name of the text file containing the instructions.
--addrecipe: Adds both ingredients and instructions. Must be followed by one of the following:
	* The file name of the file containing the recipe
	* A URL to the recipe

Meal Plan
---------
-m, --mealplan: Add to the week's meal plan. Must be followed by a day of the week (all lower-case) and a recipe name. If the recipe name is not present in the database, the user will be prompted to add a new recipe with that name. 
	Adding to the meal plan will also update the last_made value for that recipe in the menu table.
--viewmealplan: Print out the meal plan for the next seven days.

Groceries
---------
--updatestock:
--fridge: 
--pantry:
--freezer
--checkin:
-g, --groceries: 

Help
----
-h, --help: View the help dialogue.
-r, --rating: View the rating system.

Databases
=========
menu: main database
* recipe_id: ID number assigned to the recipe
* recipe_name: Name of the recipe
* drumlin_rating: Drumlin's rating of the recipe.
* ian_rating: Ian's rating of the recipe.
* lina_rating: Lina's rating of the recipe.
* format: The type of meal (e.g., Soup, Salad, Pasta)
* cuisine: e.g., Mexican, American, Thai

recipe_ingredients: brings together ingredients, measurement units, measurement quantity, and prep method for each recipe
* recipe_id: ID number assigned to the recipe 
* ingredient_id: ID number assigned to that ingredient
* quantity_id: ID number assigned to the quantity of that ingredient
* units_id: ID number assigned to the units of that ingredient
* prepmethod_id: ID number assigned to any additional preparation notes for that ingredient

recipe_instructions: the steps for cooking that recipe.
* id: ID number assigned to the recipe
* step: the number of the step
* instructions: the actual instructions for that step

meal_plan: 
* year: the year
* month: the month
* day: the day
* weekday: the weekday
* recipe_id: ID number assigned to the recipe

groceries:

Development Plan
================

Milestone 1: Menu
-----------------
By the end of this milestone, I will have a program that works solely with the "menu" table. It can: add new recipes, print out the whole menu, update existing recipes, delete recipes.
Working commands: -n, --viewmenu, -u, -d

Milestone 2: Menu+
------------------
By the end of this milestone, I will have a program that works solely with the "menu" table. In addition to Milestone 1, it can also: print out pieces of the menu (e.g., only those recipes that Drumlin rated higher than a 4; only those made over a month ago; etc.), organize the printed-out menu by rating or by date.
Working commands: --toprecipes, --filter, --order, --limit

Milestone 3: Ingredients
------------------------
By the end of this milestone, I will have a program that works with the "recipe_ingredients" table. It can: add ingredients to this table using user input, update ingredients. It should also be able to print out all the ingredients for a given recipe.
Working commands: -i, --addingredient, --unit, --quantity, --prepmethod, --viewingredients, --updateingredient

Milestone 4: Recipes
-------------------------
By the end of this milestone, I will have a program that works with the "recipe_instructions" table. It can: add instructions for a recipe to the table from a text file, add both ingredients and instructions from a text file.
Working commands: --addinstructions, --addrecipe

Milestone 6: Meal Planning
--------------------------
By the end of this milestone, I will have a program that works with the "meal_plan" table. It can: add recipes to the meal plan, print out the meal plan for the next seven days.
Working commands: --mealplan, --viewmealplan

Milestone 7: Groceries
----------------------
By the end of this milestone, I will have a program that works with the "groceries" table. It can: 

Milestone 8: URLs
-----------------
By the end of this milestone, I will have a program that can add recipes from a URL.

Milestone 9: Centralized
------------------------
By the end of this milestone, the program will be able to access the same database from several computers.