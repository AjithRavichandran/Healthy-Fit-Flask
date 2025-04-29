from flask import Blueprint, g, render_template,  current_app, flash, request ,redirect, url_for
from .models import User
from flask_login import login_required, current_user
from .models import User
from .formula import *

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')


@main.route('/user/<int:user_id>')
def some_view(user_id):
    session = g.db  # or current_app.session if using app-level session
    user = session.query(User).filter(User.id == user_id).first()
    return render_template('dashboard.html', user=user)


@main.route('/edit_step1/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_step1(user_id):
    user = g.db.query(User).filter(User.id == user_id).first()

    if request.method == 'POST':
        user.name = request.form['name']
        user.phone = request.form['phone']
        user.age = request.form['age']
        user.gender = request.form['gender']
        user.current_weight = request.form['current_weight']
        user.height = request.form['height']

        g.db.commit()
        
        return redirect(url_for('main.edit_step2', user_id=user.id))

    return render_template('edit_step1.html', user=user)

@main.route('/edit_step2/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_step2(user_id):
    user = g.db.query(User).filter(User.id == user_id).first()

    if request.method == 'POST':
        try:
            print("🟡 Received POST data:", request.form)

            if request.form.get('target_weight'):
                user.target_weight = float(request.form['target_weight'])

            if request.form.get('activity_level'):
                user.activity_level = float(request.form['activity_level'])

            if request.form.get('pace'):
                user.pace = float(request.form['pace'])

            # Recalculate BMI and adjusted calories
            user.bmi = calculate_bmi(user.current_weight, user.height)
            daily_calories = calculate_tdee(user.gender, user.current_weight, user.height, user.age, user.activity_level)

            calorie_adjustment = {4: 250, 2: 500, 1.3: 750}.get(user.pace, 500)

            adjusted_calories = (
                daily_calories - calorie_adjustment
                if user.target_weight < user.current_weight
                else daily_calories + calorie_adjustment
            )

            print(f"🧮 Calculated adjusted calories: {adjusted_calories:.2f}")

            if adjusted_calories < 1400:
                flash(f"⚠️ Adjusted calories too low: {adjusted_calories:.2f}", 'danger')
                bmi = user.bmi
                status, recommended_weight = recommend_weight(bmi, user.height, user.current_weight)
                return render_template(
                    'edit_step2.html',
                    user=user,
                    bmi=bmi,
                    status=status,
                    recommended_weight=recommended_weight,
                    calorie_warning=f"⚠️ Adjusted calories too low: {adjusted_calories:.2f} kcal"
                )

            user.adjusted_calories = adjusted_calories
            g.db.commit()

            flash("✅ Step 2 updated successfully", "success")
            return redirect(url_for("main.some_view", user_id=user.id))

        except Exception as e:
            print("❌ Exception during POST in edit_step2:", str(e))
            g.db.rollback()
            flash(f"Something went wrong: {e}", "danger")

            bmi = calculate_bmi(user.current_weight, user.height)
            status, recommended_weight = recommend_weight(bmi, user.height, user.current_weight)
            return render_template(
                'edit_step2.html',
                user=user,
                bmi=bmi,
                status=status,
                recommended_weight=recommended_weight
            )

    # GET Request
    bmi = calculate_bmi(user.current_weight, user.height)
    status, recommended_weight = recommend_weight(bmi, user.height, user.current_weight)
    return render_template(
        'edit_step2.html',
        user=user,
        bmi=bmi,
        status=status,
        recommended_weight=recommended_weight
    )
