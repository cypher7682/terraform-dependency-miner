class fmt:
    class hinter:
        def pre(self, parent_source, layer):
            pass
        def post(self, parent_source, child_source, layer):
            pass
        def start(self):
            yield
        def finish(self):
            yield

    class bullets:
        def __init__(self):
            pass

        def pre(self, parent_source, layer):
            if layer:
                b = f"{'  ' * layer}* "
                return f"{b}{parent_source.name()}"

        def post(self, parent_source, child_source, layer):
            pass

        def start(self):
            for line in [
                " ## Dependency tree"
            ]:
                yield line

        def finish(self):
            yield

    class mermaid:
        def __init__(self, direction="LR"):
            self.direction = direction

        def start(self):
            for line in [
                '```mermaid',
                f'flowchart {self.direction}'
            ]:
                yield line

        def pre(self, parent_source, layer):
            pass

        def post(self, parent_source, child_source, layer):
            name = parent_source.name() if layer else "This"
            return f"    {parent_source.uuid}[{name}] ---> {child_source.uuid}[{child_source.name()}];"

        def finish(self):
            for line in ['```']:
                yield line