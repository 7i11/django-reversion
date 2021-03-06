from __future__ import unicode_literals
import warnings
from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.utils.encoding import force_text
from reversion.admin import VersionAdmin


def patch_admin(model, admin_site=None):
    """
    Enables version control with full admin integration for a model that has
    already been registered with the django admin site.

    This is excellent for adding version control to existing Django contrib
    applications.
    """
    warnings.warn((
        "Use reversion.admin.VersionAdmin as a mixin for 3rd party apps. "
        "patch_admin will be removed in django-reversion 1.12.0."
    ), DeprecationWarning)
    admin_site = admin_site or admin.site
    try:
        ModelAdmin = admin_site._registry[model].__class__
    except KeyError:
        raise NotRegistered("The model {model} has not been registered with the admin site.".format(
            model=model,
        ))
    # Unregister existing admin class.
    admin_site.unregister(model)
    # Register patched admin class.
    PatchedModelAdmin = type("Version{name}".format(name=ModelAdmin.__name__), (VersionAdmin, ModelAdmin), {})
    admin_site.register(model, PatchedModelAdmin)


# Patch generation methods, only available if the google-diff-match-patch
# library is installed.
#
# http://code.google.com/p/google-diff-match-patch/

try:
    from diff_match_patch import diff_match_patch
except ImportError:  # pragma: no cover
    pass
else:
    dmp = diff_match_patch()

    def generate_diffs(old_version, new_version, field_name, cleanup):
        """Generates a diff array for the named field between the two versions."""
        warnings.warn("generate_diffs will be removed in django-reversion 1.12.0", DeprecationWarning)
        # Extract the text from the versions.
        old_text = old_version.field_dict[field_name] or ""
        new_text = new_version.field_dict[field_name] or ""
        # Generate the patch.
        diffs = dmp.diff_main(force_text(old_text), force_text(new_text))
        if cleanup == "semantic":
            dmp.diff_cleanupSemantic(diffs)
        elif cleanup == "efficiency":
            dmp.diff_cleanupEfficiency(diffs)
        elif cleanup is None:
            pass
        else:
            raise ValueError("cleanup parameter should be one of 'semantic', 'efficiency' or None.")
        return diffs

    def generate_patch(old_version, new_version, field_name, cleanup=None):
        """
        Generates a text patch of the named field between the two versions.

        The cleanup parameter can be None, "semantic" or "efficiency" to clean up the diff
        for greater human readibility.
        """
        warnings.warn("generate_patch will be removed in django-reversion 1.12.0", DeprecationWarning)
        diffs = generate_diffs(old_version, new_version, field_name, cleanup)
        patch = dmp.patch_make(diffs)
        return dmp.patch_toText(patch)

    def generate_patch_html(old_version, new_version, field_name, cleanup=None):
        """
        Generates a pretty html version of the differences between the named
        field in two versions.

        The cleanup parameter can be None, "semantic" or "efficiency" to clean up the diff
        for greater human readibility.
        """
        warnings.warn("generate_patch_html will be removed in django-reversion 1.12.0", DeprecationWarning)
        diffs = generate_diffs(old_version, new_version, field_name, cleanup)
        return dmp.diff_prettyHtml(diffs)
