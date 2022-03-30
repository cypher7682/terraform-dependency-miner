import logging
import os
import sys

from sources import source_git, sv
from sources.source_base import Base
import requests

TFR_TOKEN = sys.argv[4]

class Source(Base):
    matching_re = "^(tfr://)?(app.terraform.io/|registry.terraform.io/|/)?([a-zA-Z0-9-]*/[a-zA-Z0-9-]*/[a-zA-Z0-9-]*)$"
    source_input_re = r'^(tfr://)?(?P<URL>app.terraform.io/|(registry.terraform.io/|/))?(?P<ORG>[a-zA-Z0-9_-]+)/(?P<MODULE>[a-zA-Z0-9_-]+)/(?P<CLOUD>[a-zA-Z0-9_-]+)(/?version=(?P<VERSION>\d+\.\d+\.\d+))?$'
    source_output_re = r'\g<URL>||\g<ORG>||\g<MODULE>||\g<CLOUD>||\g<VERSION>'
    type = "Registry"

    def _sub_init(self):
        self.headers = {} if sys.argv[4] == "--" else {"Authorization": f"Bearer {TFR_TOKEN}"}
        self.data = self.source_string.split("||")
        self.org = self.data[1]
        self.module = self.data[2]
        self.cloud = self.data[3]

        if not self.data[0] or self.data[0] == '/':
            self.url = "registry.terraform.io/"
        else:
            self.url = self.data[0]

        self.public = self.url != "app.terraform.io/"

        if "version" in self.source_hcl:
            if self.source_hcl['version']:
                self.semver_string = self.source_hcl['version']
        elif self.data[4]:
            self.semver_string = self.data[4]
        else:
            self.semver_string = ">0.0.0"

        # Attempt to get the repo from wherever registry says it is
        self.im_a_real_boy = self._get_module(self._version())

        if self.im_a_real_boy.matches():
            self.disk_path = os.path.abspath(self.im_a_real_boy.disk_path)
            self.dead = self.im_a_real_boy.dead

    def _put_to_disk(self):
        ''' Registry isn't actually a thing. it's just a redirection serice, which is frankly shit '''
        self.im_a_real_boy.write_to_disk()

    def _get_versions(self):
        if self.public:
            url = f"https://{self.url}v1/modules"
        else:
            url = f"https://{self.url}api/registry/v1/modules"
        r = requests.get(url=f"{url}/{self.org}/{self.module}/{self.cloud}/versions",
                         headers=self.headers)

        versions = []
        try:
            for module in r.json()['modules']:
                for version in module['versions']:
                    versions.append(version['version'])
        except KeyError as e:
            logging.error(r.json())
            raise KeyError(e)

        return versions

    def _get_module(self, version):
        if not self.public:
            url = f"https://{self.url}/api/v2/organizations/{self.org}/registry-modules/private/{self.org}/{self.module}/{self.cloud}"
            r = requests.get(url=url, headers=self.headers)
            try:
                source = f"git::{r.json()['data']['attributes']['vcs-repo']['repository-http-url']}?ref=v{version}"
            except KeyError:
                logging.error(r.json())
                exit()
        else:
            url = f'https://{self.url}/v1/modules/{self.org}/{self.module}/{self.cloud}/{version}/download'
            r = requests.get(url=url, headers = self.headers)
            source = r.headers['X-Terraform-Get']
        s = {"source": source}

        sub_source = source_git.Source(s)

        return sub_source

    def _version(self):
        hv = sv._find_highest_version_in_constraints(self._get_versions(), self.semver_string)
        assert hv
        return hv

    def _name(self):
        return f"{self.source_hcl['source']}?ref={self.version()}"
