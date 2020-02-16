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
"""See docstring for NugetPackager class"""

import subprocess

from typing import Optional

from autopkglib import Processor, ProcessorError
from autopkglib.lib.nuget import NugetPackageGenerator

__all__ = ["NugetPackager"]


class NugetPackager(Processor, NugetPackageGenerator):
    """
    This is an abstract class that will wrap all the inputs and output
    variables that can be supplied to generate a nuget package.
    """

    executable_name: str
    working_dir: Optional[str] = None

    description = __doc__
    input_variables = {
        "nuspecPath": {
            "required": False,
            "description": (
                "The path to the nuspec file to build. "
                "If not defined this assumes the working directory."
            ),
        },
        "exePath": {
            "required": False,
            "description": ("The absolute path to the packager executable."),
        },
        "installerPath": {
            "required": True,
            "description": (
                "The path to the installation file. "
                "This should either be an MSI or an EXE that can "
                "perform the application's setup."
            ),
        },
        ### Metadata Overrides
        "id": {"required": True, "description": "The unique ID of the package.",},
        "version": {
            "required": True,
            "description": (
                "The version of the package. "
                "Please see the technical reference for more details on "
                "acceptable versions: "
                "https://docs.microsoft.com/en-us/nuget/concepts/package-versioning"
            ),
        },
        "title": {
            "required": True,
            "description": (
                "This is user-friendly data that shows what is being installed."
            ),
        },
        "authors": {
            "required": False,
            "description": (
                "The authors of the package or software."
                "NOTE: Not supplying either an author or an owner will raise "
                "an exception!"
            ),
        },
        "owners": {
            "required": False,
            "description": (
                "The owners of the package or software."
                "NOTE: Not supplying either an author or an owner will raise "
                "an exception!"
            ),
        },
        "licenseUrl": {
            "required": False,
            "description": ("A URL to the license of the software being packaged."),
        },
        "projectUrl": {
            "required": False,
            "description": ("A URL to the project of the software being packaged."),
        },
        "iconUrl": {
            "required": False,
            "description": (
                "A URL to the favicon of the software being packaged. "
                "This is what gets displayed in GUIs if they render available "
                "packages."
            ),
        },
        "description": {
            "required": False,
            "description": (
                "A long form description of what the package does, what it "
                "installs, changelogs, etc."
            ),
        },
        "summary": {
            "required": False,
            "description": ("A short description of what the package does."),
        },
        "releaseNotes": {
            "required": False,
            "description": ("Notes on this particular release of the package."),
        },
        "copyright": {"required": False, "description": ("Copyright information."),},
        "tags": {
            "required": False,
            "description": ("Tagging information to aide searches."),
        },
        "icon": {
            "required": False,
            "description": (
                "Not sure, but probably something to do with the icon of the "
                "package."
            ),
        },
        "license": {"required": False, "description": ("Licensing information."),},
        "dependencies": {
            "required": False,
            "description": ("Lists dependencies for this package. "),
        },
        "contentFiles": {
            "required": False,
            "description": ("Lists the file contents for this package. "),
        },
    }
    output_variables = {
        "output": {"description": "Path to where the built package should be output."},
    }

    def installer_checksum(self) -> str:
        pass

    def executable_path(self) -> str:
        """
        Resolves to either a user supplied path or the executable name of
        the packager application.
        """
        if self.executable_name is None:
            raise ValueError("the executable name must be set by subclasses")

        return (
            self.env["exePath"]
            if self.env.get("exePath") is not None
            else self.executable_name
        )
