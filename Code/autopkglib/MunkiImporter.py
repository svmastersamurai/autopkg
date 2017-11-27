#!/usr/bin/python
#
# Copyright 2013-2017 Greg Neagle
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
"""See docstring for MunkiImporter class"""

import optparse
import os
import sys
from urlparse import urlparse

from autopkglib import Processor, ProcessorError


__all__ = ["MunkiImporter"]


class MunkiImporter(Processor):
    """Imports a pkg or dmg to the Munki repo."""
    input_variables = {
        "MUNKI_REPO": {
            "description": "Munki repo URL.",
            "required": True
        },
        "MUNKI_REPO_PLUGIN": {
            "description": "Munki repo plugin. Defaults to FileRepo.",
            "required": False,
            "default": "FileRepo"
        },
        "MUNKILIB_DIR": {
            "description": ("Directory path that contains munkilib. Defaults "
                            "to /usr/local/munki"),
            "required": False,
            "default": "/usr/local/munki"
        },
        "pkg_path": {
            "required": True,
            "description": "Path to a pkg or dmg to import.",
        },
        "munkiimport_pkgname": {
            "required": False,
            "description": "Corresponds to --pkgname option to munkiimport.",
        },
        "munkiimport_appname": {
            "required": False,
            "description": "Corresponds to --appname option to munkiimport.",
        },
        "repo_subdirectory": {
            "required": False,
            "description": (
                "The subdirectory under pkgs to which the item "
                "will be copied, and under pkgsinfo where the pkginfo will "
                "be created."),
        },
        "pkginfo": {
            "required": False,
            "description": ("Dictionary of pkginfo keys to copy to "
                            "generated pkginfo."),
        },
        "extract_icon": {
            "required": False,
            "description": ("If not empty, attempt to extract and import an "
                            "icon from the installer item.")
        },
        "force_munkiimport": {
            "required": False,
            "description": (
                "If not False or Null, causes the pkg/dmg to be imported even"
                "if there is a matching pkg already in the repo."),
        },
        "additional_makepkginfo_options": {
            "required": False,
            "description": (
                "Array of additional command-line options that will "
                "be inserted when calling 'makepkginfo'.")
        },
        "version_comparison_key": {
            "required": False,
            "description": ("String to set 'version_comparison_key' for "
                            "any generated installs items."),
        },
        "uninstaller_pkg_path": {
            "required": False,
            "description": ("Path to an uninstaller pkg, supported for Adobe "
                            "installer_type items."),
        },
        "MUNKI_PKGINFO_FILE_EXTENSION": {
            "description":
                "Extension for output pkginfo files. Default is 'plist'.",
            "required": False
        },
    }
    output_variables = {
        "pkginfo_repo_path": {
            "description": ("The repo path where the pkginfo was written. "
                            "Empty if item not imported."),
        },
        "pkg_repo_path": {
            "description": ("The repo path where the pkg was written. "
                            "Empty if item not imported."),
        },
        "icon_repo_path": {
            "description": ("The repo path where the icon was written. "
                            "Empty if icon not imported."),
        },
        "munki_info": {
            "description":
                "The pkginfo property list. Empty if item not imported.",
        },
        "munki_repo_changed": {
            "description": "True if item was imported."
        },
        "munki_importer_summary_result": {
            "description": "Description of interesting results."
        },
    }
    description = __doc__

    def main(self):
        sys.path.insert(0, self.env["MUNKILIB_DIR"])
        try:
            from munkilib import munkirepo
            from munkilib.admin import munkiimportlib
            from munkilib.admin import pkginfolib
            from munkilib.cliutils import get_version, pref, path2url
        except ImportError, err:
            raise ProcessorError(
                "munkilib import error: %s\nMunki tools version 3.2.0.3462 or "
                "later is required." % str(err))

        if urlparse(self.env["MUNKI_REPO"]).scheme == '':
            self.env["MUNKI_REPO"] = path2url(self.env["MUNKI_REPO"])

        # clear any pre-exising summary result
        if 'munki_importer_summary_result' in self.env:
            del self.env['munki_importer_summary_result']

        # for backwards-compatibility with previous versions of this
        # processor, we need to accept and parse makepkginfo options

        # Generate arguments for makepkginfo.
        args = ["makepkginfo", self.env["pkg_path"]]
        if self.env.get("munkiimport_pkgname"):
            args.extend(["--pkgname", self.env["munkiimport_pkgname"]])
        if self.env.get("munkiimport_appname"):
            args.extend(["--appname", self.env["munkiimport_appname"]])
        # uninstaller pkg will be copied later, this is just to suppress
        # makepkginfo stderr warning output
        if self.env.get("uninstaller_pkg_path"):
            args.extend(["--uninstallpkg", self.env["uninstaller_pkg_path"]])
        if self.env.get("additional_makepkginfo_options"):
            args.extend(self.env["additional_makepkginfo_options"])

        # parse the options
        parser = optparse.OptionParser()
        pkginfolib.add_option_groups(parser)
        options, arguments = parser.parse_args(args)

        try:
            pkginfo = pkginfolib.makepkginfo(self.env["pkg_path"], options)
        except pkginfolib.PkgInfoGenerationError, err:
            raise ProcessorError(
                "creating pkginfo for %s failed: %s"
                % (self.env["pkg_path"], err))

        # copy any keys from pkginfo in self.env
        if "pkginfo" in self.env:
            for key in self.env["pkginfo"]:
                pkginfo[key] = self.env["pkginfo"][key]

        # set an alternate version_comparison_key
        # if pkginfo has an installs item
        if "installs" in pkginfo and self.env.get("version_comparison_key"):
            for item in pkginfo["installs"]:
                if not self.env["version_comparison_key"] in item:
                    raise ProcessorError(
                        ("version_comparison_key '%s' could not be found in "
                         "the installs item for path '%s'")
                        % (self.env["version_comparison_key"], item["path"]))
                item["version_comparison_key"] = (
                    self.env["version_comparison_key"])

        # connect to repo
        repo = munkirepo.connect(
            self.env['MUNKI_REPO'], self.env['MUNKI_REPO_PLUGIN'])

        # check to see if this item is already in the repo
        matchingitem = munkiimportlib.find_matching_pkginfo(repo, pkginfo)
        if matchingitem and matchingitem['version'] == pkginfo['version']:
            self.env["pkginfo_repo_path"] = ""
            # set env["pkg_repo_path"] to the path of the matching item
            self.env["pkg_repo_path"] = os.path.join(
                self.env["MUNKI_REPO"], "pkgs",
                matchingitem['installer_item_location'])
            self.env["munki_info"] = {}
            if "munki_repo_changed" not in self.env:
                self.env["munki_repo_changed"] = False

            self.output("Item %s already exists in the munki repo as %s."
                        % (os.path.basename(self.env["pkg_path"]),
                           "pkgs/" + matchingitem['installer_item_location']))
            return

        # copy pkg/dmg to repo
        uploaded_pkgpath = munkiimportlib.copy_item_to_repo(
            repo, self.env["pkg_path"], pkginfo.get('version'),
            self.env.get("repo_subdirectory", ""))
        # adjust the installer_item_location to match the actual location
        # and name
        pkginfo["installer_item_location"] = uploaded_pkgpath.partition('/')[2]

        # import uninstaller item if needed
        if self.env.get("uninstaller_pkg_path"):
            uploaded_uninstall_path = munkiimportlib.copy_item_to_repo(
                repo, self.env["uninstaller_pkg_path"],
                pkginfo.get('version'),
                self.env.get("repo_subdirectory", ""))
            pkginfo["uninstaller_item_location"] = (
                uploaded_uninstall_path.partition('/')[2])
            pkginfo["uninstallable"] = True

        # extract and import icon if requested
        self.env["icon_repo_path"] = ""
        if self.env.get("extract_icon"):
            if not munkiimportlib.icon_exists_in_repo(repo, pkginfo):
                imported_icon_path = munkiimportlib.extract_and_copy_icon(
                    repo, self.env["pkg_path"], pkginfo, import_multiple=False)
                if imported_icon_path:
                    self.output("Copied icon to %s" % imported_icon_path)
                    self.env["icon_repo_path"] = imported_icon_path

        # set output variables
        self.env["pkginfo_repo_path"] = munkiimportlib.copy_pkginfo_to_repo(
            repo, pkginfo, subdirectory=self.env.get("repo_subdirectory", ""))
        self.env["pkg_repo_path"] = uploaded_pkgpath
        self.env["munki_info"] = pkginfo
        self.env["munki_repo_changed"] = True
        self.env["munki_importer_summary_result"] = {
            'summary_text': 'The following new items were imported into Munki:',
            'report_fields': ['name', 'version', 'catalogs', 'pkginfo_path',
                              'pkg_repo_path', 'icon_repo_path'],
            'data': {
                'name': pkginfo['name'],
                'version': pkginfo['version'],
                'catalogs': ','. join(pkginfo['catalogs']),
                'pkginfo_path':
                    self.env['pkginfo_repo_path'].partition('pkgsinfo/')[2],
                'pkg_repo_path':
                    self.env['pkg_repo_path'].partition('pkgs/')[2],
                'icon_repo_path':
                    self.env['icon_repo_path'].partition('icons/')[2]
            }
        }

        self.output("Copied pkginfo to %s" % self.env["pkginfo_repo_path"])
        self.output("Copied pkg to %s" % self.env["pkg_repo_path"])

if __name__ == "__main__":
    PROCESSOR = MunkiImporter()
    PROCESSOR.execute_shell()
