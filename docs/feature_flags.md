# Feature flags

Feature flags should be used to conditionally show/hide new functionality which
is not ready for general release.  Feature flags enable the team to merge in 
"work in progress" features without distrupting the production operation of the 
system.

They do, however, introduce conditionality to the codebase which increases complexity
somewhat.  Developing with a feature flag active *can* mask a breakage in
code paths where the feature flag is off.  It also increases cognitive load in working
with the system.

As such, feature flags should be used sparingly and always cleaned up once they 
are ready to be switched on permanently.

## Feature flag usage

### Adding a feature flag

Add an entry to the `config.settings.base.FEATURE_FLAGS` enum.  e.g.
```
class FEATURE_FLAGS(Enum):  # noqa: N801
    TEST_FEATURE_FLAG = "test-feature-flag"
    EARLY_YEARS = "early-years"
```
The feature flag will be disabled by default.

### Checking a feature flag in templates

Feature flags can be interrogated in templates to conditionally show/hide functionality;
```
{% if is_feature_flag_enabled(FEATURE_FLAGS.EARLY_YEARS) %}
   <early years specific HTML>
{% endif %}
```

### Checking a feature flag in python

Feature flags can be interrogated in python code (e.g. a view) as follows:

```
from django.conf import settings

from datagovuk.feature_flags import is_feature_flag_active
...

if is_feature_flag_active(settings.FEATURE_FLAGS.EARLY_YEARS):
    ...
```

### Switching a feature flag on locally

This can be achieved by setting the feature flag on in `.envs/.local/.django` e.g.
```
FEATURE_FLAGS_ENABLED=test-feature-flag,early-years
```

### Switching a feature flag on a non-production kubernetes env

This should be achieved by setting the `FEATURE_FLAGS_ENABLED` environment 
variable for the environment in the https://github.com/alphagov/govuk-dgu-charts repo.


### Switching a feature flag on in production

This should be achieved by setting the `FEATURE_FLAGS_ENABLED` default value in 
`config.settings.base`.  The feature flag should be deleted from the codebase 
once we are happy that things are working and we don't need to switch it off again.
