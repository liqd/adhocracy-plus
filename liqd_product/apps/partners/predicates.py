import rules


@rules.predicate
def is_partner_admin(user, partner):
    if hasattr(partner, 'has_admin'):
        return partner.has_admin(user)
    return False
