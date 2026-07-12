from divyadrishti.ai import ConversationMemory


def test_memory_adds_exchange():
    memory = ConversationMemory()
    memory.add_exchange("Hello", "Welcome")
    assert len(memory.get_history()) == 2


def test_memory_respects_max_history():
    memory = ConversationMemory(max_history=2)
    for i in range(5):
        memory.add_exchange(f"q{i}", f"a{i}")
    assert len(memory.get_history()) == 4


def test_memory_preferences():
    memory = ConversationMemory()
    memory.set_preference("language", "hi")
    assert memory.get_preference("language") == "hi"
