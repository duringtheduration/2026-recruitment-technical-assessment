from dataclasses import dataclass
from typing import List, Dict, Union
from flask import Flask, request, jsonify
import re

# ==== Type Definitions, feel free to add or modify ===========================
@dataclass
class CookbookEntry:
	name: str

@dataclass
class RequiredItem():
	name: str
	quantity: int

@dataclass
class Recipe(CookbookEntry):
	required_items: List[RequiredItem]

@dataclass
class Ingredient(CookbookEntry):
	cook_time: int


# =============================================================================
# ==== HTTP Endpoint Stubs ====================================================
# =============================================================================
app = Flask(__name__)
# Source - https://stackoverflow.com/a/60780210
# Posted by Saeed Ir, modified by community. See post 'Timeline' for change history
# Retrieved 2026-02-22, License - CC BY-SA 4.0
app.json.sort_keys = False # <-- this line is pasted from stack overflow. function is to ensure task 3 returns the result preserving dict order

# Store your recipes here!
# cookbook = {
#     "Skibidi Spaghetti": {
#         "type": "recipe",
#         "requiredItems": [
#             {"name": "Meatball", "quantity": 3},
#             {"name": "Pasta", "quantity": 1},
#             {"name": "Tomato", "quantity": 2}
#         ]
#     },
#     "Meatball": {
#         "type": "recipe",
#         "requiredItems": [
#             {"name": "Beef", "quantity": 2},
#             {"name": "Egg", "quantity": 1}
#         ]
#     },
#     "Pasta": {
#         "type": "recipe",
#         "requiredItems": [
#             {"name": "Flour", "quantity": 3},
#             {"name": "Egg", "quantity": 1}
#         ]
#     },
#     "Beef": {"type": "ingredient", "cookTime": 5},
#     "Egg": {"type": "ingredient", "cookTime": 3},
#     "Flour": {"type": "ingredient", "cookTime": 0},
#     "Tomato": {"type": "ingredient", "cookTime": 2}
# }

cookbook = {}

# Task 1 helper (don't touch)
@app.route("/parse", methods=['POST'])
def parse():
	data = request.get_json()
	recipe_name = data.get('input', '')
	parsed_name = parse_handwriting(recipe_name)
	if parsed_name is None:
		return 'Invalid recipe name', 400
	return jsonify({'msg': parsed_name}), 200

# [TASK 1] ====================================================================
# Takes in a recipeName and returns it in a form that 
def parse_handwriting(recipeName: str) -> Union[str , None]:
	recipeName = recipeName.replace("-", " ").replace("_", " ") #remove hyphen and underscore
	recipeName = "".join([char for char in recipeName if char.isalpha() or char.isspace()]) #nly contain letters and whitespaces
	recipeName = recipeName.title() #first letter capitalise, remaining lowercase
	recipeName = re.sub(r'\s+', ' ', recipeName).strip() #only 1 whitespace. leading and trailing whitespace removed 
	if len(recipeName) <= 0: #if string is all nonsense return none
		return None
	return recipeName

print(parse_handwriting("*^&blah%"))

# [TASK 2] ====================================================================
# Endpoint that adds a CookbookEntry to your magical cookbook
@app.route('/entry', methods=['POST'])
def create_entry():

	try: # try catch incase there's unforseen errors 

		# basic requirements ========================== 
		data = request.get_json() #grab what was entered

		data['name'] = parse_handwriting(data.get('name')) # make sure name is legible. and no duplicates like apple & Apple

		if data.get('name') is None or data.get('name') in cookbook: #block if name is empty or exists in cookbook already
			return 'entry **names** must be unique', 400
		
		if data.get('type') not in ('recipe', 'ingredient'): #block anything that's not recipe or ingredient
			return '**type** can only be "recipe" or "ingredient"', 400 
		
		# recipe check ========================== 
		if data.get('type') == 'recipe': 
			if isinstance(data.get('requiredItems'), list): #check requiredItems is in list format
				for item in data.get('requiredItems'): # check requiredItems only has 1 str and int fields
					if not isinstance(item.get('name'), str) or not isinstance(item.get('quantity'), int) or not len(item.keys()) == 2:
						return 'requiredItems can only contain one string and integer field', 400
			names = [item['name'] for item in data['requiredItems']] # temp list for names in requiredItems list
			if len(names) != len(set(names)): #check if there's duplicates in names in list. 1 element per name
				return "Recipe **requiredItems** can only have one element per name.", 400
		
		# ingredient check ========================== 
		if data.get('type') == 'ingredient': 
			if not isinstance(data.get('cookTime'), int) or data.get('cookTime') < 0 or len(data.keys()) !=3 : #block if cookTime is wrong or if has extra wrong fields
				return '**cookTime** can only be greater than or equal to 0', 400

		# pass ================================
		cookbook[data.get('name')] = data
		print('-=======================')
		print(cookbook)
		return '', 200 # logic defaults to success 
	except: 
		return 'you probably entered something wrong', 400

cookbook = {} #autotester only works if cookbook is empty 

