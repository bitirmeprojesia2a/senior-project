from src.db.schedule_scrapling import collect_schedule_slots_from_scrapling_response


class _FakeTextSelector:
    def __init__(self, values):
        self._values = values

    def getall(self):
        return self._values


class _FakeNode:
    def __init__(self, text="", *, children=None, text_values=None):
        self.text = text
        self._children = children or {}
        self._text_values = text_values or [text]

    def css(self, query):
        if query == "::text":
            return _FakeTextSelector(self._text_values)
        return self._children.get(query, [])


def test_collect_schedule_slots_from_scrapling_response_parses_html_table():
    row_1 = _FakeNode(children={
        "th, td": [
            _FakeNode(""),
            _FakeNode("Pazartesi"),
            _FakeNode("Sali"),
            _FakeNode("Carsamba"),
        ]
    })
    row_2 = _FakeNode(children={
        "th, td": [
            _FakeNode("12.30"),
            _FakeNode(""),
            _FakeNode(""),
            _FakeNode("LPFE402 Ozel Ogretim Yontemleri"),
        ]
    })
    row_3 = _FakeNode(children={
        "th, td": [
            _FakeNode("13.30"),
            _FakeNode(""),
            _FakeNode(""),
            _FakeNode("LPFE402 Ozel Ogretim Yontemleri"),
        ]
    })
    table = _FakeNode(children={"tr": [row_1, row_2, row_3]})
    response = _FakeNode(
        text="2025-2026 BAHAR PEDAGOJIK FORMASYON DERS PROGRAMI",
        children={"table": [table]},
        text_values=["2025-2026 BAHAR PEDAGOJIK FORMASYON DERS PROGRAMI"],
    )

    slots = collect_schedule_slots_from_scrapling_response(
        response,
        source_name="formasyon.html",
        source_url="https://example.edu/formasyon.html",
    )

    assert len(slots) == 2
    assert slots[0]["course_code"] == "LPFE402"
    assert slots[0]["day_of_week"] == "Carsamba"
    assert slots[0]["source_document"] == "formasyon.html"
    assert slots[0]["source_url"] == "https://example.edu/formasyon.html"
