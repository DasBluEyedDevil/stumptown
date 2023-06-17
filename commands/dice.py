from evennia.commands.default.muxcommand import MuxCommand
from world.data import get_trait_list
import random
from evennia.utils.ansi import ANSIString


class dice(MuxCommand):
    """
    This is the dice roller command. It takes a dice pool and rolls that many dice.

    Usage:
        +roll <dice pool>

    Example:
        +roll str + brawl  + 2
        +roll 5
        +roll 5 + 2
        +roll dex + 2 - 1

        This command also akes the hunger mechanic itto account.

        Aww Also: +stats +sheet
    """

    key = "roll"
    aliases = ["dice", "+roll", "+dice"]
    locks = "cmd:all()"
    help_category = "General"

    def results(self, dice):
        output = []
        res = {}
        count = 0
        tens = 0
        ones = 0
        crits = 0

        for _ in range(0, int(dice)):
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
                ones += 1
            else:
                output.append("|y%s|n " % roll)

        if (tens / 2) >= 1:
            crits = int((tens/2) * 2)

        output.sort(key=lambda x: int(ANSIString((x))))
        s_list = "".join(output)

        res["output"] = output
        res["s_list"] = s_list
        res["count"] = count
        res["crits"] = crits
        res["tens"] = tens
        res["ones"] = ones

        return res

    def func(self):

        try:
            hunger = self.caller.db.stats["pools"]["hunger"]
        except KeyError:
            hunger = 0

        ones = 0
        crits = 0
        if not self.args:
            self.caller.msg("Usage: +roll <dice pool>")
            return

        # Anywhere in the string, when there's a plus sign with a space on each side, replace it with a plus
        # This is to allow for people to type in "+1 +2 +3" or "+1+2+3" and have it work the same way.
        args = self.args.replace(
            "+", " +").replace(" + ", " +").replace("-", " -").replace(" - ", " -").replace("  ", " ").split(" ")
        dice = []
        dice_pool = 0

        for arg in args:

            if arg[0] == "+" or arg[0] == "-":

                if arg[1:].isdigit():
                    if arg[0] == "+":
                        dice_pool += int(arg[1:])
                    else:
                        dice_pool -= int(arg[1:])
                    dice.append(arg)

                # everything after the first character is a trait
                temp_arg = arg[1:]
                res = get_trait_list(temp_arg)
                if res:
                    # Try to add their dice in the trait to the dice pool
                    try:
                        dice_pool += self.caller.db.stats[res.get(
                            'category')][res.get('trait')]
                        # Append the dice list with the actual name of the trait.
                        dice.append(arg[0] + res.get('trait'))
                    except KeyError:
                        # if tehre's no dice behind it, still add the trait to the output.
                        dice.append(arg[0] + res.get('trait'))

                else:
                    pass
            else:

                if arg.isdigit():
                    dice_pool += int(arg)
                    dice.append(arg)
                else:
                    res = get_trait_list(arg)
                    if res:
                        # Try to add their dice in the trait to the dice pool
                        try:
                            dice_pool += int(self.caller.db.stats[res.get(
                                'category')][res.get('trait')])
                            # Append the dice list with the actual name of the trait.
                            dice.append(res.get('trait'))
                        except KeyError:
                            # if tehre's no dice behind it, still add the trait to the output.
                            dice.append(res.get('trait'))
                        except ValueError:
                            pass

        mod_dice_pool = dice_pool - hunger
        if mod_dice_pool <= 0:
            hunger = hunger + mod_dice_pool

        regular_dice = self.results(+ mod_dice_pool)
        hunger_dice = self.results(hunger)

        succs = regular_dice.get("count") + hunger_dice.get("count") + \
            regular_dice.get("crits") + hunger_dice.get("crits")
        if succs == 0 and hunger_dice.get("ones") > 0:
            successes = "|rBestial Failure!|n"

        elif succs == 0 and not hunger_dice.get("ones"):
            successes = "|yFailure!|n"

        elif succs > 0 and hunger_dice.get("ones") > 0:
            successes = "|g" + str(succs) + "|n" + " successes"

        elif regular_dice.get("crits") and hunger_dice.get("crits"):
            successes = "|g" + str(succs) + "|n" + " |rMessy Critical!|n"
        else:
            successes = "|g" + str(succs) + "|n" + " successes"
        dice = " ".join(dice).replace(" +", " + ").replace(" -", " - ")
        if hunger:
            msg = f"|wROLL>|n |c{self.caller.name}|n rolls |w{dice}|n -> {successes} ({regular_dice.get('s_list').strip()}) |w<|n{hunger_dice.get('s_list').strip()}|w>|n"
        else:
            msg = f"|wROLL>|n |c{self.caller.name}|n rolls |w{dice}|n -> {successes} ({regular_dice.get('s_list').strip()})"
        self.caller.location.msg_contents(msg)
