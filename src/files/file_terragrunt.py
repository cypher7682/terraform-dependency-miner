from files.file_base import Base


class File(Base):
    config = {
        "file": dict(ends=".hcl", strings_not=["example"])
    }
    type = "terragrunt"

    def _sources(self):
        if 'terraform' in self.hcl:
            for module in self.hcl['terraform']:
                if "source" in module:
                    if "version" not in module:
                        module["version"] = False
                    yield module

