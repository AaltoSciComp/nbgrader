from .common import ValidationError, SchemaTooOldError, SchemaTooNewError
from .v3 import MetadataValidatorV3 as MetadataValidator
from .v3 import read_v3 as read, write_v3 as write
from .v3 import reads_v3 as reads, writes_v3 as writes

SCHEMA_VERSION = MetadataValidator.schema_version
# The values should designate an "unimportant" cell, so that they can be used without breaking anything
SCHEMA_REQUIRED = {3: {"schema_version": 3, "grade": False, "locked": False, "solution": False},
                   2: {"schema_version": 2, "grade": False, "locked": False, "solution": False},
                   1: {"schema_version": 1, "grade": False, "locked": False, "solution": False}}
