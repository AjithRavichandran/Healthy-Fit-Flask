from .models import FoodRecommendation

def calculate_bmi(weight, height):
    your_bmi = weight / (height ** 2)
    return round(your_bmi, 1)


def recommend_weight(your_bmi, height, weight, perfect_bmi=21.75):
    h2 = height ** 2
    if your_bmi < 18.5:
        bmi_difference = perfect_bmi - your_bmi
        recommended_weight = weight + (bmi_difference * h2)
        status = 'Underweight'
        return status, round(recommended_weight)
    elif your_bmi > 23:
        bmi_difference = your_bmi - perfect_bmi
        recommended_weight = weight - (bmi_difference * h2)
        status = 'Overweight'
        return status, round(recommended_weight)
    else:
        recommended_weight = weight
        status = "Healthy"
    return status, round(recommended_weight)


def calculate_tdee(gender, weight, height, age, activity_factor):
    if gender.lower() == 'male':
        bmr = 10 * weight + 6.25 * (height * 100) - 5 * age + 5
        daily_calories = bmr * activity_factor
        return round(daily_calories)
    else:
        bmr = 10 * weight + 6.25 * (height * 100) - 5 * age - 161
        daily_calories = bmr * activity_factor
        return round(daily_calories)


def calculate_time_to_target(target_weight, current_weight, pace_factor):
    weight_diff = abs(target_weight - current_weight)
    return weight_diff * pace_factor


# Fat provides 9 calories per gram
def required_fat(target_weight, current_weight, adjusted_calories):
    if target_weight > current_weight:
        fat = (adjusted_calories * 0.30) / 9
        return fat
    elif current_weight > target_weight:
        fat = (adjusted_calories * 0.20) / 9
        return fat
    else:
        fat = (adjusted_calories * 0.25) / 9
        return fat


# 1 gram protein = 4 calories
def required_protein(activity_level, weight):
    if activity_level == 1.2:
        protein = weight * 1
        return protein
    elif activity_level == 1.4:
        protein = weight * 1.25
        return protein
    elif activity_level == 1.6:
        protein = weight * 1.50
        return protein
    else:
        protein = weight * 1.75
        return protein


# 1 gram carbohydrate = 4 calories
def required_carbohydrate(target_weight, current_weight, adjusted_calories):
    if target_weight > current_weight:
        carbohydrate = (adjusted_calories * 0.60) / 4
        return carbohydrate
    elif current_weight > target_weight:
        carbohydrate = (adjusted_calories * 0.40) / 4
        return carbohydrate
    else:
        carbohydrate = (adjusted_calories * 0.50) / 4
        return carbohydrate


# 2 calories per gram.
def required_fibre(gender):
    if gender == 'male':
        fibre = 30
        return fibre
    else:
        fibre = 25
        return fibre


def meal_divide(adjusted_calories):
    main_meal = adjusted_calories / 100 * 24.5
    snacks = adjusted_calories / 100 * 13.25
    main_main_meal = main_meal / 100 * 50
    side_main_meal = main_meal / 100 * 20
    egg = main_meal / 100 * 30
    return round(main_meal), snacks, main_main_meal, side_main_meal, egg


def find_calories(cal_shown, gram10, cal):
    perfect_gram = (gram10 * cal) / cal_shown
    return round(perfect_gram)



def round_dish_count(calories_needed, per_piece_cal, threshold):
    full = calories_needed // per_piece_cal
    extra = 0.5 if calories_needed % per_piece_cal >= threshold else 0
    return round(full + extra, 1)

def find_calories(cal_shown, gram10, cal):
    perfect_gram = (gram10 * cal) / cal_shown
    return round(perfect_gram)

