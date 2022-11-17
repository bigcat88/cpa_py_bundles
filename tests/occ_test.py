# from unittest.mock import MagicMock, patch
#
# import os
# import pytest
#
# import cloud_py_api.occ as occ


# @patch("occ.subprocess.run")
# @pytest.mark.parametrize("dev_mode", ("True", "1", "0"))
# def test_occ_call_env_dev_mode(dev_mode):
#     with patch.dict(os.environ, {"DEV_MODE": dev_mode}):
#         occ.occ_call("task_name", "param_1")
