from sources.source_base import Base


class Source(Base):
    matching_re = "\.{1,2}/"
    source_input_re = r'(?P<path>[a-zA-Z0-9/_.-]*)'
    source_output_re = r'\g<path>'
    type = "Local"

    # These methods MUST be overwritten in the extended class
    def _sub_init(self):
        self.disk_path = f"{'/'.join(self.file.split('/')[:-1])}/{self.source_string}"
        self.cacheable = False

    def _put_to_disk(self):
        ''' We don't need to copy shit, cus we're already on the local filesystem
        Instead, we'll just take a relative path from where we found the source, and put the "source" on the end '''
        pass

    def _version(self):
        return "current"

    def _name(self):
        return f"'{self.source_string}'"
