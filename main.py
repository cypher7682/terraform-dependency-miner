from output.main import outputter
from output.formatters import fmt
from sources import factory as source_factory
from dependency_miner import dependency
import os
import sys
import logging

logging.basicConfig(level=logging.WARN)

OUTPUT_FILE = sys.argv[1]
OUTPUT_FORMAT = sys.argv[2]
MERMAID_DIRECTION = sys.argv[3]

if __name__ == "__main__":
    # Create the primary source from where to initiate the smashy
    s = source_factory.getSpecificSource(
        'local',
        {"source": os.path.relpath(os.path.expanduser("~/tf-telco/vonage-api-telco-main-prd/numplan_s3")),
         "version": False},
        "./"
    )
    # TODO: Make this a git repo ^

    # Create the dependency object
    d = dependency(s, recurse=True)

    formatter = {
        "bullets": fmt.bullets(),
        "mermaid": fmt.mermaid(direction=MERMAID_DIRECTION),
    }
    out = outputter(d.get_dependency_tree(), formatter[OUTPUT_FORMAT])
    out.put(file=OUTPUT_FILE)

    # TODO: Commit changes to git repo
    # TODO: Push changes to PR