import importlib

from background_task import background


@background(schedule=1)
def send_async_no_object(email_module_name,
                         email_class_name,
                         object, args, kwargs):
    mod = importlib.import_module(email_module_name)
    cls = getattr(mod, email_class_name)
    return cls().dispatch(object, *args, **kwargs)
