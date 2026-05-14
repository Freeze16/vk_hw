import pytest
from unittest.mock import AsyncMock, patch, call

from retryer import retry_with_backoff


@pytest.fixture
def mock_success_func():
    return AsyncMock(return_value="success")


@pytest.fixture
def mock_fail_then_success_func():
    mock = AsyncMock()
    mock.side_effect = [
        ValueError("Error 1"),
        ValueError("Error 2"),
        "success"
    ]
    return mock


@pytest.mark.asyncio
async def test_retry_success_immediately(mock_success_func):
    with patch("asyncio.sleep", AsyncMock()) as mock_sleep:
        result = await retry_with_backoff(mock_success_func)

        assert result == "success"
        assert mock_success_func.call_count == 1
        mock_sleep.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("base_delay, expected_delays", [
    (1.0, [1.0, 2.0]),
    (0.5, [0.5, 1.0]),
    (2.0, [2.0, 4.0]),
])
async def test_retry_fail_then_success_delays(
        mock_fail_then_success_func,
        base_delay,
        expected_delays
):
    with patch("asyncio.sleep", AsyncMock()) as mock_sleep:
        result = await retry_with_backoff(
            mock_fail_then_success_func,
            max_attempts=3,
            base_delay=base_delay,
            exceptions=(ValueError,)
        )

        assert result == "success"
        assert mock_fail_then_success_func.call_count == 3
        assert mock_sleep.call_count == len(expected_delays)

        expected_calls = [call(d) for d in expected_delays]
        assert mock_sleep.await_args_list == expected_calls


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exceptions_list, occurred_exceptions_list, expected_exception",
    [
        (
                (ValueError,),
                [ValueError("Err 1"), ValueError("Err 2")],
                ValueError
        ),
        (
                (ValueError, KeyError),
                [ValueError("Err 1"), KeyError("Err 2")],
                KeyError
        ),
    ]
)
async def test_retry_all_failures(
        exceptions_list,
        occurred_exceptions_list,
        expected_exception
):
    mock_func = AsyncMock()
    mock_func.side_effect = occurred_exceptions_list

    max_attempts = len(occurred_exceptions_list)

    with patch("asyncio.sleep", AsyncMock()):
        with pytest.raises(expected_exception) as exc_info:
            await retry_with_backoff(
                mock_func,
                max_attempts=max_attempts,
                exceptions=exceptions_list
            )

        assert str(exc_info.value) == str(occurred_exceptions_list[-1])