# `nuspec` Generator

This is module wraps Python code generated via the `generateDS` library.

It provides a simple interface for programmatically constructing and outputting
valid `.nuspec` files to construct nuget or chocolatey packages.

## Building
The definitions can be created by ingesting the `.xsd` definition file directly
from the web. Within the definition itself there are `{0}` characters that
define the namespace schema definition. I've set it to the latest version I
could find in the example. Skipping this step will cause `generateDS` to crash
due to `{0}` not being a valid namespace.

```powershell
((& curl.exe
https://raw.githubusercontent.com/NuGet/NuGet.Client/dev/src/NuGet.Core/NuGet.Packaging/compiler/resources/nuspec.xsd)
-replace "(\{0\})",'http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd')
-join '' | generateDS.exe -o generated\nuspec.py -
```

## Usage

```python
import nuspec


test = nuspec.package(
    metadata=nuspec.metadataType(
        id="test", version="0.0.1", authors="me", description="generated with
python!"
    )
)
with open("./test.nuspec", "w") as f:
    test.export(outfile=f, level=0)

with open("./test.nuspec", 'r') as f:
    print(f.read())
```
