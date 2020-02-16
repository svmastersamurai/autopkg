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

from abc import ABC

from .nupkg import NugetPackage

class NoPackageProvidedException(Exception):
    pass


class NugetPackageGenerator(ABC):
    """A base class which must implement the `pack` method."""
    package: NugetPackage

    def __init__(self, package):
        if not package:
            raise NoPackageProvidedException

        self.package = package

    def generate(self) -> str:
        return f"{self.package}"

    def pack(self) -> bool:
        """Creates the actual nuget package from a given nuspec."""
        pass
