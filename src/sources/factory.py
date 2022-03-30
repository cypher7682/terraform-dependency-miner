import logging
from sources import source_local, source_git, source_registry, source_github
from files import file_base

sources = {
    "github": source_github, #github needs to be first, because otherwise it matches registry
    "git": source_git,
    "local": source_local,
    "registry": source_registry,
}

def getSpecificSource(type, source, path):
    ''' constructs a specific source. '''
    _c = sources[type]
    s = _c.Source(source=source, file=path)
    assert s.matches()
    return s

def get(file: file_base.Base):
    for source_name, source_type in sources.items():
        for source in file.sources():
            try:
                s = source_type.Source(source, file.path)
                if s.matches():
                    s.type = source_type
                    yield s
            except KeyError as e:
                logging.error(source)
                raise KeyError(e)