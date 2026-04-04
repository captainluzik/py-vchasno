"""Tests for vchasno.exceptions."""

from vchasno.exceptions import (
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    RateLimitError,
    VchasnoAPIError,
    VchasnoError,
)


class TestExceptionHierarchy:
    def test_vchasno_error_is_exception(self):
        assert issubclass(VchasnoError, Exception)

    def test_api_error_is_vchasno_error(self):
        assert issubclass(VchasnoAPIError, VchasnoError)

    def test_authentication_error(self):
        assert issubclass(AuthenticationError, VchasnoAPIError)

    def test_rate_limit_error(self):
        assert issubclass(RateLimitError, VchasnoAPIError)

    def test_not_found_error(self):
        assert issubclass(NotFoundError, VchasnoAPIError)

    def test_bad_request_error(self):
        assert issubclass(BadRequestError, VchasnoAPIError)


class TestVchasnoAPIError:
    def test_attributes(self):
        err = VchasnoAPIError("msg", status_code=500, response_body="body")
        assert err.status_code == 500
        assert err.response_body == "body"
        assert str(err) == "msg"

    def test_response_body_default_none(self):
        err = VchasnoAPIError("msg", status_code=400)
        assert err.response_body is None

    def test_subclass_preserves_attrs(self):
        err = AuthenticationError("forbidden", status_code=403, response_body="no")
        assert err.status_code == 403
        assert err.response_body == "no"
