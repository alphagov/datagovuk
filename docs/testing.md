# Testing in datagovuk

We have three categories of tests in datagovuk; unit tests, django view tests and end to end tests.

## Unit tests

- These tests should be located as close as possible to the code under test - within a `tests/` directory.
- Tests should reflect the structure of the code under test; e.g. 
  `class CollectionService` should be tested with `class TestCollectionService`
  `def render_markdown` should be tested with `def test_render_markdown_...`
- Test function/method names should describe;
    - The thing under test (method, function, view)
    - The test state
    - The expected behaviour
    - Although sometimes, the state/expected behaviour is superfluous.  We should be pragmatic when naming tests.

## Django view tests

These are more like integration tests as they can involve more dependencies than unit tests - e.g. database access.  
They use [django's test client](https://docs.djangoproject.com/en/6.0/topics/testing/tools/#the-test-client) which simulates browser access to the application.

For rendered HTML responses, we should use these tests to check that the template context is as expected under
different states.

## End to end tests

We use [playwright](https://playwright.dev/) as an end to end test runner.

These tests orchestrate a browser to interact with the application.  They should simulate real user interactions
and give us confidence that the application is behaving correctly and that users will be able to achieve their goals.
