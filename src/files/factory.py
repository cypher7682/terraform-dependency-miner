from files import file_terraform, file_terragrunt

file_types = sources = {
    "terraform": file_terraform,
    "terragrunt": file_terragrunt,
}


def construct(file):
    for type, o in file_types.items():
        c = o.File(file)
        if c.matches():
            return c
