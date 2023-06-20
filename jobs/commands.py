from .models import Job, Bucket
from evennia.commands.default.muxcommand import MuxCommand
from .models import Bucket
from evennia.accounts.models import AccountDB
from evennia.utils.ansi import ANSIString

class CmdBucket(MuxCommand):
    """
    Manage job buckets.

    Usage:
      bucket/create <name>=<description>
      bucket/view <name>
      bucket/delete <name>
      bucket/list
    """

    key = "+bucket"
    locks = "cmd:perm(bucket) or perm(Builder)"
    aliases = ["buckets", "bucket"]
    help_category = "Jobs"

    def func(self):
        if not self.args or not self.switches:
            self.caller.msg(
                "|wJOBS>|n Usage: bucket/<create|view|delete> <name>=<description>")
            return

        if "create" in self.switches:
            try:
                name, description = self.args.split("=")
            except ValueError:
                self.caller.msg("Usage: bucket/create <name>=<description>")
                return
            account = AccountDB.objects.get(id=self.caller.id)
            bucket = Bucket.objects.create(
                name=name.strip().lower(),
                description=description.strip(),
                created_by=account,
            )
            self.caller.msg(f"Created bucket {bucket.id}: {bucket.name}")

        elif "view" in self.switches:
            name = self.args.strip()
            try:
                bucket = Bucket.objects.get(name=name)
                self.caller.msg(
                    f"Bucket {bucket.id}: {bucket.name} - {bucket.description}")
            except Bucket.DoesNotExist:
                self.caller.msg(f"No bucket named {name} exists.")

        elif "delete" in self.switches:
            name = self.args.strip()
            try:
                bucket = Bucket.objects.get(name=name)
                bucket.delete()
                self.caller.msg(f"Deleted bucket {name}.")
            except Bucket.DoesNotExist:
                self.caller.msg(f"No bucket named {name} exists.")

        elif "list" in self.switches:
            buckets = Bucket.objects.all()
            if not buckets:
                self.caller.msg("No buckets exist.")
                return
            for bucket in buckets:
                self.caller.msg(
                    f"Bucket {bucket.id}: {bucket.name} - {bucket.description}")


