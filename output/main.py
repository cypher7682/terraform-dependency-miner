import os

from output.formatters import fmt


class outputter:
    def __init__(self, dependency_tree, formatter: fmt.hinter):
        ''' takes a dependency tree, and processes the output'''
        self.dependency_tree = dependency_tree
        self.dupes = []
        self.formatter = formatter

    def put(self, file):
        if not os.path.isfile(os.path.abspath(file)):
            with open(os.path.abspath(file), 'w') as f:
                f.write("[comment]: <> (---MINER-START---)\n")
                f.write("\n")
                f.write("[comment]: <> (---MINER-END---)\n")
                f.write("\n")


        write_back = True
        mem_file = []

        with open(os.path.abspath(file), 'r') as f:
            for line in f:

                if line == "[comment]: <> (---MINER-START---)\n":
                    write_back = False
                    mem_file.append("[comment]: <> (---MINER-START---)\n")
                    mem_file.append(f" \n")

                    for l in self.formatter.start():
                        if l:
                            mem_file.append(f"{l}\n")
                    for l in self.dependency_tree_iterator():
                        if l:
                            mem_file.append(f"{l}\n")
                    for l in self.formatter.finish():
                        if l:
                            mem_file.append(f"{l}\n")

                if write_back:
                    mem_file.append(line)

                elif line == "[comment]: <> (---MINER-END---)\n":
                    mem_file.append(f" \n")
                    mem_file.append("[comment]: <> (---MINER-END---)\n")
                    write_back = True

        with open(file, 'w') as f:
            for line in mem_file:
                if type(line) == str:
                    f.write(line)

    def dependency_tree_iterator(self, layer=0):
        # {this_source: {child_source: {...} } }
        for this_source, child_sources in self.dependency_tree.items():
            yield self.formatter.pre(this_source, layer=layer)

            for thing in outputter(child_sources, formatter=self.formatter).dependency_tree_iterator(layer=layer + 1):
                yield thing

            for child_source in child_sources:
                yield self.formatter.post(this_source, child_source, layer=layer)
