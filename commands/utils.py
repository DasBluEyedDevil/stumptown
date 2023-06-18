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


def columns(col=[], col2=[], col3=[]):
    # now we need to determine which list is the longest.
    longest = max(col, col2, col3)

    # now we need to pad the lists.
    if col < longest:
        for i in range(longest - col):
            col.append((" ", " "))
    if col2 < longest:
        for i in range(longest - col2):
            col2.append((" ", " "))
    if col3 < longest:
        for i in range(longest - col3):
            col3.append((" ", " "))
    # now we need to print the lists.
    for i in range(longest):
        output = ANSIString(col[i]).ljust(26)
        output += ANSIString(col2[i]).ljust(26)
        output += ANSIString(col3[i]).ljust(26)

    return output


def format(key="", val=0, width=24, just="rjust", type="", temp=0):
    title = "|w" if val else "|x"
    text_val = "|w" if val else "|x"
    text_val += str(val) + "|n"
    try:
        parts = key.split("(")
        parts[1] = parts[1].split(")")[0]
        parts[0] = " ".join(map(lambda x: x.capitalize(), parts[0].split(" ")))
        parts[1] = " ".join(map(lambda x: x.capitalize(), parts[1].split(" ")))
    except:
        parts = [" ".join(map(lambda x: x.capitalize(), key.split(" "))), ""]

    if (parts[1]) != "":
        title += f"{parts[0]}({parts[1]})"[:width - 3 -
                                           len(ANSIString("{}".format(text_val)))] + ":|n"
    else:
        title += f"{parts[0]}"[:width - 3 -
                               len(ANSIString("{}".format(text_val)))] + ":|n"

    if temp:
        text_val += f"|w({temp})|n"
    if just == "ljust":
        if type == "specialty":
            return ANSIString(ANSIString(title).ljust(20) + ANSIString("{}".format(str(val)))).ljust(width)[0:width]
        else:
            return ANSIString(ANSIString(title).ljust(15) + ANSIString("{}".format(str(val)))).ljust(width)[0:width]
    else:
        if type == "specialty":
            return "  " + ANSIString(ANSIString(title).ljust(width - 2 - len(ANSIString("{}".format(text_val))), ANSIString("|x.|n")) + "{}".format(text_val))
        else:
            return ANSIString(ANSIString(title).ljust(width - len(ANSIString("{}".format(text_val))), ANSIString("|x.|n")) + "{}".format(text_val))
