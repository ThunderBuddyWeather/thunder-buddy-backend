import os

import pytest

# Check if running in CI environment
IN_CI = os.environ.get('CI') == 'true'

# Create a decorator to skip tests in CI
skip_in_ci = pytest.mark.skipif(
    IN_CI, 
    reason="JWT authentication tests are skipped in CI environment"
) 