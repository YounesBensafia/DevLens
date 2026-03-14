from devlens.llm.exception import LLMClientError


def test_llm_client_error_string_includes_context():
	err = LLMClientError(
		"Request failed",
		status_code=400,
		original_exception=ValueError("bad input"),
	)

	rendered = str(err)
	assert "Request failed" in rendered
	assert "status 400" in rendered
	assert "ValueError" in rendered