"""
This module contains the commands for character generation.

"""

from evennia.commands.default.muxcommand import MuxCommand
from world.data import BIO, get_trait_list, SPLATS, PHYSICAL, MENTAL, SOCIAL, SKILLS
from evennia.utils.ansi import ANSIString
from .utils import target, columns, format


class cmdSplat(MuxCommand):
    """
    This is the command to set a sphere on a character. This must be
    done before any other chargen commands can be used.

    Usage:
        +splat [<target>=]<splat> - Sets the splat of the character.
    """

    key = "+splat"
    aliases = ["splat"]
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
                self.caller.msg("Could not find target.")
                return

            splat = self.rhs
            target.db.stats.splat = splat

        # Check if a player is already approved.
        if target.db.approved == True:
            self.caller.msg("You are already approved.")
            return

        # check for a valid splat
        if splat not in SPLATS:
            self.caller.msg("|wCG>|n That is not a valid splat.")
            self.caller.msg("|wCG>|n Valid splats are: |w{}|n".format(
                ", ".join(SPLATS)))
            return

        # set the splat
        target.db.stats["splat"] = splat
        target.db.stats["bio"]["splat"] = splat

        self.caller.msg(
            "|wCG>|n |c{}'s|n splat has set to |w{}|n.".format(target.name, target.db.stats["splat"]))


