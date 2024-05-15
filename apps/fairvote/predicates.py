from adhocracy4.modules import predicates as module_pred
from adhocracy4.phases import predicates as phase_pred


@phase_pred.rules.predicate
def phase_allows_buy(user, item):
    if item:
        return phase_pred.has_feature_active(item.module, item.__class__, "buy")
    return False


@module_pred.rules.predicate
def is_allowed_buy_item(user, item):
    if item:
        return module_pred.is_allowed_rate_item(user, item)
    return False