class CmdJob(MuxCommand):
    """
    Manage jobs

    Usage:
      job <id>
      job/create <bucket>/<title>=<description>
      job/view <id>
      job/update <id>=<new description>
      job/delete <id>
      job/claim <id>
      job/complete <id>
      job/reopen <id>
      job/assign <id>=<account>


    """

    key = "job"
    locks = "cmd:perm(job) or perm(Builder)"
    help_category = "Jobs"

    def func(self):
        if not self.args or not self.switches:
            self.caller.msg(
                "|wJOBS>|n Usage: job/<create|view|update|delete> <arguments>")
            return

        if "create" in self.switches:
            try:
                bucket_title, rest = self.args.split("/")
                title, description = rest.split("=")
                bucket_title = bucket_title.strip()
                title = title.strip()
                description = description.strip()
            except ValueError:
                self.caller.msg(
                    "|wJOBS>|n Usage: job/create <bucket>/<title>=<description>")
                return

            try:
                bucket = Bucket.objects.get(name=bucket_title)
            except Bucket.DoesNotExist:
                self.caller.msg(
                    f"|wJOBS>|n No bucket named {bucket_title} exists.")
                return

            account = AccountDB.objects.get(id=self.caller.id)
            job = Job.objects.create(
                title=title,
                description=description,
                bucket=bucket,
                creator=account,
            )
            self.caller.msg(f"|wJOBS>|n Created job {job.id}: {job.title}")

        elif "view" in self.switches:
            id = self.args.strip()
            try:
                job = Job.objects.get(id=id)

                self.caller.msg(
                    f"Job {job.id}: {job.title} - {job.description} in bucket {job.bucket.name}")

            except Job.DoesNotExist:
                self.caller.msg(f"|wJOBS>|n No job with ID {id} exists.")

        elif "update" in self.switches:
            try:
                id, new_description = self.args.split("=")
                id = id.strip()
                new_description = new_description.strip()
            except ValueError:
                self.caller.msg(
                    "|wJOBS>|n Usage: job/update <id>=<new description>")
                return

            try:
                job = Job.objects.get(id=id)
                job.description = new_description
                job.save()
                self.caller.msg(
                    f"|wJOBS>|n Updated job {job.id}: {job.title} - {job.description}")
            except Job.DoesNotExist:
                self.caller.msg(f"|wJOBS>|n No job with ID {id} exists.")

        elif "delete" in self.switches:
            id = self.args.strip()
            try:
                job = Job.objects.get(id=id)
                job.delete()
                self.caller.msg(f"|wJOBS>|n Deleted job with ID {id}.")
            except Job.DoesNotExist:
                self.caller.msg(f"|wJOBS>|n No job with ID {id} exists.")

        elif "assign" in self.switches:
            try:
                id, assignee_name = self.args.split("=")
                id = id.strip()
                assignee_name = assignee_name.strip()
            except ValueError:
                self.caller.msg(
                    "|wJOBS>|n Usage: job/assign <id>=<assignee>")
                return

            try:
                job = Job.objects.get(id=id)
                assignee = AccountDB.objects.get(username=assignee_name)
                job.assigned_to = assignee
                job.save()
                self.caller.msg(
                    f"|wJOBS>|n Assigned job {job.id}: {job.title} to {assignee.username}")
            except Job.DoesNotExist:
                self.caller.msg(f"|wJOBS>|n No job with ID {id} exists.")
            except AccountDB.DoesNotExist:
                self.caller.msg(
                    f"|wJOBS>|n No player with username {assignee_name} exists.")

        elif "claim" in self.switches:
            id = self.args.strip()
            try:
                job = Job.objects.get(id=id)
                if job.assigned_to:
                    self.caller.msg(
                        f"|wJOBS>|n Job {id} is already claimed by {job.assigned_to.username}.")
                else:
                    job.assigned_to = self.caller
                    job.save()
                    self.caller.msg(
                        f"|wJOBS>|n You have claimed job {job.id}: {job.title}")
            except Job.DoesNotExist:
                self.caller.msg(f"|wJOBS>|n No job with ID {id} exists.")

        elif "complete" in self.switches:
            id = self.args.strip()
            try:
                job = Job.objects.get(id=id)
                if job.status == 'CLOSED':
                    self.caller.msg(
                        f"|wJOBS>|n Job {id} is already completed.")
                else:
                    job.status = 'CLOSED'
                    job.save()
                    self.caller.msg(
                        f"|wJOBS>|n You have completed job {job.id}: {job.title}")
            except Job.DoesNotExist:
                self.caller.msg(f"|wJOBS>|n No job with ID {id} exists.")

        elif "reopen" in self.switches:
            id = self.args.strip()
            try:
                job = Job.objects.get(id=id)
                if job.status != 'CLOSED':
                    self.caller.msg(
                        f"|wJOBS>|n Job {id} is not completed yet.")
                else:
                    job.status = 'OPEN'
                    job.save()
                    self.caller.msg(
                        f"|wJOBS>|n You have reopened job {job.id}: {job.title}")
            except Job.DoesNotExist:
                self.caller.msg(f"|wJOBS>|n No job with ID {id} exists.")

        elif "assign" in self.switches:
            try:
                id, account_name = self.args.split("=")
                id = id.strip()
                account_name = account_name.strip()
            except ValueError:
                self.caller.msg("|wJOBS>|n Usage: job/assign <id>=<account>")
                return

            try:
                job = Job.objects.get(id=id)
                account = AccountDB.objects.get(username=account_name)
                job.assigned_to = account
                job.save()
                self.caller.msg(
                    f"|wJOBS>|n You have assigned job {job.id}: {job.title} to {account.username}")
            except Job.DoesNotExist:
                self.caller.msg(f"|wJOBS>|n No job with ID {id} exists.")
            except AccountDB.DoesNotExist:
                self.caller.msg(
                    f"|wJOBS>|n No account with username {account_name} exists.")
        # if there's no flags, and no args, just list all jobs
        elif not self.switches and not self.args:
            jobs = Job.objects.all()
            output = ANSIString("|wJOBS>|n\n").center(78, ANSIString("|R=|n"))
            output += ANSIString("|CJOB #  Category   Request Title              Started  Handler           Status|n").ljust(78)
            self.caller.msg(output)
