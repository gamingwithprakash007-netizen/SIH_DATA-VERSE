"""
DATA VERSE Universal MetaPathFinder.
Resolves backend.* and tests.* modules directly from files on disk,
bypassing 9p cached directory listings.
"""
import sys
import os
import importlib.util
from importlib.abc import MetaPathFinder

class UniversalDataVerseFinder(MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if fullname.startswith("backend.") or fullname.startswith("tests."):
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            parts = fullname.split(".")
            file_candidate = os.path.join(root_dir, *parts) + ".py"
            init_candidate = os.path.join(root_dir, *parts, "__init__.py")
            if os.path.isfile(file_candidate):
                return importlib.util.spec_from_file_location(fullname, file_candidate)
            elif os.path.isfile(init_candidate):
                return importlib.util.spec_from_file_location(
                    fullname,
                    init_candidate,
                    submodule_search_locations=[os.path.join(root_dir, *parts)]
                )
        return None

if not any(isinstance(finder, UniversalDataVerseFinder) for finder in sys.meta_path):
    sys.meta_path.insert(0, UniversalDataVerseFinder())
