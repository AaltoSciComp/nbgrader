import nbformat
from nbformat.notebooknode import NotebookNode


class DuplicateCellError(Exception):

    def __init__(self, message):
        super(DuplicateCellError, self).__init__(message)


# This doesn't have to be a class right now, but I'm writing it that way in case extensions are needed later
class CheckDuplicateFlag:

    def __init__(self, notebook_filename):
        # Does this have to be the full path
        with open(notebook_filename, encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=nbformat.NO_CONVERT)
        self.postprocess(nb)

    def postprocess(self, nb: NotebookNode):
        for cell in nb.cells:
            self.postprocess_cell(cell)

    @staticmethod
    def postprocess_cell(cell: NotebookNode):
        if "nbgrader_local" in cell.metadata and "duplicate" in cell.metadata.nbgrader_local:
            del cell.metadata.nbgrader_local["duplicate"]  # this should work because it is a dict underneath?
            msg = "Detected cells with same ids"  # TODO
            raise DuplicateCellError(msg)
