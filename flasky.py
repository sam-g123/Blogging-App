import os
import sys
import click
from app import create_app, db
from app.models import User, Role, Post
from flask_migrate import Migrate, upgrade
import unittest

# Conditional import for coverage
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

# Create Flask app and configure migration
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

# Shell context for Flask CLI
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Post=Post)

# Deployment task command
@app.cli.command()
def deploy():
    """Run deployment tasks."""
    # Migrate database to latest revision
    upgrade()
    # Create or update user roles
    Role.insert_roles()
    # Ensure all users are following themselves
    User.add_self_follows()

# Test command for Flask CLI
@app.cli.command()
@click.option('--coverage/--no-coverage', default=False, help='Run tests under code coverage.')
def test(coverage):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    tests = unittest.TestLoader().discover('tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()
    sys.exit(0 if result.wasSuccessful() else 1)

# Profiling command for Flask CLI
@app.cli.command()
@click.option('--length', default=25, help='Number of functions to include in the profiler report.')
@click.option('--profile-dir', default=None, help='Directory where profiler data files are saved.')
def profile(length, profile_dir):
    """Start the application under the code profiler."""
    from werkzeug.middleware.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length], profile_dir=profile_dir)
    app.run(debug=False)

# Run the application
if __name__ == '__main__':
    app.run(debug=False)
