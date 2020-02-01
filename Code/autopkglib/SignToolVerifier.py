#!/usr/local/autopkg/python
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""See docstring for SignToolVerifier class"""

import os.path
import subprocess
import pathlib
from typing import List

from autopkglib import Processor, ProcessorError

__all__ = ["SignToolVerifier"]


class SignToolVerifier(Processor):
    """Verifies an authenticode signed installer using the Microsoft SDK
    signtool executable."""

    EXTENSIONS = [".exe", ".msi"]

    # TODO: How much of this is needed to act as a drop-in replacement in an
    # override recipe??
    input_variables = {
        "DISABLE_CODE_SIGNATURE_VERIFICATION": {
            "required": False,
            "description": ("Prevents this processor from running."),
        },
        "input_path": {
            "required": True,
            "description": (
                "File path to an application bundle (.app) or installer "
                "package (.pkg or .mpkg). Can point to a path inside "
                "a .dmg which will be mounted."
            ),
        },
        "signtool_path": {
            "required": False,
            "description": (
                "The path to signtool.exe. This varies between versions of the "
                "Windows SDK, so you can explicitly set that here in an override."
            ),
        },
        "additional_arguments": {
            "required": False,
            "description": (
                "Array of additional argument strings to pass to codesign."
            ),
        },
    }
    output_variables = {}

    description = __doc__

    def codesign_verify(
        self, path, codesign_additional_arguments=None, signtool_path=None
    ) -> bool:
        """
        Runs 'signtool.exe /pa <path>'. Returns True if signtool exited with 0
        and False otherwise.
        """
        if not codesign_additional_arguments:
            codesign_additional_arguments = []

        signtool_bin = signtool_path if signtool_path else "signtool.exe"
        process = [signtool_bin, "verify", "/pa"]

        # Add additional arguments (if any).
        for argument in codesign_additional_arguments:
            process.append(argument)

        process.append(f"{pathlib.WindowsPath(path)}")

        proc = subprocess.Popen(
            process,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        (output, error) = proc.communicate()

        # Log all output. signtool seems to output only
        # to stderr but check the stdout too
        # TODO: Is this true or not???
        if error:
            [self.output(line) for line in error.splitlines()]

        if output:
            [self.output(line) for line in output.splitlines()]

        # Return True if codesign exited with 0
        return proc.returncode == 0

    def main(self):
        if self.env.get("DISABLE_CODE_SIGNATURE_VERIFICATION"):
            self.output("Code signature verification disabled for this recipe run.")
            return

        input_path = self.env["input_path"]
        signtool_path = self.env["signtool_path"]

        try:
            self.codesign_verify(input_path, signtool_path=signtool_path)
        except Exception as e:
            self.outfile(f"Exception: {e}")
        finally:
            self.output("finished")


if __name__ == "__main__":
    PROCESSOR = SignToolVerifier()
    PROCESSOR.execute_shell()
