from evennia.commands.default.muxcommand import MuxCommand
from world.data import get_trait_list
import random
from evennia.utils.ansi import ANSIString


class dice(MuxCommand):
    """
    This is a super basic dice roller for the early stages of the game.
    It will be expanded upon later.

    Usage:
        +roll <dice pool> 
    """

    key = "roll"
    aliases = ["dice", "+roll", "+dice"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        output = []
        count = 0
        tens = 0
        crits = 0
        if not self.args:
            self.caller.msg("Usage: +roll <dice pool>")
            return

        # Parse the arguments
        args = self.args.split()
        dice_pool = args[0]

        if not dice_pool.isdigit():
            self.caller.msg("Usage: +roll <dice pool>")
            return

        for _ in range(0, int(dice_pool)):
            roll = random.randint(1, 10)
            if roll == 10:
                tens += 1
                count += 1
                output.append("|g%s|n " % roll)
            elif roll >= 6:
                output.append("|g%s|n " % roll)
                count += 1
            elif roll == 1:
                output.append("|r%s|n " % roll)
            else:
                output.append("|y%s |n" % roll)

        if (tens / 2) >= 1:
            crits = int((tens/2) * 2)

        successes = ""
        if (count + crits) > 0:
            successes = "|g" + str(count + crits) + "|n"
        else:
            successes = "|y0|n"

        output.sort(key=lambda x: ANSIString((x)))
        s_list = " ".join(output)

        self.caller.location.msg_contents(
            f"|w+ROLL>%cn |c{self.caller.name}|n rolls |w{dice_pool}|n dice -> {successes} successes ({s_list})")

        # for every pair of 10s rolled, add 2 successes
