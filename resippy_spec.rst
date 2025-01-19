=============================
resippy program specification
=============================

Description
===========
The program is for use by the homehold. Its purpose is to store the recipes we use, as well as our ratings of them and a calendar of when we've cooked them. 

Desired Functionality
=====================
Menu
----
--new: Add a new recipe to the database. Must be followed by the recipe name. Additional optional arguments: [--drumlin_rating], [--ian_rating], [--lina_rating], [--last_made] (if these are not provided, they will be NULL in the table)
--viewmenu: View the whole menu. Additional optional arguments: [--order], [--filter], [--limit]
--toprecipes: View the menu organized by rating. Must be followed by one of "drumlin", "ian", or "lina". Additional optional arguments: [--limit], [--filter]
--update_menu: Update the menu. Must be followed by the recipe name and one of the following: [--drumlin_rating], [--ian_rating], [--lina_rating], [--last_made] 
--delete: Delete a recipe from the menu. Must be followed by the recipe name. User will be prompted to confirm [Y/N].
--random: Prints out a random meal from the menu. Additional arguments: [--filter]

Recipe
------
--ingredients: Prints out the ingredients for a recipe. Must be followed by the recipe name.
--addingredient: Adds an ingredient to the ingredients table. Must be followed by the ingredient name. Additional arguments: [--unit], [--quantity], [--prepmethod]
--viewingredients: View the ingredients for a recipe printed out onto the screen. Must be followed by the recipe name.
--addinstructions: Adds instructions to the instructions table. Must be followed by the file name of the text file containing the instructions. 

Meal Plan
---------
--mealplan: Add to the week's meal plan. Must be followed by a day of the week (all lower-case) and a recipe name. If the recipe name is not present in the database, the user will be prompted to add a new recipe with that name. Adding to the meal plan will also update the last_made value for that recipe in the menu table.
--viewmealplan: Print out the meal plan for the next seven days.
--groceries: Generates a groceries list based on the current meal plan.

Help
----
-h, --help: View the help dialogue.
--rating: View the rating system (1-5 Stars)

Databases
=========
menu: main database
- recipe_id: ID number assigned to the recipe
- recipe_name: Name of the recipe
- drumlin_rating: Drumlin's rating of the recipe.
- ian_rating: Ian's rating of the recipe.
- lina_rating: Lina's rating of the recipe.
- format: The type of meal (e.g., Soup, Salad, Pasta)
- cuisine: e.g., Mexican, American, Thai

recipe_ingredients: brings together ingredients, measurement units, measurement quantity, and prep method for each recipe
- recipe_id: ID number assigned to the recipe 
- ingredient_id: ID number assigned to that ingredient
- quantity: Amount of that ingredient
- unit_id: ID number assigned to the units of that ingredient
- prepmethod_id: ID number assigned to any additional preparation notes for that ingredient

recipe_instructions: the steps for cooking that recipe.
- id: ID number assigned to the recipe
- step: the number of the step
- instructions: the actual instructions for that step

meal_plan: 
- weekday: the weekday
- recipe_id: ID number assigned to the recipe

ingredients
- ingredient_id: ID number assigned to that ingredient
- ingredient_name: Name of the ingredient

units:
- unit_id: ID number assigned to the units of that ingredient
- unit_name: Name of the unit (e.g., teaspoon, can, cup, grams)

prepmethod:
- unit_id: ID number assigned to the units of that ingredient
- prepmethod_name: Name of the prep method (e.g., 'room temperature', 'diced')

groceries:
- ingredient_id: ID number assigned to that ingredient
- quantity: Amount of that ingredient
- unit_id: ID number assigned to the units of that ingredient

Development Plan
================
Milestone 1: Menu
-----------------
By the end of this milestone, I will have a program that works solely with the "menu" table. It can: add new recipes, print out the whole menu, update existing recipes, delete recipes.

Milestone 2: Menu+
------------------
By the end of this milestone, I will have a program that works solely with the "menu" table. In addition to Milestone 1, it can also: print out pieces of the menu (e.g., only those recipes that Drumlin rated higher than a 4; only those made over a month ago; etc.), organize the printed-out menu by rating or by date.

Milestone 3: Ingredients
------------------------
By the end of this milestone, I will have a program that works with the "recipe_ingredients", "ingredients", "units", and "prepmethod" tables. It can: add ingredients to this table using user input, update ingredients. It should also be able to print out all the ingredients for a given recipe.

Milestone 4: Recipes
-------------------------
By the end of this milestone, I will have a program that works with the "recipe_instructions" table. It can: add instructions for a recipe to the table from a text file.

Milestone 5: Meal Planning
--------------------------
By the end of this milestone, I will have a program that works with the "meal_plan" table. It can: add recipes to the meal plan, print out the meal plan for the next seven days.

Milestone 6: Groceries
----------------------
By the end of this milestone, I will have a program that works with the "groceries" table. It can: add the required ingredients for that week's meal plan to the table. It should also remove any previous ingredients.
