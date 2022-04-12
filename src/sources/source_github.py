import os.path

import sources.source_git
from sources.source_base import Base
import shutil
import git

class Source(Base):
    # These Re's are fucking disgusting, but actually work REALLY quite well
    matching_re = r'^(git@)?github.com'
    source_input_re = r'(?P<SSH>git@)?github.com/(?P<OTHER_SHIT>.+)$'
    source_output_re = r'\g<SSH>||\g<OTHER_SHIT>'
    type = "Github"

    # These methods MUST be overwritten in the extended class
    def _sub_init(self):
        data = self.source_string.split('||')
        self.proto = "ssh://" if data[0].strip() else "https://"
        self.other_shit = data[1].strip()

        s = {"source": f"git::{self.proto}github.com/{self.other_shit}"}
        s = sources.source_git.Source(s)
        if s.matches():
            self.real_me = s

        self.disk_path = self.real_me.disk_path
        self.dead = self.real_me.dead


    def _put_to_disk(self):
        self.real_me.write_to_disk()

    def _version(self):
        self.real_me.version()

    def _name(self):
        return f"{self.proto}github.com/{self.other_shit}"
