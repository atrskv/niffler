import pytest


class pages:
    spending = pytest.mark.usefixtures("spending_page")
