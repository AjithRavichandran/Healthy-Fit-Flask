def get_valid_phone_number(prompt):
    while True:
        phone = input(prompt)
        if phone.isdigit() and len(phone) == 10:
            return phone
        else:
            print("Invalid phone number. Please enter a 10-digit number.")


def get_valid_name(prompt):
    while True:
        name_strip = input(prompt).strip()
        name = name_strip.upper()
        if name and name.isalpha():
            return name
        else:
            print("Invalid input. Please enter a valid name containing only alphabets.")


def get_valid_gender(prompt):
    valid_genders = {"male", "female"}
    while True:
        gender = input(prompt).lower()
        if gender in valid_genders:
            return gender
        else:
            print("Invalid input. Please enter 'male', 'female'.")


def get_valid_integer(prompt, min_value=None, max_value=None):
    while True:
        try:
            value = int(input(prompt))
            if (min_value is not None and value < min_value) or (max_value is not None and value > max_value):
                print(f"Please enter a value between {min_value} and {max_value}.")
            else:
                return value
        except ValueError:
            print("Invalid input. Please enter a valid integer.")


def get_valid_float(prompt, min_value=None, max_value=None):
    while True:
        try:
            value = float(input(prompt))
            if (min_value is not None and value < min_value) or (max_value is not None and value > max_value):
                print(f"Please enter a value between {min_value} and {max_value}.")
            else:
                return value
        except ValueError:
            print("Invalid input. Please enter valid Number.")
