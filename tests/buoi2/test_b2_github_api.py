"""Buoi 2 - B2.13 GitHub REST API (syllabus 6.2).

Same APIRequestContext you used for Toolshop, on a different, real public API.
Fixture: github (see conftest.py). Docs: https://docs.github.com/en/rest

Rate limit: without a token GitHub allows 60 calls per hour per IP address. The whole class shares
the school's IP, so create a token (github.com > Settings > Developer settings > Fine-grained tokens,
no permissions needed) and put it in .env as GITHUB_TOKEN. Never commit .env.

Run:  pytest tests/buoi2/test_b2_github_api.py -v
"""
import re
import uuid
from importlib.metadata import version

import pytest

pytestmark = [pytest.mark.api, pytest.mark.github]

REPO = "microsoft/playwright-python"


# ---------------------------------------------------------------- B2.13a
def test_b2_13a_github_repo_returns_expected_metadata(github):
    """Goal: GET /repos/{owner}/{repo} describes the repository.
    Precondition: the repository is public.
    Expected: 200, full_name equals REPO, language Python, licence spdx_id Apache-2.0,
    stargazers_count is an int > 0, archived is False."""
    """Goal: kiểm tra metadata của repository công khai.
    Precondition: repository microsoft/playwright-python tồn tại.
    Expected: đúng tên, ngôn ngữ, giấy phép và trạng thái."""
    response = github.get(f"/repos/{REPO}")

    assert response.status == 200, response.text()

    body = response.json()

    assert body["full_name"] == REPO, body
    assert body["language"] == "Python", body

    license_info = body.get("license")

    assert isinstance(license_info, dict), license_info
    assert license_info["spdx_id"] == "Apache-2.0", license_info

    assert isinstance(body["stargazers_count"], int), body
    assert body["stargazers_count"] > 0, body
    assert body["archived"] is False, body


# ---------------------------------------------------------------- B2.13b
def test_b2_13b_github_unknown_user_returns_404_with_message(github):
    """Goal: kiểm tra phản hồi cho người dùng không tồn tại.
    Precondition: tạo tên người dùng ngẫu nhiên.
    Expected: trả về 404 và message Not Found."""
    username = f"no-such-user-{uuid.uuid4().hex[:12]}"

    response = github.get(f"/users/{username}")

    assert response.status == 404, response.text()
    assert response.json()["message"] == "Not Found"


# ---------------------------------------------------------------- B2.13c
def test_b2_13c_github_response_reports_rate_limit(github):
    """Goal: kiểm tra header giới hạn lượt gọi API.
    Precondition: gọi endpoint rate_limit.
    Expected: limit và remaining là số, 0 <= remaining <= limit."""
    response = github.get("/rate_limit")

    assert response.status == 200, response.text()

    limit = int(response.headers["x-ratelimit-limit"])
    remaining = int(response.headers["x-ratelimit-remaining"])

    assert limit > 0, response.headers
    assert 0 <= remaining <= limit, response.headers


# ---------------------------------------------------------------- B2.13d (challenge)
def test_b2_13d_github_latest_release_matches_installed_playwright(
    github,
):
    """Goal: so sánh bản phát hành với Playwright đang cài.
    Precondition: đọc được latest release và phiên bản cài trên máy.
    Expected: tag hợp lệ và bản phát hành không cũ hơn bản đang cài."""
    response = github.get(f"/repos/{REPO}/releases/latest")

    assert response.status == 200, response.text()

    body = response.json()
    tag = body["tag_name"]

    assert re.fullmatch(r"v\d+\.\d+\.\d+", tag), tag

    latest_version = tuple(
        int(part)
        for part in tag.removeprefix("v").split(".")
    )

    installed = version("playwright")

    installed_version = tuple(
        int(part)
        for part in installed.split(".")
    )

    assert latest_version >= installed_version, (
        f"Latest release: {tag}; "
        f"Playwright đang cài: {installed}"
    )
