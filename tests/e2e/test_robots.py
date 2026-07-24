def test_robots(page, live_server_url):
    page.goto(str(live_server_url + "/robots.txt"))
    assert "User-agent: *" in page.content()
