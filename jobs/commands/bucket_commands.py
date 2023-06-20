from evennia import Command as MuxCommand
# import the Player model
from evennia import DefaultCharacter as Player
from evennia.utils.ansi import ANSIString


from jobs.models import Bucket, Job
from django.db.models import Count


class CmdBuckets(MuxCommand):
    """
    Usage:
        +buckets

    Display a list of all buckets.
    """
    help_category = "Jobs"
    key = "+buckets"
    locks = "cmd:perm(Builder) or perm(Admin)"

    def func(self):
        # Retrieve all buckets and count the related jobs
        buckets = Bucket.objects.annotate(jobs_count=Count('jobs')).all()

        if not buckets:
            self.caller.msg("|wJOBS>|n No buckets found.")
            return
        
        # Display the buckets
        output = ANSIString(" Buckets ").center(78, ANSIString("|R=|n")) + "\n"
        output += ANSIString(" |CID#   Bucket             Description                                     Jobs|n") + "\n"
        output += ANSIString("|R-|n" * 78) + "\n"
        
        for bucket in buckets:
            output += ANSIString(f" {bucket.id:<4}  {bucket.name:<18} {bucket.description:<45}   {bucket.jobs_count:>4}") + "\n"
        output += ANSIString("|R-|n" * 78) + "\n"
        output += ANSIString(f"Type +bucket/info <bucket> For specific bucket.") + "\n"
        output += ANSIString("|R=|n" * 78) + "\n"

        self.caller.msg(output)
        return
    
class CmdBucketInfo(MuxCommand):
    """
    Usage:
        +bucket/info <bucket>

    Display information about a bucket.
    """
    key = "+bucket/info"
    help_category = "Jobs"
    
    # Only accessible by Builders or Admins
    locks = "cmd:perm(Builder) or perm(Admin)"

    def func(self):
        if not self.args:
            self.caller.msg("You must provide the name of a bucket.")
            return

        try:
            # Retrieve the bucket
            bucket = Bucket.objects.get(name__iexact=self.args.strip())

        except Bucket.DoesNotExist:
            self.caller.msg(f"No bucket found with the name {self.args}.")
            return

        # Retrieve jobs related to the bucket
        jobs = Job.objects.filter(bucket=bucket)

        # Display bucket details
        self.caller.msg(f"Name: {bucket.name}")
        self.caller.msg(f"Description: {bucket.description}")
        self.caller.msg(f"Created at: {bucket.created_at}")
        self.caller.msg(f"Updated at: {bucket.updated_at}")
        self.caller.msg(f"Jobs Count: {jobs.count()}")

        # Display jobs in the bucket
        if jobs:
            self.caller.msg("Jobs:")
            for job in jobs:
                self.caller.msg(f"  {job.title} ({job.status})")


class CmdBucketMonitor(MuxCommand):
    """
    Usage:
        +bucket/monitor <bucket>
    """
    key = "+bucket/monitor"
    help_category = "Jobs"
    locks = "cmd:perm(Builder) or perm(Admin)"

    def func(self):
        if not self.args:
            self.caller.msg("|wJOBS>|n You must provide the name of a bucket.")
            return

        try:
            # Retrieve the bucket
            bucket = Bucket.objects.get(name__iexact=self.args.strip())
        except Bucket.DoesNotExist:
            self.caller.msg(f"|wJOBS>|n No bucket found with the name {self.args}.")
            return

        # Retrieve the list of monitoring buckets, if it exists
        monitoring_buckets = self.caller.db.monitoring_buckets if self.caller.db.monitoring_buckets else []

        # Check if the user is already monitoring this bucket
        if bucket:
            if bucket.name in monitoring_buckets:
                # If they are, stop monitoring it
                monitoring_buckets.remove(bucket.name)
                self.caller.msg(
                    f"You are no longer monitoring the bucket: {bucket.name}")
            else:
                # If they aren't, start monitoring it
                monitoring_buckets.append(bucket.name)
                self.caller.msg(
                    f"You are now monitoring the bucket: {bucket.name}")

            # Save the updated list back to the database
            self.caller.db.monitoring_buckets = monitoring_buckets

        self.caller.msg(f"Monitoring buckets: {monitoring_buckets}")

