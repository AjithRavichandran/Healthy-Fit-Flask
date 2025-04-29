from flask import Blueprint, render_template, flash, redirect, g, request, url_for, session as flask_session
from .models import User, FoodRecommendation
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import Session
from .formula import *
import traceback
from collections import defaultdict

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        session = g.db
        form = request.form
        username = form['username']

        # Check if username already exists
        existing_user = session.query(User).filter_by(username=username).first()
        if existing_user:
            flash('❌ Username already exists. Please choose a different one.', 'danger')
            return render_template('signup.html', form=form)  # Re-render signup page with form data (optional)

        # Save form data in session
        flask_session['signup_data'] = {
            'username': username,
            'password': generate_password_hash(form['password'], method='pbkdf2:sha256'),
            'name': form['name'],
            'phone': form['phone'],
            'gender': form['gender'],
            'age': float(form['age']),
            'height': float(form['height']),
            'current_weight': float(form['current_weight']),
        }

        # Calculate BMI & recommended weight
        height = flask_session['signup_data']['height']
        weight = flask_session['signup_data']['current_weight']
        bmi = calculate_bmi(weight, height)
        status, recommended_weight = recommend_weight(bmi, height, weight)

        return render_template(
            'signup_step2.html',
            bmi=bmi,
            status=status,
            recommended_weight=recommended_weight
        )

    # GET request: show the signup form
    return render_template('signup.html')


@auth.route('/signup_complete', methods=['POST'])
def signup_complete():
    db_session = None
    try:
        if 'signup_data' not in flask_session:
            flash('Session expired. Please sign up again.', 'danger')
            return redirect(url_for('auth.signup'))

        # Get and save form values to session
        activity_factor = float(request.form['activity_level'])
        pace_level = float(request.form['pace_level'])
        flask_session['activity_level'] = activity_factor
        flask_session['pace'] = pace_level

        # Pull from session
        data = flask_session['signup_data']
        if not all(k in data for k in ['username', 'password', 'name', 'phone', 'gender', 'age', 'height', 'current_weight']):
            flash('Missing required data. Please fill out the form correctly.', 'danger')
            return redirect(url_for('auth.signup'))
        target_weight = float(request.form['target_weight'])

        if target_weight < 30 or target_weight > 300:
            flash('Please enter a reasonable target weight between 30kg and 300kg.', 'danger')
            bmi = calculate_bmi(data['current_weight'], data['height'])
            status, recommended_weight = recommend_weight(bmi, data['height'], data['current_weight'])
            return render_template(
                'signup_step2.html',
                bmi=bmi,
                status=status,
                recommended_weight=recommended_weight,
                target_weight=target_weight,
                selected_activity_level=activity_factor,
                selected_pace_level=pace_level,
            )

        height = data['height']
        current_weight = data['current_weight']
        gender = data['gender']
        age = data['age']

        daily_calories = calculate_tdee(gender, current_weight, height, age, activity_factor)

        bmi = calculate_bmi(current_weight, height)
        calorie_adjustment = {4: 250, 2: 500, 1.3: 750}.get(pace_level, 500)
        adjusted_calories = daily_calories + calorie_adjustment if target_weight > current_weight else daily_calories - calorie_adjustment

        if adjusted_calories < 1400:
            flash(
                f'⚠️ Your adjusted calories is only {adjusted_calories:.2f} kcal, which is below the safe threshold of 1400 kcal.\n'
                f'Please decrease your pace level or increase your target weight.',
                'danger'
            )
            status, recommended_weight = recommend_weight(bmi, height, current_weight)
            return render_template(
                'signup_step2.html',
                bmi=bmi,
                status=status,
                recommended_weight=recommended_weight,
                target_weight=target_weight,
                selected_activity_level=activity_factor,
                selected_pace_level=pace_level,
                calorie_warning=f"⚠️ Your adjusted calories is only {adjusted_calories:.2f} kcal, which is below the safe threshold of 1400 kcal. Please decrease your pace level or increase your target weight."
            )
        

        # Insert into DB now
        with Session() as session:
            try:
                user = User(
                    username=data['username'],
                    password=data['password'],
                    name=data['name'],
                    phone=data['phone'],
                    gender=gender,
                    age=age,
                    height=height,
                    current_weight=current_weight,
                    target_weight=target_weight,
                    bmi=bmi,
                    activity_level=activity_factor,
                    pace=pace_level,
                    adjusted_calories=adjusted_calories,
                )
                session.add(user)
                session.flush()

                recommendations = build_recommendations(user.id, adjusted_calories, current_weight, target_weight)
                session.add_all(recommendations)
                session.commit()
            
            except Exception as e:
                session.rollback()  # Rollback everything if there's any error
                raise e


        flash('🎉 Signup completed successfully!', 'success')
        return redirect(url_for('auth.login'))

    except Exception as e:
        print("❌ Error occurred during signup completion:", e)
        traceback.print_exc()
        flash(f'Error occurred: {str(e)}', 'danger')
        return redirect(url_for('auth.signup'))



@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session = g.db
        user = session.query(User).filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user)
        flash('Logged in successfully!', 'success')
        return redirect(url_for('main.some_view', user_id=user.id))

    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth.route('/food_recommendation/<int:user_id>')
def food_recommendations(user_id):
    with Session() as session:
        user = session.query(User).get(user_id)
        recommendation = session.query(FoodRecommendation).filter_by(user_id=user_id).all()

        grouped = defaultdict(list)
        for recommendations in recommendation:
            print(f"{recommendations.recommended_food} -> {recommendations.sesion}")
            grouped[recommendations.sesion].append(recommendations)

        print("Grouped Keys:", list(grouped.keys()))

        return render_template(
            'food_recommendation.html',
            user=user,
            grouped_recommendations=grouped
        )
