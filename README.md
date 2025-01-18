# resippy
A CLI recipe app for the homehold.

## Milestone 1

This update finalizes a version of resippy that works solely with the SQL "menu" table in the resippy.db database. It can:
- Add new recipes to the menu, with additional ratings and 'last-made' date;
- Print out the whole menu into the console;
- Update existing recipe values with different ratings and last-made dates;
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
--viewmenu
View the menu (printed onto the console)
--new NEW
Add a new recipe. Include the name of the recipe you would like to add.
--update_menu UPDATE_MENU
Update a recipe. Include the name of the recipe you would like to update.
--del_recipe DEL_RECIPE
Delete a recipe. Include the name of the recipe you would like to delete.

### Next Steps

In the next milestone, I hope to:

- [x] Update the viewmenu option such that I can also filter the menu based on ratings or last-made dates;
- [ ] Update the viewmenu option such that I can organize the rows by rating or by last_made dates;
- [ ] Limit the printed recipes to a certain number rather than printing the entire menu
- [ ] Add a "Dish Type" column to the menu table that includes options such as "Pasta", "Soup", "Salad", etc.
- [ ] Add a "Cuisine" column to the menu table that includes options such as "Mexican", "Thai", etc.
