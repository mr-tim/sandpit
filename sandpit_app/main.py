from beaker.middleware import SessionMiddleware

from webapp import app
from webapp.core import current_user

if __name__ == '__main__':
    session_opts = {
        'session.data_dir': '/sandpit/sessions/data',
        'session.lock_dir': '/sandpit/sessions/lock',
        'type': 'file'

    }

    @app.context_processor
    def inject_current_user():
    	return dict(current_user=current_user)

    app.wsgi_app = SessionMiddleware(app.wsgi_app, session_opts)
    app.run(host='0.0.0.0', debug=True)