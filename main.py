import os
from config import Config
from matchers import Matchers
from repo import R
from pprint import pprint

class dep_handler():
    def __init__(self, repo: R, parent=""):
        # Set empty deps, because it errors all over the place if it doesn't exist.
        self.dependencies = []

        # we'll clone to a UUID just so that we know we aren't conflicting with another repo with the same name
        self.repo = repo
        self.repo.do_clone()

        if parent:
            self.tree = f"{parent} => {self.repo.name}@{self.repo.branch}"
        else:
            self.tree = f"{self.repo.name}@{self.repo.branch}"
        print(self.tree)

        # Populate a list of dependencies
        # We do this here so that we can remove the current repo before we recurse.
        # Otherwise disk space go BYEBYE!!!
        if not self.repo.dead_branch:
            self._find_dependencies()

    def _find_dependencies(self):
        matchers = Matchers(parent=self.tree)
        for dir_path, dirs, files in os.walk(self.repo.path):
            for file in files:
                if dependencies := matchers.match(f"{dir_path}/{file}"):
                    self.dependencies = self.dependencies + dependencies.repos

        self.repo.rm()

    def get_dep_tree(self):
        dep_tree = {}
        if self.repo.title:
        dep_tree[self.repo.title or f"{self.repo.name}@{self.repo.branch}"] = []
        for dep in self.dependencies:
            dep_tree[f"{self.repo.name}@{self.repo.branch}"].append(dep.get_dep_tree())
        return dep_tree


    # TODO: Return the recursed tree

    def __del__(self):
        '''Safeguard - this tidies up any missing repos that we didn't tidy'''
        self.repo.rm()




if __name__ == "__main__":
    for r in Config.terragrunt_repos:
        d = dep_handler(R(r, f"git@github.com:{r}.git"))
        d.get_dep_tree()