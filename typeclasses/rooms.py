"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.objects.objects import DefaultRoom
from evennia.utils.ansi import ANSIString
from .objects import ObjectParent


class Room(ObjectParent, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """

    def return_appearance(self, looker, **kwargs):
        """
        This is the hook for returning the appearance of the room.
        """

        def format_time(time_in_seconds):
            """
            This function takes a time in seconds and returns a string that represents
            that time in a more human-friendly format.
            """
            minutes, seconds = divmod(time_in_seconds, 60)
            hours, minutes = divmod(minutes, 60)
            days, hours = divmod(hours, 24)
            # round seconds
            seconds = int(round(seconds, 0))
            minutes = int(round(minutes, 0))
            hours = int(round(hours, 0))
            days = int(round(days, 0))

            time_str = ""
            if days > 0:
                time_str = f"{days}d"
                return time_str.strip()
            elif hours > 0:
                time_str = f"{hours}h"
                return time_str.strip()
            elif minutes > 0:
                time_str = f"{minutes}m"
                return time_str.strip()
            elif seconds > 0:
                time_str += f"{seconds}s"
                return time_str.strip()

        # Get the description, build the string
        description = self.db.desc

        # build the namestring. This is Name(#id) for admins
        # and Name for all others.
        output = ""
        namestring = self.get_display_name(looker)

        # build the return string
        output += ANSIString("[ |w%s|n ]" %
                             namestring).center(78, ANSIString("|w=|n"))
        output += "\n\n%s\n\n" % description
        # display the characters in the room.
        characters = [char for char in self.contents if char.has_account]
        if characters:
            output += ANSIString("[ |wCharacters|n ]").center(78, "-")
            for char in characters:

                # if the looker can see the character, show the name, idle time and a short_desctiption
                if char.access(looker, "view"):
                    # if the listed char is admin or greater, show a star '* ' before the name

                    if char.locks.check_lockstring(char, "perm(Admin)"):
                        charstring = ANSIString(" |c*|n  %s|n" %
                                                char.get_display_name(looker)).ljust(20)
                    else:
                        charstring = ANSIString("    %s|n" %
                                                char.get_display_name(looker)).ljust(20)

                    # show the idle time.  If the character is the looker, show 0s.
                    if char == looker:
                        charstring += ANSIString("  |w0s|n").rjust(5)
                    else:
                        charstring += ANSIString("%s" %
                                                 format_time(char.idle_time)).rjust(5)

                    # if the character has a short_description, show it. ekse show how to set it.
                    if char.db.short_description:
                        charstring += ANSIString("  %s" %
                                                 char.db.short_description).ljust(55)
                    else:
                        charstring += ANSIString(
                            "  Use '+shortdesc <description>' to set this.|n")

                    output += "\n%s" % charstring

        # display the exits  in the room if there are any
        exits = [exit for exit in self.contents if exit.destination]
        if exits:
            output += "\n" + ANSIString("[ |wExits|n ]").center(78, "-")
            count = 0
            for exit in exits:
                if count % 3 == 0:
                    output += "\n "
                count += 1

                output += ANSIString("%s  " %
                                     exit.get_display_name(looker)).ljust(25)
            output += "\n" + ANSIString("|w=|n" * 78)
        else:
            output += "\n" + ANSIString("|w=|n" * 78)
        return output
