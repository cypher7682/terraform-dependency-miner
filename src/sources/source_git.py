import logging
import os.path
import sys

from sources.source_base import Base
import shutil
import git

class Source(Base):
    # These Re's are fucking disgusting, but actually work REALLY quite well
    matching_re = r'git::'
    source_input_re = r'git::((?P<PROTO>https|ssh)://)(?P<URL>.+?)/(?P<ORG>[a-zA-Z0-9_-]+)/(?P<REPO>[a-zA-Z0-9_-]+(.git)?)(?P<PATH>(/{1,2}([a-zA-Z0-9_-]+)?)*)?(\?ref=(?P<BRANCH>.+?))?'
    source_output_re = r'\g<PROTO>||\g<URL>||\g<ORG>||\g<REPO>||\g<PATH>||\g<BRANCH>'
    type = "Git"

    # These methods MUST be overwritten in the extended class
    def _get_facts_from_source(self, data):
        self.protocol = data[0].strip()
        self.url = data[1].strip()
        self.clone_url = f"{self.url}" if sys.argv[6] == "--" else f"{sys.argv[6]}@{self.url}"
        self.org = data[2].strip()
        self.repo = data[3].strip()
        self.path = data[4].strip() or ''
        self.branch = data[5].strip() or 'origin/master'

        self.repo_root = os.path.abspath(f"/tmp/{self.url}/{self.org}/{self.repo}/{self.branch}")
        self.disk_path = os.path.abspath(f"{self.repo_root}/{self.path}")

    def _sub_init(self):
        self._get_facts_from_source(self.source_string.split('||'))

    def _put_to_disk(self):
        if os.path.isdir(f"{self.repo_root}/.git"):
            r = git.Repo(self.repo_root)
        else:
            try:
                shutil.rmtree(self.repo_root)
                shutil.rmtree(self.repo_root)
            except FileNotFoundError:
                r = git.Repo.clone_from(
                    f"{self.protocol}://{self.clone_url}/{self.org}/{self.repo}",
                    self.repo_root
                )

        if self.path:
            if not os.path.isdir(self.disk_path):
                self.dead = True

        try:
            r.git.reset('--hard', self.branch)
        except git.exc.GitCommandError:
            logging.info(f"No branch '{self.branch}'")
            self.branch = f'{self.branch}(DEAD)'
            self.dead = True



    def rm(self):
        try:
            shutil.rmtree(self.root_path)
            shutil.rmtree(self.root_path)
        except FileNotFoundError:
            pass

    def _version(self):
        raise self.branch

    def _name(self):
        return f"{self.protocol}://{self.url}/{self.org}/{self.repo}/{self.path}?ref={self.branch}"

    def _rm(self):
        try:
            shutil.rmtree(self.disk_path)
            shutil.rmtree(self.disk_path)
        except FileNotFoundError:
            pass
        except AttributeError:
            pass

    def __del__(self):
        pass
        #self._rm()