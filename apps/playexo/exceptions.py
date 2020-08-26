class ScriptError(Exception):
    pass



class BuildError(ScriptError):
    """Exception raised if there has been an error during the builder"""
    pass



class GradeError(ScriptError):
    """Exception raised if there has been an error during the grader"""
    pass
