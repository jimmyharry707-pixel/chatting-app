"""Presence registry lifecycle tests."""
from server.services.presence import PresenceRegistry

def test_user_becomes_online_on_first_connection():
    registry=PresenceRegistry()
    assert registry.connect(7,"desktop-a") is True
    assert registry.is_online(7)

def test_second_device_does_not_repeat_online_transition():
    registry=PresenceRegistry()
    registry.connect(7,"desktop-a")
    assert registry.connect(7,"desktop-b") is False

def test_user_stays_online_until_last_device_disconnects():
    registry=PresenceRegistry()
    registry.connect(7,"a"); registry.connect(7,"b")
    assert registry.disconnect(7,"a") is False
    assert registry.is_online(7)
    assert registry.disconnect(7,"b") is True
    assert not registry.is_online(7)
