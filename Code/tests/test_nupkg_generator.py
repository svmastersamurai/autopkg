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

import unittest
from textwrap import dedent

from autopkglib.lib.nuget import NugetPackage


class TestNupkgGenerator(unittest.TestCase):
    def test_nuget_package_string_formatter(self):
        expected = dedent(
            """<package xmlns:mstns="http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd" xmlns:None="http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd" >
    <metadata>
        <id>test</id>
        <version>0.0.1</version>
        <authors>python</authors>
    </metadata>
</package>
        """
        )
        pkg = NugetPackage(id="test", version="0.0.1", authors="python")
        xml = f"{pkg}"
        self.assertTrue(len(xml) > 0)
        self.assertEquals(expected, xml)

    def test_nuget_package_required_fields(self):
        # Must supply a version.
        with self.assertRaises(ValueError):
            NugetPackage(id="test", authors="python")

        # Must supply an id.
        with self.assertRaises(ValueError):
            NugetPackage(version="0.0.1", authors="python")

        # Must supply either an owner or an author.
        with self.assertRaises(ValueError):
            NugetPackage(id="test", version="0.0.1")

        # Both are fine too.
        NugetPackage(id="test", version="0.0.1", authors="python", owners="community")


if __name__ == "__main__":
    unittest.main()
