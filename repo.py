import uuid
import shutil

import git.exc
from git import Repo

class R:
    def __init__(self, name, url, path_suffix="", branch="", title=""):
        self.name = name
        self.url = url
        self.branch = branch or "origin/master"
        self.path_suffix = path_suffix
        self.uuid = str(uuid.uuid4())
        self.path = f'/tmp/{self.uuid}'
        self.root_path = self.path
        self.dead_branch = False
        self.title = title

    def do_clone(self):
        self.repo = Repo.clone_from(
            self.url,
            self.path,
        )
        try:
            self.repo.git.reset('--hard', self.branch)
        except git.exc.GitCommandError as e:
            self.branch += "(DEAD)"
            self.dead_branch = True

        self.path = f'{self.path}/{self.path_suffix}'

    def rm(self):
        try:
            shutil.rmtree(self.root_path)
            shutil.rmtree(self.root_path)
        except FileNotFoundError:
            pass

    def __del__(self):
        self.rm()
