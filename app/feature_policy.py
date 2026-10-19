"""Release scope: classroom/assistant work stays available to developers.

Packaged releases show the completed presentation/voice workflow by default.
This is a product scope switch, not an access-control or data deletion boundary.
"""

import os
import sys


def experimental_teaching_enabled(*, frozen=None):
    override = os.environ.get('BILICLASS_EXPERIMENTAL_TEACHING')
    if override is not None:
        return override.strip() == '1'
    return not (getattr(sys, 'frozen', False) if frozen is None else frozen)
