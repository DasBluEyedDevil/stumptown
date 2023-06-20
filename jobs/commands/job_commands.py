from evennia import Command as MuxCommand
from jobs.models import Job, Bucket, Comment
# get AccoumtDB model
from evennia.accounts.models import AccountDB
from django.utils import timezone


class CmdJobs(MuxCommand):
    """
    Usage:
        +jobs
    """
    key = "+jobs"
    help_category = "Jobs"

    def func(self):
        # Get the account associated with this command.
        account = AccountDB.objects.get(id=self.caller.id)

        # Query the database for jobs.
        jobs = Job.objects.filter(created_by=account, assigned_to=account)
        
        if jobs:
            # Construct a string to display the jobs.
            job_list = "\n".join(
                f"{job.title} - Status: {job.status}" for job in jobs)
            self.caller.msg(f"Your jobs:\n{job_list}")
        else:
            self.caller.msg("You have no jobs.")


class CmdJobsList(MuxCommand):
    """
    Usage:
        +jobs/list <bucket>
    """
    key = "+jobs/list"

    def func(self):
        # Check if the user provided a bucket name.
        if not self.args:
            self.caller.msg("You must provide a bucket name.")
            return

        # Query the database for the bucket.
        try:
            bucket = Bucket.objects.get(name=self.args.strip())
        except Bucket.DoesNotExist:
            self.caller.msg("That bucket does not exist.")
            return

        # Query the database for jobs in the bucket.
        jobs = Job.objects.filter(bucket=bucket)

        if jobs:
            # Construct a string to display the jobs.
            job_list = "\n".join(
                f"{job.title} - Status: {job.status}" for job in jobs)
            self.caller.msg(f"Jobs in bucket '{bucket.name}':\n{job_list}")
        else:
            self.caller.msg(f"There are no jobs in bucket '{bucket.name}'.")


class CmdJobView(MuxCommand):
    """
    Usage:
        +job <#>
    """
    key = "+job"

    def func(self):
        # Check if the user provided a job ID.
        if not self.args:
            self.caller.msg("You must provide a job ID.")
            return

        # Query the database for the job.
        try:
            job = Job.objects.get(id=int(self.args.strip()))
        except (Job.DoesNotExist, ValueError):
            self.caller.msg("That job does not exist.")
            return

        # Construct a string to display the job details.
        job_details = f"""
        Title: {job.title}
        Description: {job.description}
        Status: {job.status}
        Priority: {job.priority}
        Created By: {job.created_by.username if job.created_by else 'N/A'}
        Assigned To: {job.assigned_to.username if job.assigned_to else 'N/A'}
        Bucket: {job.bucket.name}
        """

        self.caller.msg(job_details)


class CmdJobCreate(MuxCommand):
    """
    Usage:
        +job/create <bucket>/<title>=<description>
    """
    key = "+job/create"

    def func(self):
        # Check if the user provided a bucket name, title, and description.
        if not self.args or not self.lhs or not self.rhs:
            self.caller.msg(
                "Usage: +job/create <bucket>/<title>=<description>")
            return

        bucket_name, title = self.lhs.split("/", 1)

        # Query the database for the bucket.
        try:
            bucket = Bucket.objects.get(name=bucket_name)
        except Bucket.DoesNotExist:
            self.caller.msg("That bucket does not exist.")
            return

        # Create the new job.
        job = Job.objects.create(
            title=title,
            description=self.rhs,
            creator=self.caller,
            bucket=bucket
        )

        self.caller.msg(
            f"Job '{job.title}' created successfully in bucket '{bucket.name}'.")


class CmdJobAddComment(MuxCommand):
    """
    Usage:
        +job/add <#>=<comments>
    """
    key = "+job/add"

    def func(self):
        # Check if the user provided a job ID and comments.
        if not self.args or not self.lhs or not self.rhs:
            self.caller.msg("Usage: +job/add <#>=<comments>")
            return

        # Query the database for the job.
        try:
            job = Job.objects.get(id=int(self.lhs))
        except (Job.DoesNotExist, ValueError):
            self.caller.msg("That job does not exist.")
            return

        # Create the new comment.
        Comment.objects.create(
            content=self.rhs,
            author=self.caller,
            job=job
        )

        self.caller.msg("Comment added successfully.")


class CmdJobCheckIn(MuxCommand):
    """
    Usage:
        +job/checkin <#>
    """
    key = "+job/checkin"
    locks = "cmd:all(); arg:all()"

    def func(self):
        # Fetch the job using the job number provided in self.args
        try:
            job = Job.objects.get(id=self.args)
        except Job.DoesNotExist:
            self.caller.msg("Job does not exist.")
            return

        # Check in the job
        job.assigned_to = None
        job.save()
        self.caller.msg(f"You've checked in job #{self.args}.")


class CmdJobCheckOut(MuxCommand):
    """
    Usage:
        +job/checkout <#>
    """
    key = "+job/checkout"
    locks = "cmd:all(); arg:all()"

    def func(self):
        # Fetch the job using the job number provided in self.args
        try:
            job = Job.objects.get(id=self.args)
        except Job.DoesNotExist:
            self.caller.msg("Job does not exist.")
            return

        # Check out the job
        job.assigned_to = self.caller.account
        job.save()
        self.caller.msg(f"You've checked out job #{self.args}.")


class CmdJobComplete(MuxCommand):
    """
    Usage:
        +job/complete <#>=<comment>
    """
    key = "+job/complete"
    locks = "cmd:all(); lhs:all(); rhs:all()"

    def func(self):
        # Fetch the job using the job number provided in self.lhs
        try:
            job = Job.objects.get(id=self.lhs)
        except Job.DoesNotExist:
            self.caller.msg("Job does not exist.")
            return

        # Complete the job
        job.completed = True
        job.resolved_at = timezone.now()
        job.save()

        # Add a completion comment
        comment = Comment.objects.create(
            content=self.rhs,
            job=job,
            author=self.caller.account
        )

        self.caller.msg(f"You've completed job #{self.lhs}.")
