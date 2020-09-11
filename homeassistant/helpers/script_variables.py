"""Script variables."""
from typing import Any, Dict, Mapping, Optional

from homeassistant.core import HomeAssistant, callback

from . import template


class ScriptVariables:
    """Class to hold and render script variables."""

    def __init__(self, variables: Dict[str, Any]):
        """Initialize script variables."""
        self.variables = variables
        self._has_template: Optional[bool] = None

    @callback
    def async_render(
        self,
        hass: HomeAssistant,
        run_variables: Optional[Mapping[str, Any]],
    ) -> Dict[str, Any]:
        """Render script variables.

        The run variables are used to compute the static variables, but afterwards will also
        be merged on top of the static variables.
        """
        if self._has_template is None:
            self._has_template = template.is_complex(self.variables)
            template.attach(hass, self.variables)

        if not self._has_template:
            rendered_variables = dict(self.variables)

            if run_variables is not None:
                rendered_variables.update(run_variables)

            return rendered_variables

        rendered_variables = {} if run_variables is None else dict(run_variables)

        for key, value in self.variables.items():
            # We can skip if we're going to override this key with
            # run variables anyway
            if key in rendered_variables:
                continue

            rendered_variables[key] = template.render_complex(value, rendered_variables)

        if run_variables:
            rendered_variables.update(run_variables)

        return rendered_variables

    def as_dict(self) -> dict:
        """Return dict version of this class."""
        return self.variables