# [TASK 3] ====================================================================
# Endpoint that returns a summary of a recipe that corresponds to a query name
@app.route('/summary', methods=['GET'])
def summary():
	
	# cookbook = {
    # "Skibidi Spaghetti": {
    #     "type": "recipe",
    #     "requiredItems": [
    #         {"name": "Meatball", "quantity": 3},
    #         {"name": "Pasta", "quantity": 1},
    #         {"name": "Tomato", "quantity": 2}
    #     ]
    # },
    # "Meatball": {
    #     "type": "recipe",
    #     "requiredItems": [
    #         {"name": "Beef", "quantity": 2},
    #         {"name": "Egg", "quantity": 1}
    #     ]
    # },
    # "Pasta": {
    #     "type": "recipe",
    #     "requiredItems": [
    #         {"name": "Flour", "quantity": 3},
    #         {"name": "Egg", "quantity": 1}
    #     ]
    # },
    # "Beef": {"type": "ingredient", "cookTime": 5},
    # "Egg": {"type": "ingredient", "cookTime": 3},
    # "Flour": {"type": "ingredient", "cookTime": 0},
    # "Tomato": {"type": "ingredient", "cookTime": 2}
	# }

	# global cookbook
	# cookbook.clear()
	# cookbook = {} #autotester only works if cookbook is empty 

	#initiate variables used later================================== 
	cookTime = 0 
	Ingredientslist = []
	
	# name============================================ 
	name = request.args.get('name') 

	#check if data entered is valid ==================================
	if cookbook.get(name) == None:
		return 'invalid name', 400
	elif cookbook.get(name)['type'] != 'recipe': 
		return 'not a recipe', 400 

	try: #try incase unforseen errors 

		# cooktime ======================================================== 
		def getCookTime(name, quantity): # accept both name and quantity bc quantity is needed for later calculations

			nonlocal cookTime 
			print(cookbook[name])

			try: 
				if cookbook[name]['type'] == 'ingredient': 
					cookTime += cookbook[name]['cookTime'] * quantity # if ingredient, add it to cooktime immediately, multiplying for quantity 
					print(cookTime)
				elif cookbook[name]['type'] == 'recipe': #if recipe, see what logical layers are below it
					requiredItemList = cookbook[name]['requiredItems'] 
					print(requiredItemList)
					for entry in requiredItemList: # for every ingredient or recipe in requireditems
						requiredItemQuantity = entry['quantity']*quantity #ensure quantity is multiplied each time to count everything 
						print(entry)
						getCookTime(entry['name'], requiredItemQuantity) #recursion to reach the bottom most layer (eg. recipe to recipe to ingredients)
				else: 
					return 'invalid cookbook type', 400 #incase cookbook has an invalid entry somehow despite task 2

				return cookTime
			except: 
				return 'something went wrong. possibly recipe entered contains recipe or ingredients not in cookbook', 400
		
		getCookTime(name, 1) #call to calculate. default quantity on all summaries is 1
		print(cookTime)

		# ingredients list =====================================================
		#first make a list of dict of all ingredients 
		def getIngredientsList(name, quantity): # accept both name and quantity bc quantity is needed for later calculations

			nonlocal Ingredientslist
			print(cookbook[name])

			if cookbook[name]['type'] == 'ingredient': 
				# Ingredientslist.append(cookbook[name])
				Ingredientslist.append({"name":name, "quantity":quantity})
				print(cookTime)
			elif cookbook[name]['type'] == 'recipe': #if recipe, see what logical layers are below it
				print('wait')
				requiredItemList = cookbook[name]['requiredItems'] 
				print(requiredItemList)
				for entry in requiredItemList: # for every ingredient or recipe in requireditems
					print(entry)
					requiredItemQuantity = entry['quantity']*quantity #ensure quantity is multiplied each time to count everything 
					getIngredientsList(entry['name'], requiredItemQuantity) #recursion to reach the bottom most layer (eg. recipe to recipe to ingredients)
			else: 
				return 'invalid cookbook type', 400 #incase cookbook has an invalid entry somehow despite task 2

			return Ingredientslist
		
		getIngredientsList(name, 1) #call to calculate. quantity default is 1
		print(Ingredientslist)

		# then merge the duplicate items into one 
		def mergeIngredientsList(Ingredientslist): 
			num = 0 #need num for later
			for entry in Ingredientslist: 
				num += 1 
				print (num) 
				for entry2 in Ingredientslist[num:]: #num: means loop through ingredientslist but exclude the first item
					if entry['name'] == entry2['name']: #so we can compare every item to each other once in ingredientslist
						print(entry['name'])
						print(entry2['name']) 
						entry2['quantity'] += entry['quantity'] #where if items have duplicates, add all the quantity onto one item
						Ingredientslist.remove(entry) #and delete the other item once quantity is added (moved)
						print(Ingredientslist) 
					else: 
						print(entry['name'])
						print(entry2['name']) 
			return Ingredientslist
		
		mergeIngredientsList(Ingredientslist)
		print(Ingredientslist)

		# print(cookTime = getCookTime())
		# cookTime = cookbook[name]
		recipeSummary = {
			"name": name, 
			"cookTime": cookTime, 
			"ingredients": Ingredientslist 

		}
		print("=====================")
		print(cookbook)

	except: #catch here for either unexpected errors or ingredient/recipe not exist in cookbook
		return 'something went wrong. possibly recipe entered contains recipe or ingredients not in cookbook', 400


	return jsonify(recipeSummary), 200


# ===== README =======================================
# 
# autotester notes 
# i ran the autotester on my device. 
# i can pass every test 100% EXCEPT when test 3 is ran after test 2
# in which case i would fail one section in test 3. 
# i suspect this is because task 2 writes to cookbook and task 3 reads from cookbook, 
# meaning test 2 might've polluted cookbook's data for test 3. 
# i have tried to manually clear cookbook in my own subroutines, 
# but that just makes the autotester fail me in a different section, 
# which i suspect is because i wasn't supposed to manually tamper with cookbook in my subroutines 
# i don't think i can fix the issue here in my code. 
# but the code does pass 100% on autotester if test part 3 is ran in isolation 




# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
	app.run(debug=True, port=8080)
