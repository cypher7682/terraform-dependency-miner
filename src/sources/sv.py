import semver
import re


def _is_version_within_constraints(version, constraints: str) -> bool:
    constraints = constraints.replace(" ", "").split(",")

    for constraint in constraints:
        r = re.search(r'(?P<GRAMMAR><|<=|=|==|>=|>|~>|!=)?(?P<MAJOR>\d+)(.(?P<MINOR>\d+)?)?(.(?P<PATCH>\d+)?)?',
                      constraint.strip())

        grammar = r.group("GRAMMAR") or "=="
        if grammar == "=":
            grammar = "=="
        major = r.group("MAJOR")
        minor = r.group("MINOR") or 0
        patch = r.group("PATCH") or 0
        constraint = f"{grammar}{major}.{minor}.{patch}"

        if grammar == "~>":
            lt_major = 99999
            lt_minor = 99999
            lt_patch = 99999
            if r.group("PATCH"):
                lt_major = r.group("MAJOR")
                lt_minor = int(r.group("MINOR")) + 1
                lt_patch = 0
            elif r.group("MINOR"):
                lt_major = int(r.group("MAJOR")) + 1
                lt_minor = 0
                lt_patch = 0

            constraints.append(f">={major}.{minor}.{patch}")
            constraints.append(f"<{lt_major}.{lt_minor}.{lt_patch}")
            continue


        if not semver.match(version, constraint):
            return False
    return True

def _find_highest_version_in_constraints(versions: [], constraints: str) -> str:
    highest_version = "0.0.0"
    for version in versions:
        if _is_version_within_constraints(version, constraints):
            highest_version = semver.max_ver(highest_version, version)

    if highest_version == "0.0.0":
        return ""
    return highest_version