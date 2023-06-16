"""
This module contains the commands for character generation.

"""

from evennia.commands.default.muxcommand import MuxCommand
from world.data import BIO, get_trait_list, SPLATS, PHYSICAL, MENTAL, SOCIAL, SKILLS, STATS
from evennia.utils.ansi import ANSIString
from .utils import target, format


class cmdSplat(MuxCommand):
    """
    This is the command to set a sphere on a character. This must be
    done before any other chargen commands can be used.

    Usage:
        +splats to see a list of valid splats.
        +splat [<target>=]<splat> - Sets the splat of the character.

    """

    key = "+splat"
    aliases = ["splat", "+splats", "splats"]
    locks = "cmd:all()"
    help_category = "chargen"

    def func(self):

        target = self.caller
        splat = self.args.lower()

        # check for a target
        if self.rhs:
            target = self.caller.search(
                self.lhs, global_search=True)
            if not target:
                self.caller.msg("|wSPLAT>|n Could not find target.")
                return

            splat = self.rhs
            target.db.stats.splat = splat

        # if there are no args, list the splats available.
        if not self.args:
            self.caller.msg(
                "|wSPLAT>|n Valid splats are: |w{}|n".format(
                    ", ".join(map(lambda x: ANSIString(f"|w{x.capitalize()}|n"), SPLATS)))
            )
            return

        # Check if a player is already approved.
        if target.db.approved == True:
            self.caller.msg("|wSPLAT>|n You are already approved.")
            return

        # check for a valid splat
        if splat not in SPLATS:
            self.caller.msg("|wSPLAT>|n That is not a valid splat.")
            self.caller.msg("|wSPLAT>|n Valid splats are: |w{}|n".format(
                ", ".join(map(lambda x: ANSIString(f"|w{x.capitalize()}|n"), SPLATS)))
            )
            return

        # set the splat
        target.db.stats["splat"] = splat.lower()
        target.db.stats["bio"] = {"splat": splat.lower()}

        self.caller.msg(
            "|wSPLAT>|n |c{}'s|n splat has set to |w{}|n.".format(target.name, target.db.stats["splat"].upper()))


