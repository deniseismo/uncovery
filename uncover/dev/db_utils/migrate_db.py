from flask_migrate import MigrateCommand, Migrate
from flask_script import Manager
from uncover import create_app, db

app = create_app()
app.app_context().push()

migrate = Migrate(app, db, render_as_batch=True)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    manager.run()
