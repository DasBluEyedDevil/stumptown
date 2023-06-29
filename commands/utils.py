from evennia.utils.ansi import ANSIString


def target(context):
    key = context.lhs.lower()
    target = context.caller
    instance = ""
    value = context.rhs or ""
    specialty = ""

    # determine if we're setting a target and stat
    if "/" in key:
        target = context.caller.search(
            key.split("/")[0], global_search=True)
        key = key.split("/")[1]

        if not key:
            return

        # Split the key into the fixed key.
        key = context.lhs.split("/")[1]
        target = context.caller

    key = key.split("(")
    if len(key) > 1:
        instance = context.args.split("(")[1]
        instance = instance.split(")")[0]

    key = key[0]

    # split the value into the value and specialty
    if "/" in value:
        specialty = value.split("/")[1]
        value = value.split("/")[0]
    return {
        "target": target,
        "key": key,
        "value": value,
        "instance": instance,
        "specialty": specialty
    }


def is_approved(target):
    try:
        if target.db.stats["approved"] == True or target.perm_check("Admin"):
            return True
        else:
            return False
    except:
        return False


def is_ic(target):
    if target.db.stats["ic"] == True:
        return True
    else:
        return False
