from files.file_base import Base
from pprint import pprint


class File(Base):
    config = {
        "file": dict(ends=".tf", strings_not=["example"])
    }
    type = "terraform"

    def _sources(self):
        if 'module' in self.hcl:
            for modules in self.hcl['module']:
                for name, module in modules.items():
                    if "version" not in module:
                        module["version"] = False

                    yield {"source": module["source"], "version": module["version"]}

