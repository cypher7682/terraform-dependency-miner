import os.path
from config import Config
from repo import R
import re

DEPENDENCY_CACHE = {}

class Dependency_Matcher:
    def __init__(self, config, file_path, parent=""):
        self.parent = parent
        self.config = config
        self.file_path = file_path
        self._parse_file_contents_for_dependencies()

        if not 'terragrunt' in self.config:
            self.config['terragrunt'] = False

    def _parse_file_contents_for_dependencies(self):
        self._matches = []
        with open(self.file_path) as file:
            for line in file:
                if self._line_matcher(line.strip()):
                    self._matches.append(line.strip())
        self._format_matches_for_output()

    def _format_matches_for_output(self):
        '''
        The output mutator MUST match all dependencies here.
        Otherwise we're going to fucking explode.
        Output mutation MUST be in the format `url,path,branch`

        IF those aren't set, we'll do out very bestest to try and match a "sensible" git string.
        :return:
        '''
        self.repos = []
        if 'mutator_input_re' in self.config and 'mutator_output_re' in self.config:
            r = self.config['mutator_input_re']
            o = self.config['mutator_output_re']
        else:
            r = r'^.*(git::https://)?(?P<url>github.com(/[a-z0-9-_]+){2}(\.git)?)(?P<path>(/+([a-z0-9-_]+)?)+)?(\?ref=(?P<branch>[a-z[0-9.]*))?\".*'
            o = r'\g<url>,\g<path>,\g<branch>'


        for match in self._matches:
            try:
                assert re.match(r, match)
            except AssertionError:
                print(f"WARNING: '{r}' doesn't match dependency string: '{match}'")
                continue
            url, path, branch = re.sub(r, r'\g<url>,\g<path>,\g<branch>', match).split(',')

            from main import dep_handler # Don't ask
            if f"{url}@{path}@{branch}" not in DEPENDENCY_CACHE:

                if self.config['terragrunt']:
                    title = "/".join(list(filter(len, self.file_path.split('/')))[2:-1])
                    self.parent = title
                else:
                    title = ""

                DEPENDENCY_CACHE[f"{url}@{path}@{branch}"] = dep_handler(R(url,
                                                                           f"ssh://git@{url}",
                                                                           path_suffix=path,
                                                                           branch=branch,
                                                                           title = title),
                                                                         parent=self.parent,
                                                                         )

            if title:
                self.repos.append({title: DEPENDENCY_CACHE[f"{url}@{path}@{branch}"]})
            else:
                self.repos.append(DEPENDENCY_CACHE[f"{url}@{path}@{branch}"])

    def _line_matcher(self, line):
        '''We get into the realm of double negatives here.
        All the matchers for a dep *must* match for this to return true
        Hence, if a matcher returns false, return false too'''

        return False not in [
            self._Strings(line),
            self._Re(line),
        ]

    def _Re(self,txt):
        if "re" in self.config:
            return re.match(self.config["re"], txt)
        return True

    def _Strings(self, txt):
        if "strings" in self.config:
            for s in self.config["strings"]:
                if s not in txt:
                    return False
            return True
        return True

    def has_deps(self):
        pass

class Matcher:
    def __init__(self, config, parent=""):
        self.fm = config['file']
        self.dm = config['deps']
        self.parent = parent

    def matches_file(self, file):
        '''
        File Matchers MUST match all provided matchings
        :param file:
        :return:
        '''
        if False not in [
            self._matches_file_String_ends(file),
            self._matches_file_Re(file),
            self._matches_file_Strings_not(file)
        ] and not os.path.islink(file) :
            return Dependency_Matcher(self.dm, file, parent=self.parent)
        return False

    def _matches_file_String_ends(self, file):
        if "ends" in self.fm:
            return file.endswith(self.fm["ends"])
        return True

    def _matches_file_Re(self, file):
        if 're' in self.fm:
            return re.match(self.fm['re'], file)
        return True

    def _matches_file_Strings_not(self, file):
        if 'strings_not' in self.fm:
            for string in self.fm['strings_not']:
                if string in file:
                    return False
        return True

class Matchers:
    def __init__(self, parent=""):
        self.parent=parent
        self.MATCHERS = [Matcher(m, parent=self.parent) for m in Config.matchers]

    def match(self, file):
        for matcher in self.MATCHERS:
            if dependency_matcher := matcher.matches_file(file):
                return dependency_matcher
        return False