from background_task import background


@background(schedule=0)
def raise_background_error(e):
    raise Exception(e)
