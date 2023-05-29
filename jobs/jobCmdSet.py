from evennia import CmdSet
from .commands.bucket_commands import CmdBuckets, CmdBucketInfo, CmdBucketHelp, CmdBucketCreate, CmdBucketDelete, CmdBucketMonitor
from .commands.job_commands import CmdJobs, CmdJobsList, CmdJobView, CmdJobCreate, CmdJobAddComment


class JobCmdSet(CmdSet):
    """
    This command set includes the commands for managing jobs and buckets.

    """
    key = "job_cmdset"

    def at_cmdset_creation(self):
        self.add(CmdBuckets())
        self.add(CmdBucketInfo())
        self.add(CmdBucketHelp())
        self.add(CmdBucketCreate())
        self.add(CmdBucketDelete())
        self.add(CmdBucketMonitor())
        self.add(CmdJobs())
        self.add(CmdJobsList())
        self.add(CmdJobView())
        self.add(CmdJobCreate())
        self.add(CmdJobAddComment())
