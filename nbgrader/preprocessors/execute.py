from nbconvert.preprocessors import ExecutePreprocessor, CellExecutionError
from traitlets import Bool, List, Integer
from textwrap import dedent

from . import NbGraderPreprocessor
from nbconvert.exporters.exporter import ResourcesDict
from nbformat.notebooknode import NotebookNode
from typing import Any, Optional, Tuple


class UnresponsiveKernelError(Exception):
    pass


class Execute(NbGraderPreprocessor, ExecutePreprocessor):

    interrupt_on_timeout = Bool(True)
    allow_errors = Bool(True)
    raise_on_iopub_timeout = Bool(True)
    extra_arguments = List([], help=dedent(
        """
        A list of extra arguments to pass to the kernel. For python kernels,
        this defaults to ``--HistoryManager.hist_file=:memory:``. For other
        kernels this is just an empty list.
        """)
    ).tag(config=True)

    execute_retries = Integer(0, help=dedent(
        """
        The number of times to try re-executing the notebook before throwing
        an error. Generally, this shouldn't need to be set, but might be useful
        for CI environments when tests are flaky.
        """)
    ).tag(config=True)

    def preprocess(self,
                   nb: NotebookNode,
                   resources: ResourcesDict,
                   retries: Optional[Any] = None
                   ) -> Tuple[NotebookNode, ResourcesDict]:
        # This gets added in by the parent execute preprocessor, so if it's already in our
        # extra arguments we need to delete it or traitlets will be unhappy.
        if '--HistoryManager.hist_file=:memory:' in self.extra_arguments:
            self.extra_arguments.remove('--HistoryManager.hist_file=:memory:')

        if retries is None:
            retries = self.execute_retries

        try:
            output = super(Execute, self).preprocess(nb, resources)
        except RuntimeError:
            if retries == 0:
                raise UnresponsiveKernelError()
            else:
                self.log.warning("Failed to execute notebook, trying again...")
                return self.preprocess(nb, resources, retries=retries - 1)

        return output

    def preprocess_cell(self, cell, resources, cell_index, store_history=True):
            """
            Need to override preprocess_cell to check reply for errors
            """
            # Copied from nbconvert ExecutePreprocessor
            if cell.cell_type != 'code' or not cell.source.strip():
                return cell, resources
            
            self._check_assign_resources(resources)
            cell = self.execute_cell(cell, cell_index, store_history)

            # temporal workaround
            if cell.cell_type == "code":
                if cell.execution_count == True:
                    cell.execution_count = 1

            cell_allows_errors = (
                self.allow_errors or "raises-exception" in cell.metadata.get("tags", [])
            )

            if self.force_raise_errors or not cell_allows_errors:
                if cell.outputs.get("output_type") == "error":
                    raise CellExecutionError.from_cell_and_msg(cell, cell.outputs)

            return cell, resources