class cmdCg(MuxCommand):
    """
    This command is used to create a character. it is the main 
    method of setting tour character's chargen settings.

    WARNING!!  Before you can use this command, you must set your 
    splat with +splat!

    Usage:
        +stat [<target>/]<trait>=[<value>][/<specialty>]

        examples:
            +stat strength=3
            +stat  athletics=2/Running

            +stat Diablerie/strength=3
            +stat Diablerie/athletics=2/Running

            To reset a stat, leave the value blank.  When you resete 
            a stat, you must also reset the specialties.

                +stat strength=

            To reset a specialty, leave the specialty blank.

                +stat athletics=/Running

        To reset your whole +sheet use |r+stats/wipe|n.

    See also:  +splat +sheet

    """
    key = "+stats"
    aliases = ["stats", "stat", "+stat"]
    locks = "cmd:all()"
    help_category = "chargen"

    def func(self):
        # Unapproved characters can use this command.
        if self.caller.db.stats["approved"] == True and not self.caller.locks.check_lockstring(self.caller, "perm(Admin)"):
            self.caller.msg("You are already approved.")
            return

        # if the command was +stats/wipe me=confirm, then wipe the stats.
        if self.switches[0] == "wipe" and self.rhs == "confirm":
            self.caller.db.stats = STATS
            self.caller.msg("|wSTATS>|n Your stats have been wiped.")
            return

        # if the command was +stats/wipe. then comfirm they need to use +stats/wipe me=confirm
        if self.switches[0] == "wipe":
            self.caller.msg(
                "|wSTATS>|n You are about to wipe your stats.  This cannot be undone.")
            self.caller.msg(
                "|wSTATS>|n To confirm, use: |r+stats/wipe me=confirm|n")
            return

        if not self.args:
            self.caller.msg("|wSTATS>|n Usage: +stat <trait>=<value>")
            return

        # check for a target
        tar = target(self).get("target")
        key = target(self).get("key")
        instance = target(self).get("instance")
        value = target(self).get("value")
        specialty = target(self).get("specialty")

        # check if caller is target.  Only admins can set other people's stats.
        if self.caller != tar and not self.caller.locks.check_lockstring(self.caller, "perm(Admin)"):
            self.caller.msg("|wSTATS>|n You can only set your own stats.")
            return

        # check for a valid target
        if not tar.db.stats["splat"]:
            self.caller.msg(
                "|wSTATS>|n You must set |c%s's|n splat first." % tar.get_display_name(self.caller))
            return

        # check for a valid key
        traits = get_trait_list(key)
        try:
            key = traits.get("trait")
        except AttributeError:
            self.caller.msg("|wSTATS>|n That is not a valid trait.")
            return

        # check for good values
        try:
            self.rhs = int(self.rhs)
        except ValueError:
            pass

        # check to see if we pass the check
        if traits["check"]:

            if not traits["check"](tar.db.stats):
                self.caller.msg("|wSTATS>|n> " + traits["check_message"])
                return

        # check for instance
        if instance and traits.get("instanced"):
            key = "%s(%s)" % (key.capitalize(), instance.capitalize())

        elif instance and not traits.get("instance"):
            self.caller.msg("|wSTATS>|n That trait does not have instances.")
            return

        elif not instance and traits.get("instance"):
            self.caller.msg(
                "|wSTATS>|n You must specify an (instance) for |w%s()|n." % traits.get(key.capitalize()))
            return

        # check for spwcialties [<value>][/<specialty>]
        # to set a specialty, you must set a value and have a value in the key trait first.
        if traits.get("has_specialties") and value and specialty:

            # check for a valid specialty or if no specialties exist, set the value
            if not len(traits["specialties"]):
                print(traits.get("category"))
                # set the  character's trait  if the trait exists
                if tar.db.stats[traits.get("category")].get(key):

                    # update the specialties dictionary entry for the specialty under the key.
                    try:
                        tar.db.stats["specialties"][key][specialty] = value
                    except KeyError:
                        tar.db.stats["specialties"][key] = {specialty: value}

                    self.caller.msg(
                        "|wSTATS>|n Specialty |w%s|n set on |c%s's|n |w%s|n." % (specialty, tar.name, key.upper()))

                    return

            # Else there are specalties defined.  Check for a valid specialty and value
            # check for a valid specialty
            if specialty not in traits["specialties"]:
                self.caller.msg(
                    "|wSTATS>|n That is not a valid specialty for |w%s|n." % key.upper())
                self.caller.msg("|wSTATS>|n Valid specialties are: |w%s|n" % ", ".join(
                    map(lambda x: ANSIString(f"|w{x}|n"), traits["specialties"].keys())))
                return

            try:
                value = int(value)
            except ValueError:
                pass

            # check for a valid value
            if value not in traits["specialties"][specialty]["values"]:
                self.caller.msg(
                    "|wSTATS>|n That is not a valid value for |w%s|n." % key.upper())
                return
            else:
                print(tar.db.stats[traits.get("category")].get(key))
                # set the  character's trait  if the trait exists
                if tar.db.stats[traits.get("category")].get(key):
                    # update the specialties dictionary entry for the specialty under the key.
                    try:
                        tar.db.stats["specialties"][key][specialty] = value
                    except KeyError:
                        tar.db.stats["specialties"][key] = {specialty: value}
                    except AttributeError:
                        tar.db.stats["specialties"] = {key: {specialty: value}}

                    self.caller.msg(
                        "|wSTATS>|n Specialty |w%s|n set on |c%s's|n |w%s|n." % (specialty, tar.name, key.upper()))

                    return
        # end specialties

        # check for a valid value
        # if no value is given then the trait should be rmeoved from the character
        # along with any specialties

        # if no value is given and a matching specialty for the key is found (case insenstiive)
        # then remove the specialty from the character.
        if not value and tar.db.stats["specialties"].get(key).get(specialty):
            del tar.db.stats["specialties"][key][specialty]
            self.caller.msg(
                "|wSTATS>|n Specialty |w%s|n removed from |c%s's|n |w%s|n." % (specialty, tar.name, key.upper()))
            return

        # if no value is given and no specialty is given, then remove the trait from the character.
        # if the trait has specialties, remove them as well.
        # if the trait is an attribute, then just reset it to 1.
        if not value and not specialty:
            if tar.db.stats["specialties"].get(key):
                del tar.db.stats["specialties"][key]
            if tar.db.stats[traits.get("category")].get(key):
                del tar.db.stats[traits.get("category")][key]
            if tar.db.stats["attributes"].get(key):
                tar.db.stats["attributes"][key] = 1
            self.caller.msg(
                "|wSTATS>|n |w%s|n removed from |c%s's|n sheet." % (key.upper(), tar.name))
            return

        # check for valid values
        if traits["values"] and self.rhs not in traits["values"]:
            self.caller.msg(
                "|wSTATS>|n That is not a valid value for |w%s|n." % key.upper())
            return

        # set the value
        try:
            tar.db.stats[traits.get("category")][key] = int(self.rhs)
        except ValueError:
            tar.db.stats[traits.get("category")][key] = self.rhs

        self.caller.msg("|wSTATS>|n |c%s's|n  |w%s|n set to|w %s|n." %
                        (tar.name, key.upper(), self.rhs))


