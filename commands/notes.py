from evennia.commands.default.muxcommand import MuxCommand
from datetime import datetime
from evennia.utils.ansi import ANSIString


class cmdNotes(MuxCommand):
    """
 READ NOTES
   +notes                      - see all your notes
   +note <note name or number> - see your note
   +note/<category>            - see all your notes in a category

   +note <target>/*            - see all visible notes on someone else
   +note <target>/<note>       - see a note on someone else
   +note/<category> <target>/* - see all notes on someone else in a category

 MAKE NOTES
   +note <name>=<text>            - make a note called <name>
   +note/<category> <name>=<text> - make a note in a specific category

 EDIT NOTES
   +note <note>=<new text>     - change the text on a note, removes approval
   +notemove <note>=<category> - move a note to a new category, keeps approval
   +note/<category> <note>=<new text> - change the text of a note into
                                        a new category, removes approval
   +notestatus <note>=PRIVATE|PUBLIC  - make a note in-/visible to others

 SHOW NOTES
   +noteprove <note>=<target(s)> - show any note to a list of targets
                                 - (names or dbrefs separated by commas)
  """

    key = "+notes"
    aliases = ["+notes", "notes", "+note", "note", "+n", "n"]
    locks = "cmd:all()"
    help_category = "Character Generation"

    def get_target(self, target):
        """
        Gets the target object from the name.
        """
        tar = self.caller.search(target, global_search=True)

        # if no target is found check for me and here.
        if not tar:
            if target.lower() == "me":
                tar = self.caller
            elif target.lower() == "here":
                tar = self.caller.location
            else:
                return None
        else:
            return tar

    def func(self):

        # make sure the caller has a notes attribute.
        if not self.caller.db.notes:
            self.caller.db.notes = {}

        # if there's an = in the name, it's editing a note somehow.
        if self.rhs:
            self.edit_note()
            return
        else:
            # if there's no equala, it's a read command.
            self.read_note()
            return

    def edit_note(self):
        try:
            category = self.switches[0]
        except IndexError:
            category = "general"

        name = self.lhs.lower()
        note = self.rhs

        # if there is no note, then it's clearing the note from the system.
        if not note:
            self.caller.db.notes[category].pop(name)
            self.caller.msg("Note %s cleared." % name)
            return

        if not self.caller.db.notes.get(category):
            self.caller.db.notes[category] = {}

        self.caller.db.notes[category][name] = {
            "text": note,
            "date": datetime.now(),
            "private": False,
            "approved": False,
            "approved_by": None
        }

        self.caller.msg("Note |w%s|n saved." % name)
        return

    def read_note(self):
        try:
            category = self.switches[0]
        except IndexError:
            category = "general"

        name = self.args
        target = self.caller

        # if there's a / in the name, it's a target.
        if "/" in name:
            try:
                target, name = name.split("/")
                target = self.get_target(target)
            except ValueError:
                target = self.caller
                name = name

        # if there's no name, it's a list of notes.
        if not name or name == "*" and target == self.caller:
            self.list_notes(category)
            return
        else:
            # if there's no name, it's a list of notes.
            if not name or name == "*" and target != self.caller:
                self.list_notes_other(category, target)
                return
        # if there's a name, or it's a number it's a specific note.
        # if there's a number, and the target is the caller it's a specific note.
        if name.isdigit() and target == self.caller:
            self.show_note_by_number(category, int(name))
            return
        else:
            # if there's a number, and the target is the caller it's a specific note.
            if name.isdigit() and target != self.caller:

                # builder+ can see notes on other people.
                if self.caller.check_permstring("builders"):
                    self.show_note_by_number_other(category, target, int(name))
                    return
                else:
                    self.caller.msg("You can't read other people's notes.")
                    return

    def list_notes(self, category):
        """
        Lists all the notes in a category.
        """
        if self.switches:
            # if the category doesn't exist, then there are no notes.
            if not self.caller.db.notes.get(category):
                self.caller.msg(
                    "You have no notes in the |w%s|n category." % category.upper())
                return
            self.caller.msg(ANSIString("[ |cNotes|n ]").center(
                78, ANSIString("|w=|n")))
            # if the category exists, list all the notes.
            self.caller.msg("Notes in the %s category:" % category)
            for note in self.caller.db.notes[category]:
                self.caller.msg(note)
            return
        else:

            # if there are no notes, tell the caller.
            if not self.caller.db.notes:
                self.caller.msg("You have no notes.")
                return

            self.caller.msg(ANSIString("[ |cNotes|n ]").center(
                78, ANSIString("|w=|n")))
            # if there are notes, list them.
            for category in self.caller.db.notes:
                self.caller.msg(ANSIString("[ |w{}|n ]".format(
                    category)).center(78, "-"))
                count = 0
                for note in self.caller.db.notes[category]:
                    output = "#|w{}|n  |c{}|n".format(count, note.capitalize())

                    if self.caller.db.notes[category][note]["approved"]:
                        output += " |g *|n"

                    if self.caller.db.notes[category][note]["private"]:
                        output += " |r<P>|n"

                    self.caller.msg(output)
                    text = self.caller.db.notes[category][note]["text"]
                    # If the text is longer than 75 characters, truncate it.
                    # else just display it.
                    if len(text) <= 75:
                        self.caller.msg("    " + text)
                    else:
                        self.caller.msg("    " + text[:70] + "...")

                    count += 1

            self.caller.msg(ANSIString("|w=|n" * 78))
            self.caller.msg(
                "To read a note, type '|w+note[/<category>] <note>|n'.")
            return

    def show_note_by_name(self, category, name):
        """
        Shows a specific note.
        """
        # if the category doesn't exist, then there are no notes.
        if not self.caller.db.notes.get(category):
            self.caller.msg("You have no notes in the %s category." % category)
            return

       # show the note
        try:
            self.caller.msg(self.caller.db.notes[category][name])
        except KeyError:
            self.caller.msg("I can't find that note.")
        return

    def show_note_by_name_other(self, category, target, name):
        """
        Shows a specific note.
        """
        # if the category doesn't exist, then there are no notes.
        if not target.db.notes.get(category):
            if self.caller.check_permstring("builders"):
                self.caller.msg("%s has no notes in the %s category." %
                                (target, category))
            return

        # show the note
        try:
            self.caller.msg(target.db.notes[category][name])
        except KeyError:
            self.caller.msg("I can't find that note.")
        return

    def show_note_by_number(self, category, number):
        """
        Shows a specific note.
        """
        # if the category doesn't exist, then there are no notes.
        if not self.caller.db.notes.get(category):
            self.caller.msg("You have no notes in the %s category." % category)
            return

        # if the number is out of range, tell the caller.
        if number > len(self.caller.db.notes[category]):
            self.caller.msg("There is no note with that number.")
            return

        # show the note by index.  This is a bit of a hack, but it works.
        # Make a list of the note titles, choose one, and vifew from that name.
        try:
            note = list(self.caller.db.notes[category].keys())[number]
            self.show_note_by_name(category, note)
        except IndexError:
            self.caller.msg("I can't find that note.")

        return

    def show_note_by_number_other(self, category, target, number):
        """
        Shows a specific note.
        """
        # if the category doesn't exist, then there are no notes.
        if not target.db.notes.get(category):
            self.caller.msg(
                "They have no notes in the %s category." % category)
            return

        # if the number is out of range, tell the caller.
        if number > len(target.db.notes[category]):
            self.caller.msg("There is no note with that number.")
            return

        # show the note by index.  This is a bit of a hack, but it works.
        # Make a list of the note titles, choose one, and vifew from that name.
        try:
            note = list(target.db.notes[category].keys())[number]
            self.show_note_by_name_other(category, note, target)
        except IndexError:
            self.caller.msg("I can't find that note.")

        return

    def list_notes_other(self, category, target):
        """
        Lists all the notes in a category.
        """

        if not target:
            self.caller.msg("They have no notes.")
            return

        # if there are no notes, tell the caller.
        if not target.db.notes:
            self.caller.msg("They have no notes.")
            return

        self.caller.msg(ANSIString("[ |cNotes for {}|n ]".format(target.get_display_name(self.caller))).center(
            78, ANSIString("|w=|n")))
        # if there are notes, list them.
        for category in target.db.notes:
            self.caller.msg(ANSIString("[ |w{}|n ]".format(
                category)).center(78, "-"))
            count = 0

            for note in target.db.notes[category]:
                output = "#|w{}|n  |c{}|n".format(count, note.capitalize())

                if target.db.notes[category][note]["approved"]:
                    output += " |g *|n"

                if target.db.notes[category][note]["private"]:
                    output += " |r<P>|n"

                self.caller.msg(output)
                text = target.db.notes[category][note]["text"]
                # If the text is longer than 75 characters, truncate it.
                # else just display it.
                if len(text) <= 75:
                    self.caller.msg("    " + text)
                else:
                    self.caller.msg("    " + text[:70] + "...")

                count += 1

        self.caller.msg(ANSIString("|w=|n" * 78))
        self.caller.msg(
            "To read a note, type '|w+note[/<category>] [<name>/]<note>|n'.")
        return
