def test_vite_env_fixture_is_available(vite_env):
    assert vite_env in {"development", "production"}
