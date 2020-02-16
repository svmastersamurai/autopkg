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

from .generated.nuspec import package, metadataType
from io import StringIO


class NugetPackage(package):
    """NugetPackage is a thin wrapper around the generated `package` class."""

    xml_package: package

    def __init__(
        self,
        id=None,
        version=None,
        title=None,
        authors=None,
        owners=None,
        licenseUrl=None,
        projectUrl=None,
        iconUrl=None,
        description=None,
        summary=None,
        releaseNotes=None,
        copyright=None,
        tags=None,
        icon=None,
        license=None,
        dependencies=None,
        contentFiles=None,
    ):
        if id is None:
            raise ValueError("you must supply a package id")
        if version is None:
            raise ValueError("you must supply a package version")

        if authors is None and owners is None:
            raise ValueError("you must supply either an owner or an author")

        self.xml_package = package(
            metadata=metadataType(
                id=id,
                version=version,
                title=title,
                authors=authors,
                owners=owners,
                licenseUrl=licenseUrl,
                projectUrl=projectUrl,
                iconUrl=iconUrl,
                description=description,
                summary=summary,
                releaseNotes=releaseNotes,
                copyright=copyright,
                tags=tags,
                icon=icon,
                license=license,
                dependencies=dependencies,
                contentFiles=contentFiles,
            )
        )

    def __str__(self) -> str:
        """
        generateDS wants a file, so use BytesIO to mimic a file to return a
        string.
        """
        buffer = StringIO("")
        self.xml_package.export(buffer, level=0)
        output = buffer.getvalue()
        buffer.close()

        return output
