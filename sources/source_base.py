import re
import uuid
import logging
import MinerExceptions

log = logging.getLogger()

class Base:
    matching_re = ""
    source_input_re = ""
    source_output_re = ""
    type = "Base"
    def __init__(self, source, file="", parent_version=""):
        # assert to make sure these are overridden in the extended class
        assert self.matching_re
        assert self.source_input_re
        assert self.source_output_re

        # We only need the "file" stuff for relative imports
        self.cacheable = True
        self.uuid = str(uuid.uuid4())
        self.file = file
        self.dead = False # Is this a dead end?
        self.source_hcl = source # The source dict
        self.disk_path = f'/tmp/{self.uuid}' # Default disk path (often overridden)

        self.source_string = re.sub(self.source_input_re, self.source_output_re, self.source_hcl['source']).strip()

    def matches(self):
        if re.search(self.matching_re, self.source_hcl['source']):
            if not re.match(self.source_input_re, self.source_hcl['source']):
                logging.warning(f"Ignoring broken source... '{self.source_hcl['source']}' did not match '{self.source_input_re}")
                return False

            self._sub_init()
            return True
        logging.debug(f"[{self.type}] Ignoring source. '{self.source_hcl['source']}' does not match '{self.matching_re}'")
        return False

    def write_to_disk(self):
        self._put_to_disk()

    def name(self):
        return self._name()

    def version(self):
        return self._version()

    def _sub_init(self):
        pass

    # These methods MUST be overwritten in the extended class
    def _put_to_disk(self):
        '''This method MUST be overwritten in the extended classes'''
        raise MinerExceptions.BaseClassException("The extended class has not extended the _put_to_disk method, and is therefore broken")

    def _version(self):
        raise MinerExceptions.BaseClassException("The extended class has not extended the _version method, and is therefore broken")

    def _name(self):
        raise MinerExceptions.BaseClassException("The extended class has not extended the _name method, and is therefore broken")

