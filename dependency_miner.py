import MinerExceptions
from files import factory as file_factory
from sources import factory as source_factory
import os
import logging

DEP_CACHE = {}
INSPECTED = 0

class dependency:
    def __init__(self, source, recurse=False, cache=True):
        self.source = source
        self.cache = cache
        self.source.write_to_disk()

        self.name = source.name()
        self.recurse=recurse

        logging.info(f"Inspecting source: {self.source.disk_path} || {self.name}")

    def _find_matching_files(self):
        ''' Looks for files matching the configured patterns
        Yields each one that matches '''
        if self.recurse:
            for root, dirs, files in os.walk(self.source.disk_path):
                for file in files:
                    file = f"{root}/{file}"
                    try:
                        if f := file_factory.construct(file):
                            yield f
                    except MinerExceptions.InvalidHCLException as e:
                        logging.error(str(e))
                        continue
        else:
            for file in os.listdir(self.source.disk_path):
                try:
                    if f := file_factory.construct(f"{self.source.disk_path}/{file}"):
                        yield f
                except MinerExceptions.InvalidHCLException as e:
                    logging.error(str(e))
                    continue

    def _extract_child_sources(self):
        ''' Looks for kkk strings inside the files found by _find_matching_files
        Each kkk is then fetched to disk on a unique UUID, and instantiates another dependency
        :returns dependency '''
        if not self.source.dead:
            for f in self._find_matching_files():
                for s in source_factory.get(f):
                    yield s

    def get_dependency_tree(self) -> dict:
        child_sources = {}

        for s in self._extract_child_sources():
            d = dependency(s, cache=self.cache)

            if not d.source.cacheable or not self.cache:
                # Return the dep instantly, cus it's not cacheable
                logging.info(f"Not caching {d.name}, as it's not cacheable")
                child_sources.update(d.get_dependency_tree())

            elif d.name in DEP_CACHE:
                logging.info(f"Returning {d.name} from cache")
                child_sources.update(DEP_CACHE[d.name])

            else:
                # if it's cacheable, do so
                logging.info(f"Caching dependency: {d.name}")
                DEP_CACHE[d.name] = d.get_dependency_tree()
                child_sources.update(DEP_CACHE[d.name])

        return {self.source: child_sources}
