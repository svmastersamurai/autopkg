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
import sys
import os
from textwrap import dedent
from tempfile import TemporaryDirectory
from pathlib import Path

from autopkglib.lib.nuget import NugetPackage, ChocolateyInstallGenerator
from autopkglib.NugetChocoPackager import NugetChocoPackager
from autopkglib import ProcessorError


class TestNupkgGenerator(unittest.TestCase):
    def setUp(self):
        self.maxDiff = 100000

    def test_nuget_package_string_formatter(self):
        expected = dedent(
            """\
<package xmlns:mstns="http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd" xmlns:None="http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd" >
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

    def test_install_generator(self):
        expected = dedent(
            """\
$packageArgs = @{
  PackageName = 'bob'
  FileType = 'msi'
  SilentArgs = '/qn /norestart'
  Url = 'https://somewhere.com/file.msi'
  Url64bit = 'https://somewhere.com/file-x64.msi'
  ValidExitCodes = @(0,3010,1641)
  Checksum = '12345'
  ChecksumType = 'sha256'
  Checksum64 = '123356'
  ChecksumType64 = 'sha256'
}

Install-ChocolateyPackage @packageArgs
"""
        )
        test = ChocolateyInstallGenerator(
            PackageName="bob",
            FileType="msi",
            Url="https://somewhere.com/file.msi",
            Url64bit="https://somewhere.com/file-x64.msi",
            SilentArgs="/qn /norestart",
            ValidExitCodes=[0, 3010, 1641],
            Checksum="12345",
            ChecksumType="sha256",
            Checksum64="123356",
            ChecksumType64="sha256",
        )

        self.assertEquals(expected, f"{test}")

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    @unittest.skipUnless(
        (os.popen("choco.exe --version").close() is None), "requires chocolatey"
    )
    def test_choco_packager_raises_on_error(self):
        t = NugetChocoPackager()
        t.env = {"id": "test", "version": "0.0.1"}
        # This will raise an exception since there isn't a description.
        t.package = NugetPackage(
            id=t.env["id"], version=t.env["version"], authors="python"
        )
        with self.assertRaises(ProcessorError):
            t.main()

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    @unittest.skipUnless(
        (os.popen("choco.exe --version").close() is None), "requires chocolatey"
    )
    def test_choco_packager_packages_successfully(self):
        from zipfile import ZipFile

        with TemporaryDirectory() as output_dir:
            t = NugetChocoPackager()
            t.env = {"id": "test", "version": "0.0.1", "output": f"{output_dir}"}
            t.package = NugetPackage(
                id=t.env["id"],
                version=t.env["version"],
                authors="python",
                description="test",
            )
            t.main()
            with ZipFile(
                Path(output_dir, f"{t.env['id']}.{t.env['version']}.nupkg"), "r"
            ) as z:
                self.assertTrue(
                    all(
                        i in z.namelist()
                        for i in ["tools/chocolateyinstall.ps1", "test.nuspec"]
                    )
                )


if __name__ == "__main__":
    unittest.main()
