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
"""See docstring for NugetChocoPackager class"""

import subprocess
from pathlib import Path
from os import mkdir


from .NugetPackager import NugetPackager
from autopkglib import Processor, ProcessorError
from autopkglib.lib.nuget import NugetPackageGenerator

__all__ = ["NugetChocoPackager"]


class NugetChocoPackager(NugetPackager):
    """
    This generator will shell out to `choco.exe` to package a nuspec into
    a nupkg.
    """

    executable_name = "choco.exe"

    def pack(self):
        cmd = [self.executable_path(), "pack"]
        if self.env.get("nuspecPath") is not None:
            cmd.append(self.env["nuspecPath"])

        if self.env.get("output") is not None:
            cmd.append("--outputdirectory")
            cmd.append(self.env["output"])
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False,
                cwd=self.working_dir,
            )
            (stdout, stderr) = proc.communicate()
        except OSError as err:
            raise ProcessorError(
                f"choco.exe execution failed with error code {err.errno}: "
                f"{err.strerror}"
            )

        if proc.returncode != 0:
            raise ProcessorError(
                f"creating nupkg for {self.env['id']} {self.env['version']} failed: {stderr}"
            )

    def main(self):
        if not self.working_dir:
            with self._create_tmpdir() as td:
                self.working_dir = td.name
                tools_dir = Path(td.name, "tools")
                install_ps1 = Path(tools_dir, "chocolateyinstall.ps1")
                spec_file = Path(
                    td.name, f"{self.package.xml_package.metadata.id}.nuspec"
                )

                if not tools_dir.exists():
                    mkdir(tools_dir)

                if not install_ps1.exists():
                    with install_ps1.open(mode="w") as f:
                        f.write("generate the ps1 here")

                if not spec_file.exists():
                    with spec_file.open(mode="w") as f:
                        f.write(self.generate())
                self.pack()


if __name__ == "__main__":
    PROCESSOR = NugetChocoPackager()
    PROCESSOR.execute_shell()
