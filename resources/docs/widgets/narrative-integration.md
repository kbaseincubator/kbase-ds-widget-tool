# Narrative Integration

The first iteration of DS Widgets utilized an iframes + window messaging approach, both
to control widget lifecycle (e.g. start with auth and params) and state preservation.

This approach, however, is not suitable for Python-based DS widgets. And by
extrapolation, it is not a good general solution.

I do think that it is still the most viable approach for state synchronization, but that
is probably a conversation for another chapter.

For widget lifecycle, I think we'll need two features:

- use the standard KBase auth cookie, kbase_session, for authentication.

- use url path and search fragment (query paramaters) for widget parameterization.

## Auth Cookie

The auth cookie `kbase_session` will always be present in the browser if the DS widget
is accessed from the Narrative. The DS widget can simply read and use the cookie's token
value.

The only complication is prod, in which user interfaces operate on `narrative.kbase.us`
and services on `kbase.us`.  To accommodate this, the `kbase_session_backup` cookie is
utilized  to allow services to access an auth cookie. This is to accommodate the
HTMLFileSetService.

## Widget Parameterization

Since a widget is invoked by a call to a DS service endpoint, parameters may be passed
by the usual means for a URL - within the pathname and in the search fragment.