class CmdBucketCreate(MuxCommand):
    """
    Usage:
        +bucket/create <bucket>=<description>
    """
    key = "+bucket/create"
    help_category = "Jobs"
    locks = "cmd:perm(Builder) or perm(Admin)"

    def func(self):

        if not self.args:
            self.caller.msg(
                "|wJOBS>|n You must provide the name and description of the bucket.")
            return

        try:
            bucket_name, description = [arg.strip()
                                        for arg in self.args.split("=", 1)]
        except ValueError:
            self.caller.msg(
                "|wJOBS>|n You must provide the name and description of the bucket in the format: <bucket>=<description>")
            return

        # Check if a bucket with the same name already exists
        if Bucket.objects.filter(name__iexact=bucket_name).exists():
            self.caller.msg(
                f"|wJOBS>|n A bucket with the name {bucket_name} already exists.")
            return

        # Create the new bucket
        new_bucket = Bucket.objects.create(
            name=bucket_name, description=description)

        self.caller.msg(
            f"|wJOBS>|n Bucket {new_bucket.name} created with description: {new_bucket.description}")


class CmdBucketDelete(MuxCommand):
    """
    Usage:
        +bucket/delete <bucket>
    """
    key = "+bucket/delete"
    help_category = "Jobs"
    # Assuming only Builders or Admins can delete buckets
    locks = "cmd:perm(Builder) or perm(Admin)"

    def func(self):
        if not self.args:
            self.caller.msg(
                "|wJOBS>|n You must provide the name of the bucket you want to delete.")
            return

        bucket_name = self.args.strip()

        # Check if a bucket with the same name exists
        try:
            bucket = Bucket.objects.get(name__iexact=bucket_name)
        except Bucket.DoesNotExist:
            self.caller.msg(f"|wJOBS>|n No bucket found with the name {bucket_name}.")
            return

        # Delete the bucket
        bucket_name = bucket.name  # Store the name for the message after deletion
        bucket.delete()

        self.caller.msg(f"|wJOBS>|n Bucket {bucket_name} deleted.")


class CmdBucketAccess(MuxCommand):
    """
    Usage:
        +bucket/access <player>=<bucket>
    """
    key = "+bucket/access"
    help_category = "Jobs"
    # Assuming only Builders or Admins can manage bucket access
    locks = "cmd:perm(Builder) or perm(Admin)"

    def func(self):
        if not self.args or not self.rhs:
            self.caller.msg(
                "|wJOBS>|n You must provide the name of the player and the bucket.")
            return

        player_name = self.args.strip()
        bucket_name = self.rhs.strip()

        # Check if a player with the given name exists
        try:
            player = Player.objects.get(username__iexact=player_name)
        except Player.DoesNotExist:
            self.caller.msg(f"No player found with the name {player_name}.")
            return

        # Check if a bucket with the given name exists
        try:
            bucket = Bucket.objects.get(name__iexact=bucket_name)
        except Bucket.DoesNotExist:
            self.caller.msg(f"No bucket found with the name {bucket_name}.")
            return

        # Toggle the player's access to the bucket
        if bucket_name in player.db.accessible_buckets:
            player.db.accessible_buckets.remove(bucket_name)
            self.caller.msg(
                f"|wJOBS>|n {player_name} no longer has access to the bucket {bucket_name}.")
        else:
            player.db.accessible_buckets.append(bucket_name)
            self.caller.msg(
                f"|wJOBS>|n {player_name} now has access to the bucket {bucket_name}.")

        # Save the updated accessible_buckets list back to the database
        player.db.accessible_buckets = player.db.accessible_buckets
