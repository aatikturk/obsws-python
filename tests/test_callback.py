import pytest
from obsws_python.callback import Callback


class TestCallbacks:
    __test__ = True

    @classmethod
    def setup_class(cls):
        cls.callback = Callback()

    @pytest.fixture(autouse=True)
    def wraps_tests(self):
        yield
        self.callback.clear()

    def test_register_callback(self):
        def on_callback_method():
            pass

        self.callback.register(on_callback_method)
        assert self.callback.get() == ["CallbackMethod"]

    def test_register_callbacks(self):
        def on_callback_method_one():
            pass

        def on_callback_method_two():
            pass

        self.callback.register((on_callback_method_one, on_callback_method_two))
        assert self.callback.get() == ["CallbackMethodOne", "CallbackMethodTwo"]

    def test_deregister_callback(self):
        def on_callback_method_one():
            pass

        def on_callback_method_two():
            pass

        self.callback.register((on_callback_method_one, on_callback_method_two))
        self.callback.deregister(on_callback_method_one)
        assert self.callback.get() == ["CallbackMethodTwo"]

    def test_deregister_callbacks(self):
        def on_callback_method_one():
            pass

        def on_callback_method_two():
            pass

        def on_callback_method_three():
            pass

        self.callback.register(
            (on_callback_method_one, on_callback_method_two, on_callback_method_three)
        )
        self.callback.deregister((on_callback_method_two, on_callback_method_three))
        assert self.callback.get() == ["CallbackMethodOne"]
