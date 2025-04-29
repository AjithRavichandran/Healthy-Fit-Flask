from HealthyFit import create_app
from HealthyFit.extensions import Base, engine

app = create_app()

with app.app_context():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    app.run(debug=True)
