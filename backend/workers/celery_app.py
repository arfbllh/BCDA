from celery import Celery, Task

celery_app = Celery("bcancerportal")


class AppContextTask(Task):
    """Runs the task inside ``celery_app.flask_app`` app context (set in init_celery)."""

    abstract = True

    def __call__(self, *args, **kwargs):
        app = getattr(celery_app, "flask_app", None)
        if app is None:
            return self.run(*args, **kwargs)
        with app.app_context():
            return self.run(*args, **kwargs)


def init_celery(app):
    celery_app.flask_app = app
    celery_app.conf.update(
        broker_url=app.config["CELERY_BROKER_URL"],
        result_backend=app.config["CELERY_RESULT_BACKEND"],
        task_always_eager=app.config["CELERY_TASK_ALWAYS_EAGER"],
        task_ignore_result=False,
    )
    celery_app.Task = AppContextTask
    return celery_app
