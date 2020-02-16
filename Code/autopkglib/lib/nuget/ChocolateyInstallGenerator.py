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

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


INSTALL_TEMPLATE = r"""
$packageName= '{0}'
$toolsDir   = "$(Split-Path -Parent $MyInvocation.MyCommand.Definition)"
$url        = '{1}}'
$url64      = '{2}'


$packageArgs = @{
  packageName   = $packageName
  fileType      = '{3}'
  url           = $url
  url64bit      = $url64
  silentArgs    = "{4}"
  validExitCodes= {5}
  checksum      = '12345'
  checksumType  = 'sha256'
  checksum64    = '123356'
  checksumType64= 'sha256'
}

Install-ChocolateyPackage @packageArgs
"""

LOCATION_HEADER = 0
LOCATION_IN_SPLAT = 1


@dataclass
class ChocolateyInstallGenerator:
    """
    This will render a chocolateyinstall.ps1 file given some inputs:
    https://chocolatey.org/docs/helpers-install-chocolatey-package

    The generation of the script is intentionally naive and likely
    can only handle the simplest of use cases.
    """

    PackageName: str
    FileType: Optional[str] = None
    SilentArgs: Optional[List[str]] = None
    Url: Optional[str] = None
    Url64bit: Optional[str] = None
    ValidExitCodes: Optional[List[int]] = None
    Checksum: Optional[str] = None
    ChecksumType: Optional[str] = None
    Checksum64: Optional[str] = None
    ChecksumType64: Optional[str] = None
    Options: Optional[Dict[str, Any]] = None
    File: Optional[str] = None
    File64: Optional[str] = None
    UseOnlyPackageSilentArguments: Optional[bool] = None
    UseOriginalLocation: Optional[bool] = None

    def render(self) -> str:
        splat = "$packageArgs = @{\n"
        for k, v in self.__dict__.items():
            if v is None:
                continue
            elif isinstance(v, str):
                value = f"'{v}'"
            elif isinstance(v, List):
                value = f"@({','.join([x.__str__() for x in v])})"
            elif isinstance(v, bool):
                value = f"${v}"
            splat += f"  {k} = {value}\n"
        splat += "}\n\n"
        splat += "Install-ChocolateyPackage @packageArgs\n"

        return splat

    def __str__(self) -> str:
        return self.render()