class cmdSheet(MuxCommand):
    """
    This command is used to view a character's sheet. Staff can view any character's
    sheet, but players can only view their own.

    Usage:
        +sheet [<target>]
    """

    key = "+sheet"
    aliases = ["sheet"]
    locks = "cmd:all()"
    help_category = "chargen"

    def show_bio(self, target):
        """
        This method shows the bio of a character.
        """
        # first print the header.
        output = ANSIString(
            "|Y[|n |wCharacter Sheet|n for: |c{}|n |Y]|n".format(target.name)).center(78, ANSIString("|R=|n"))
        bio = []

        for item in BIO:
            traits = get_trait_list(item)

            if traits["check"] and not traits["check"](target.db.stats):
                continue

            # if the bio field passes the check, we add it to the list.
            try:
                val = target.db.stats[traits.get("category")][item].split(" ")
                val = " ".join([x.capitalize() for x in val])
                bio.append(
                    ANSIString(format(key=item.capitalize(), val=val, width=38, just="ljust")))
            except KeyError:
                bio.append(ANSIString(
                    format(item, "", width=38, just="ljust")))

        # Noq peint the bio in two columns.
        count = 0
        for i in range(0, len(bio)):
            if count % 2 == 0:
                output += "\n "
            else:
                output += " "

            count += 1
            output += bio[i]

        self.caller.msg(output)

    def show_attributes(self, target):
        """
        This method shows the attributes of a character.
        """
        self.caller.msg(ANSIString("|w Attributes |n").center(
            78, ANSIString("|R=|n")))
        # first we need to build our three lists.
        mental = []
        physical = []
        social = []

        # now we need to sort the attributes into their lists.

        for key, value in target.db.stats["attributes"].items():
            if key in MENTAL:
                mental.append(format(key, value))
            elif key in PHYSICAL:
                physical.append(format(key, value))
            elif key in SOCIAL:
                social.append((format(key, value)))

        # now we need to print the lists.
        # first print the three headers.
        output = ANSIString("Physical").center(
            26) + ANSIString("Mental").center(26) + ANSIString("Social").center(26)
        self.caller.msg(output)

        # now we need to print the three lists. if one list is shorter than the others, we need to pad it.
        # if the list is shorter than the others, we need to pad it.
        mental_length = len(mental)
        physical_length = len(physical)
        social_length = len(social)

        # now we need to determine which list is the longest.
        longest = max(mental_length, physical_length, social_length)

        # now we need to pad the lists.
        if mental_length < longest:
            for i in range(longest - mental_length):
                mental.append(" ")
        if physical_length < longest:
            for i in range(longest - physical_length):
                physical.append(" ")
        if social_length < longest:
            for i in range(longest - social_length):
                social.append(" ")
        # now we need to print the lists.
        for i in range(longest):
            output = " " + physical[i]
            output += "  " + mental[i]
            output += "  " + social[i]

            self.caller.msg(output)

    def show_skills(self, target):
        """
        This method shows the skills of a character.
        """
        self.caller.msg(ANSIString("|w Skills |n").center(
            78, ANSIString("|R=|n")))
        # first we need to build our three lists.
        mental = []
        physical = []
        social = []

        # now we need to sort the Skills into their lists.
        # We need to list all of the skills on the sheet.
        # We fill in the missing values on in the db with a zero.
        for key in SKILLS:
            try:

                value = target.db.stats["skills"][key]
            except KeyError:
                value = 0

            # If the key has any character specialties, we need to send them to the format fuction with special idnication
            # That it's a specialty.
            specialties = target.db.stats["specialties"].get(key)

            if key in MENTAL:
                mental.append(format(key, value))
                if specialties:
                    for specialty in specialties:
                        mental.append(
                            format(specialty, specialties.get(specialty), type="specialty"))
            elif key in PHYSICAL:
                physical.append(format(key, value))
                if specialties:
                    for specialty in specialties:
                        physical.append(
                            format(specialty, specialties.get(specialty), type="specialty"))
            elif key in SOCIAL:
                social.append((format(key, value)))
                if specialties:
                    for specialty in specialties:
                        social.append(
                            format(specialty, specialties.get(specialty), type="specialty"))

        # now we need to print the three lists. if one list is shorter than the others, we need to pad it.
        # if the list is shorter than the others, we need to pad it.
        mental_length = len(mental)
        physical_length = len(physical)
        social_length = len(social)

        # now we need to determine which list is the longest.
        longest = max(mental_length, physical_length, social_length)

        # now we need to pad the lists.
        if mental_length < longest:
            for i in range(longest - mental_length):
                mental.append(" " * 24)
        if physical_length < longest:
            for i in range(longest - physical_length):
                physical.append(" " * 24)
        if social_length < longest:
            for i in range(longest - social_length):
                social.append(" " * 24)
        # now we need to print the lists.
        for i in range(longest):
            output = " " + physical[i]
            output += "  " + mental[i]
            output += "  " + social[i]

            self.caller.msg(output)

    def show_disciplines(self, target):
        """
        This method shows the disciplines of a character.
        """
        output = ANSIString("|w Disciplines |n").center(
            78, ANSIString("|R=|n"))

        # first we build our two list

        disciplines = []
        columns = []
        for key, value in target.db.stats["disciplines"].items():
            disciplines.append(format(key, value, width=24))
            specialties = target.db.stats["specialties"].get(key)

            if specialties:
                for specialty in specialties:
                    disciplines.append(
                        format(specialty, specialties.get(specialty), type="specialty", width=24))
            columns.append(disciplines)
            disciplines = []

         # for each column, get the longest entry and pad the rest of the entries to match.
        for column in columns:
            try:
                max_length = max(len(columns[0]), len(
                    columns[1]), len(columns[2]))
            except IndexError:
                try:
                    max_length = max(len(columns[0]), len(columns[1]))
                except IndexError:
                    max_length = len(columns[0])

            if len(column) < max_length:
                for i in range(max_length - len(column)):
                    column.append(" " * 24)

        # now we need to print the lists by row.  Two columns per row. if we have more than 2 columns, we need to print
        # the first two columns, then the next two columns, etc.
        # if we have an odd number of columns, we need to print the last column by itself.
        # if we have an even number of columns, we need to print the last two columns together.
        # if we have more than 4 columns, we need to print the first two columns, then the next two columns, etc.
        for i in range(0, len(columns), 3):
            for j in range(max_length):
                output += "\n "
                output += columns[i][j]
                if i + 1 < len(columns):
                    output += "  " + columns[i + 1][j]
                if i + 2 < len(columns):
                    output += "  " + columns[i + 2][j]

            if (i + 3 < len(columns)):
                output += "\n"

        if len(columns) > 0:
            self.caller.msg(output.strip())

    def show_advantages(self, target):
        """
        This method shows the advantages of a character.
        """
        output = ANSIString("|w Advantages |n").center(39, ANSIString("|R=|n"))
        output += ANSIString("|w Flaws |n").center(39, ANSIString("|R=|n"))

        # first we build our two lists.
        raw_advantages = target.db.stats["advantages"]
        raw_flaws = target.db.stats["flaws"]
        advantages = []
        flaws = []

        # fill in format entry for advanaages and flaws
        for key, value in raw_advantages.items():
            advantages.append(format(key, value, width=37))
        for key, value in raw_flaws.items():
            flaws.append(format(key, value, width=37))

        # get the max length and pad the end of the list with spaces
        max_length = max(len(raw_advantages), len(flaws))
        if len(raw_advantages) < max_length:
            for i in range(max_length - len(raw_advantages)):
                advantages.append(" " * 36)
        if len(raw_flaws) < max_length:
            for i in range(max_length - len(raw_flaws)):
                flaws.append(" " * 36)

        # now we need to print the lists.
        for i in range(max_length):

            output += "\n " + advantages[i] + "  " + flaws[i]
        if max_length > 0:
            self.caller.msg(output)

    def func(self):
        # check to see if caller
        tar = self.caller
        if self.lhs.lower() == "me" or not self.lhs:
            tar = self.caller
        else:
            tar = self.caller.search(self.args, global_search=True)

        try:
            # player has to ahve a splat set first!
            if not tar.db.stats["bio"].get("splat"):
                self.caller.msg(
                    "|wSTATS>|n |yThey must select a splat before you can view their sheet.|n")
                return
        except TypeError:
            self.caller.msg(
                "|wSTATS>|n Pwemission Denied.")
            return
        except AttributeError:
            self.caller.msg(
                "|wSTATS>|n I can't find that player.")
            return

        # check if the target is the caller, or if the caller is admin.
        if self.caller != tar and not self.caller.locks.check_lockstring(self.caller, "perm(Admin)"):
            self.caller.msg("|wCG>|n You can only view your own sheet.")
            return

        # show the sheet
        self.caller.msg(self.show_bio(tar))
        self.caller.msg(self.show_attributes(tar))
        self.caller.msg(self.show_skills(tar))
        self.caller.msg(self.show_advantages(tar))
        if tar.db.stats["bio"].get("splat") == "vampire":
            self.caller.msg(self.show_disciplines(tar))

        self.caller.msg(ANSIString(ANSIString("|R=|n") * 78))
