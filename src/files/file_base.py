import logging
import os.path
import hcl2
import exceptions

class Base:
    def __init__(self, file):
        assert self.config
        assert self.type

        self.file = os.path.abspath(file)
        self.path = os.path.abspath(file)

    def matches(self):
        ''' File Files MUST match all provided matching '''
        if not os.path.islink(self.file) and \
                os.path.isfile(self.file) and \
                False not in [
                    self._matches_file_String_ends(),
                    self._matches_file_Strings_not()
                ]:
            self._hcl_me()
            return self
        return False


    def _hcl_me(self):
        with open(self.file) as f:
            try:
                self.hcl = hcl2.load(f)
                return True
            except:
                raise exceptions.InvalidHCLException(f"{self.file} broke the HCL parser")


    def _matches_file_String_ends(self):
        try:
            return self.file.endswith(self.config["file"]["ends"])
        except AttributeError:
            return True

    def _matches_file_Strings_not(self):
        try:
            for string in self.config["file"]["strings_not"]:
                if string in self.file:
                    return False
        except AttributeError:
            return True

    def sources(self):
        # perform some validation to make sure our interfaces are returning the correct shit:
        for source in self._sources():
            # TODO: validate that the source looks like a real source
            yield dict(source)


    # These methods MUST be overridden in the extended classes
    def _sources(self):
        raise exceptions.BaseClassException("The extended class has not extended the _name method, and is therefore broken")