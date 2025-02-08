# resippy
A CLI recipe app for the homehold.

### Usage

usage: resippy.py [-h] [--drumlin_rating DRUMLIN_RATING] [--ian_rating IAN_RATING] [--lina_rating LINA_RATING] [--last_made DD/MM/YYYY] [--cuisine CUISINE] [--dish_type DISH_TYPE] [--viewmenu] [--filter FILTER] [--order ORDERBY] [--limit LIMIT] [--printrecipe RECIPENAME] [--addingredients RECIPENAME CSVPATH] [--addinstructions RECIPENAME TXTPATH] [--rating] [--addtomealplan WEEKDAY RECIPENAME] [--printmealplan] [--groceries] [--save] [--random] [--new RECIPENAME | --update_menu RECIPENAME | --del_recipe RECIPENAME]

options:
  -h, --help            show this help message and exit
  --drumlin_rating DRUMLIN_RATING
                        Drumlin's rating of the recipe
  --ian_rating IAN_RATING
                        ian's rating of the recipe
  --lina_rating LINA_RATING
                        Lina's rating of the recipe
  --last_made DD/MM/YYYY
                        Date the recipe was last made (formatted as DD/MM/YYYY)
  --cuisine CUISINE     Cuisine the dish is from (e.g., Mexican, Thai).
  --dish_type DISH_TYPE
                        Dish type (e.g., pasta, salad, potatoes).
  --viewmenu            View the menu.
  --filter FILTER       Filter you would like to use. Should be formatted as an SQL condition.
  --order ORDERBY       Variable you would like to order the table by (e.g., last_made), as well as ASC or DESC.
  --limit LIMIT         Number of recipes you would like to limit the output to.
  --printrecipe RECIPENAME
                        Name of the recipe you would like to see printed.
  --addingredients RECIPENAME CSVPATH
                        Name of the dish and path to the .csv file containing the recipe. Recipe should be formatted with columns 'ingredient', 'quantity', 'units', and 'prepmethod'.
  --addinstructions RECIPENAME TXTPATH
                        Name of the dish and path to the .txt file containing the instructions. Each instruction should be on a new line.
  --rating              View the rating system.
  --addtomealplan WEEKDAY RECIPENAME
                        Day of the week and the recipe you would like to add to the meal plan.
  --printmealplan       View the existing meal plan.
  --groceries           Create a grocery list for the meals currently in the meal plan.
  --save                Saves the grocery list into a .txt file.
  --random              Print a random recipe name to the terminal.
  --new RECIPENAME      Name of the recipe you would like to add to the menu
  --update_menu RECIPENAME
                        Name of the recipe you would like to update in the menu
  --del_recipe RECIPENAME
                        Name of the recipe you would like to delete from the menu