def build_recommendations(user_id, adjusted_calories, current_weight, target_weight):
    main_meal, snacks, main_main_meal, side_main_meal, egg_meal = meal_divide(adjusted_calories)
    recs = []

    # Breakfast main dish
    breakfast_items = {'idly': 70, 'dosa': 110, 'poori': 134}
    thresholds = {'idly': 40, 'dosa': 70, 'poori': 80}
    for item, cal in breakfast_items.items():
        count = round_dish_count(main_main_meal, cal, thresholds[item])
        recs.append(FoodRecommendation(
            recommended_food=item,
            count=count,
            gram=None,
            calories=count * cal,
            user_id=user_id,
            sesion='Breakfast Main Dish',
            ses='breakfast'
        ))

    # Side dishes for Breakfast
    side_dishes = [
        ('Coconut Chutney', 20, 10),
        ('Sambar', 8, 10),
        ('Tomato Chutney', 7, 10)
    ]
    for name, cal_shown, gram10 in side_dishes:
        gram = find_calories(cal_shown, gram10, side_main_meal)
        recs.append(FoodRecommendation(
            recommended_food=name,
            count=None,
            gram=gram,
            calories=round(side_main_meal),
            user_id=user_id,
            sesion='Breakfast Side Dish',
            ses='breakfast'
        ))

    # Breakfast egg
    egg_count = round_dish_count(egg_meal, 63, 37)
    recs.append(FoodRecommendation(
        recommended_food='Egg',
        count=egg_count,
        gram=None,
        calories=egg_count * 63,
        user_id=user_id,
        sesion='Breakfast Egg',
        ses='breakfast'
    ))

    # Lunch main dish
    veg_cal = main_meal * 0.3
    egg_omlete = 127
    lunch_main_cal = main_meal - veg_cal - egg_omlete
    lunch_items = {'sambar rice': 16, 'curd rice': 19, 'veg fried rice': 22}
    for item, per_gm in lunch_items.items():
        grams = lunch_main_cal / per_gm * 20
        recs.append(FoodRecommendation(
            recommended_food=item,
            count=None,
            gram=round(grams),
            calories=round(lunch_main_cal),
            user_id=user_id,
            sesion='Lunch Main Dish',
            ses='lunch'
        ))
    
    # Lunch Side Dish
    side_dishes2 = [
        ('Carrot Beans', 20, 20),
        ('Potato', 25, 20),
        ('Beetroot', 18, 20)
    ]
    for name, cal_shown, gram10 in side_dishes2:
        gram = find_calories(cal_shown, gram10, side_main_meal)
        recs.append(FoodRecommendation(
            recommended_food=name,
            count=None,
            gram=gram,
            calories=round(veg_cal),
            user_id=user_id,
            sesion='Lunch Side Dish',
            ses='lunch'
        ))
    

    # Lunch egg
    recs.append(FoodRecommendation(
        recommended_food='Egg omlete',
        count=1,
        gram=56,
        calories=egg_omlete,
        user_id=user_id,
        sesion='Lunch Egg',
        ses='lunch'
    ))

    # Dinner main dish
    dinner_items = {'sapathi': 85, 'raki dosa': 103, 'parota': 144}
    thresholds = {'sapathi': 40, 'raki dosa': 70, 'parota': 80}
    for item, cal in dinner_items.items():
        count = round_dish_count(main_main_meal, cal, thresholds[item])
        recs.append(FoodRecommendation(
            recommended_food=item,
            count=count,
            gram=None,
            calories=count * cal,
            user_id=user_id,
            sesion='Dinner Main Dish',
            ses='dinner'
        ))

    #Dinner Side Dish
    side_dishes3 = [
        ('Tomato Gravy', 7, 10),
        ('Sambar', 8, 10),
        ('Chicken Gravy', 11, 10)
    ]
    for name, cal_shown, gram10 in side_dishes3:
        gram = find_calories(cal_shown, gram10, side_main_meal)
        recs.append(FoodRecommendation(
            recommended_food=name,
            count=None,
            gram=gram,
            calories=round(side_main_meal),
            user_id=user_id,
            sesion='Dinner Side Dish',
            ses='dinner'
        ))


    # Dinner egg
    recs.append(FoodRecommendation(
        recommended_food='Egg',
        count=egg_count,
        gram=None,
        calories=egg_count * 63,
        user_id=user_id,
        sesion='Night Egg',
        ses='dinner'
    ))

    # Shakes & Snacks
    if target_weight > current_weight:
        shakes = [
            ("Shake (100gm of banana, 3 Almond, 5 Cashew, 2 Dates 50gm of milk, 1 tablespoon pf Chia seed)", 1, 270, 'Shake'),
            ("Shake (100gm of banana, 1 tablespoon Raisins,1 Walnut, 50gm of milk, 1 tablespoon pf Chia seed)", 1, 270, 'Shake')
        ]
        snack = [
            ("2 slice of Bread with 2 tablespoon of Peanut Butter", 1, 250, 'Snack'),
            ("Bread Omelette", 1, 250, 'Snack')
        ]
    else:
        shakes = [
            ("Shake (100gm of banana, 3 Almond, 3 Cashew, 2 Dates, Use Water, 1 teaspoon of Chia seed)", 1, 250, 'Shake'),
            ("Shake (100gm of banana, 1 teaspoon Raisins, 1/2 Walnut, Use Water, 1 teaspoon of Chia seed)", 1, 250, 'Snack')
        ]
        snack = [
            ("2 slice of Bread with 2 teaspoon of Peanut Butter", 1, 230, 'Snack'),
            ("Oil less Homemade Bread Omelette", 1, 230, 'Snack')
        ]

    for food, count, cal, ses in shakes + snack:
        recs.append(FoodRecommendation(
            recommended_food=food,
            count=count,
            gram=None,
            calories=cal,
            user_id=user_id,
            sesion=ses,
            ses=ses.lower()
        ))

    return recs
