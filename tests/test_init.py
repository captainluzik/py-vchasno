"""Tests for vchasno.__init__ exports."""

import vchasno


class TestPackageExports:
    def test_vchasno_class(self):
        assert hasattr(vchasno, "Vchasno")

    def test_async_vchasno_class(self):
        assert hasattr(vchasno, "AsyncVchasno")

    def test_vchasno_error(self):
        assert hasattr(vchasno, "VchasnoError")

    def test_vchasno_api_error(self):
        assert hasattr(vchasno, "VchasnoAPIError")

    def test_authentication_error(self):
        assert hasattr(vchasno, "AuthenticationError")

    def test_rate_limit_error(self):
        assert hasattr(vchasno, "RateLimitError")

    def test_not_found_error(self):
        assert hasattr(vchasno, "NotFoundError")

    def test_bad_request_error(self):
        assert hasattr(vchasno, "BadRequestError")

    def test_all_exports(self):
        expected = [
            "AsyncVchasno",
            "Vchasno",
            "VchasnoError",
            "VchasnoAPIError",
            "AuthenticationError",
            "RateLimitError",
            "NotFoundError",
            "BadRequestError",
        ]
        for name in expected:
            assert name in vchasno.__all__
