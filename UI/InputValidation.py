def validate_nrun(nrun_str):
    try:
        nrun = int(nrun_str)
        return nrun > 0
    except ValueError:
        return False


def validate_required_strings(strs):
    return all(s.strip() for s in strs)