class cmdCg(MuxCommand):
    """
    This command is used to create a character. it is the main method of setting 
    tour character's chargen settings.

    Usage:
        +cg [<target>/]<trait>=[<value>]

    """
    key = "+cg"
    aliases = ["+chargen", "chargen", "cg"]
    locks = "cmd:all()"
    help_category = "chargen"

    def func(self):
        # Unapproved characters can use this command.
        if self.caller.db.approved == True and not self.caller.locks.check_lockstring(self.caller, "perm(Admin)"):
            self.caller.msg("You are already approved.")
            return

        # check for a target
        tar = target(self).get("target")
        key = target(self).get("key")
        instance = target(self).get("instance")
        value = target(self).get("value")
        specialty = target(self).get("specialty")

        # check if caller is target.  Only admins can set other people's stats.
        if self.caller != tar and not self.caller.locks.check_lockstring(self.caller, "perm(Admin)"):
            self.caller.msg("|WCG>|n You can only set your own stats.")
            return

        # check for a valid target
        if not tar.db.stats["splat"]:
            self.caller.msg(
                "|wCG>|n You must set |c%s's|n splat first." % tar.name)
            return

        # check for a valid key
        traits = get_trait_list(key)
        try:
            key = traits.get("trait")
        except AttributeError:
            self.caller.msg("|wCG>|n That is not a valid trait.")
            return

        # check for good values
        try:
            self.rhs = int(self.rhs)
        except ValueError:
            pass

        # check to see if we pass the check
        if traits["check"]:

            if not traits["check"](tar.db.stats):
                self.caller.msg("|wCG>|n> " + traits["check_message"])
                return

        # check for instance
        if instance and traits.get("instanced"):
            key = "%s(%s)" % (key.capitalize(), instance.capitalize())

        elif instance and not traits.get("instance"):
            self.caller.msg("|wCG>|n That trait does not have instances.")
            return

        elif not instance and traits.get("instance"):
            self.caller.msg(
                "|wCG>|n You must specify an (instance) for |w%s()|n." % traits.get(key.capitalize()))
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
                        "|wCG>|n Specialty |w%s|n set on |c%s's|n |w%s|n." % (specialty, tar.name, key.upper()))

                    return

            # Else there are specalties defined.  Check for a valid specialty and value
            # check for a valid specialty
            if specialty not in traits["specialties"]:
                self.caller.msg(
                    "|wCG>|n That is not a valid specialty for |w%s|n." % key.upper())
                return

            try:
                value = int(value)
            except ValueError:
                pass

            # check for a valid value
            if value not in traits["specialties"][specialty]["values"]:
                self.caller.msg(
                    "|wCG>|n That is not a valid value for |w%s|n." % key.upper())
                return
            else:
                print(tar.db.stats[traits.get("category")].get(key))
                # set the  character's trait  if the trait exists
                if tar.db.stats[traits.get("category")].get(key):
                    print("made it!!!!")
                    # update the specialties dictionary entry for the specialty under the key.
                    try:
                        tar.db.stats["specialties"][key][specialty] = value
                    except KeyError:
                        tar.db.stats["specialties"][key] = {specialty: value}

                    self.caller.msg(
                        "|wCG>|n Specialty |w%s|n set on |c%s's|n |w%s|n." % (specialty, tar.name, key.upper()))

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
                "|wCG>|n Specialty |w%s|n removed from |c%s's|n |w%s|n." % (specialty, tar.name, key.upper()))
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
                "|wCG>|n |w%s|n removed from |c%s's|n sheet." % (key.upper(), tar.name))
            return

        # check for valid values
        if traits["values"] and self.rhs not in traits["values"]:
            self.caller.msg(
                "|wCG>|n That is not a valid value for |w%s|n." % key.upper())
            return

        # set the value
        try:
            tar.db.stats[traits.get("category")][key] = int(self.rhs)
        except ValueError:
            tar.db.stats[traits.get("category")][key] = self.rhs

        self.caller.msg("|wCG>|n |c%s's|n  |w%s|n set to|w %s|n." %
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
        output = ANSIString("|wBio|n").center(78, "-")
        bio = []

        for item in BIO:
            traits = get_trait_list(item)

            if traits["check"] and not traits["check"](target.db.stats):
                continue

            # if the bio field passes the check, we add it to the list.
            try:
                bio.append(
                    ANSIString(format(key=item, val=target.db.stats["bio"][item], width=38, just="ljust")))
            except KeyError:
                bio.append(ANSIString(
                    format(item, "", width=38, just="ljust")))

        # Noq peint the bio in two columns.
        count = 0
        for i in range(0, len(bio)):
            if count % 2 == 0:
                output += "\n"
            else:
                output += " "

            count += 1
            output += bio[i]

        self.caller.msg(output)

    def show_attributes(self, target):
        """
        This method shows the attributes of a character.
        """
        self.caller.msg(ANSIString("|wAttributes|n").center(78, "-"))
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
        output = ANSIString("|wPhysical|n").center(
            26) + ANSIString("|wMental|n").center(26) + ANSIString("|wSocial|n").center(26)
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
            output = physical[i]
            output += "  " + mental[i]
            output += "  " + social[i]

            self.caller.msg(output)

    def show_skills(self, target):
        """
        This method shows the skills of a character.
        """
        self.caller.msg(ANSIString("|wSkills|n").center(78, "-"))
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
            output = physical[i]
            output += "  " + mental[i]
            output += "  " + social[i]

            self.caller.msg(output)

    def show_backgrounds(self, target):
        """
        This method shows the backgrounds of a character.
        """
        self.caller.msg(ANSIString("|wBackgrounds|n").center(78, "-"))
        backgrounds = target.db.stats["backgrounds"]
        output = ""
        count = 0
        for key, value in backgrounds.items():
            output += format(key, value)+"  "
            count += 1
            if count == 3:
                self.caller.msg(output)
                output = "\n"
                count = 0
        if count != 0:
            self.caller.msg(output)

        self.caller.msg(output)

    def show_merits(self, target):
        """
        This method shows the merits of a character.
        """
        self.caller.msg(ANSIString("|wMerits|n").center(78, "-"))
        # first we need to build our three lists.

        # get the merits list from the target, put it through the formatter
        # and print it with three columns
        merits = target.db.stats["merits"]
        output = ""
        count = 0
        for key, value in merits.items():
            output += format(key, value)+"  "
            count += 1
            if count == 3:
                self.caller.msg(output)
                output = "\n"
                count = 0
        if count != 0:
            self.caller.msg(output)

    def show_flaws(self, target):
        """
        This method shows the flaws of a character.
        """
        self.caller.msg(ANSIString("|wFlaws|n").center(78, "-"))
        # first we need to build our three lists.

        # get the flaws list from the target, put it through the formatter
        # and print it with three columns
        flaws = target.db.stats["flaws"]
        output = ""
        count = 0
        for key, value in flaws.items():
            output += format(key, value)+"  "
            count += 1
            if count == 3:
                self.caller.msg(output)
                output = "\n"
                count = 0
        if count != 0:
            self.caller.msg(output)

    def show_disciplines(self, target):
        """
        This method shows the disciplines of a character.
        """
        self.caller.msg(ANSIString("|wDisciplines|n").center(78, "-"))
        # first we need to build our three lists.

        # Build the discipline list + specialties 1 column at a time and print it in
        # up to 3 columns
        disciplines = target.db.stats["disciplines"]

        output = ""
        for key, value in disciplines.items():
            output += format(key, value, width=76) + "\n"
            for specialty in target.db.stats["specialties"][key]:
                output += format(specialty, 1,
                                 type="specialty", width=76) + "\n"
        self.caller.msg(output)

    def show_pools(self, target):
        """
        This method shows the pools of a character.
        """
        self.caller.msg(ANSIString("|wPools|n").center(78, "-"))
        # first we need to build our three lists.

        # get the pools list from the target, put it through the formatter
        # and print it with three columns
        pools = target.db.stats["pools"]
        output = ""
        count = 0
        for key, value in pools.items():
            output += format(key, value)+"  "
            count += 1
            if count == 3:
                self.caller.msg(output)
                output = "\n"
                count = 0
        if count != 0:
            self.caller.msg(output)

    def func(self):
        # check to see if caller
        req = target(self)
        tar = req.get("target")

        # check if the target is the caller, or if the caller is admin.
        if self.caller != tar and not self.caller.locks.check_lockstring(self.caller, "perm(Admin)"):
            self.caller.msg("|wCG>|n You can only view your own sheet.")
            return

        # show the sheet
        self.caller.msg(ANSIString(
            "[ Character Sheet for: |c{}|n ]".format(tar.name)).center(78, ANSIString("|w=|n")))
        self.caller.msg(self.show_bio(tar))
        self.caller.msg(self.show_attributes(tar))
        self.caller.msg(self.show_skills(tar))
        self.caller.msg(self.show_backgrounds(tar))
        if tar.db.stats["merits"]:
            self.caller.msg(self.show_merits(tar))
        if tar.db.stats["flaws"]:
            self.caller.msg(self.show_flaws(tar))
        if tar.db.stats["disciplines"]:
            self.caller.msg(self.show_disciplines(tar))

        self.caller.msg(self.show_pools(tar))
        self.caller.msg(ANSIString(ANSIString("|w=|n") * 78))
