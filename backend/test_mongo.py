from fastapi_app.mongo import insert_event, get_events_by_project

insert_event({"project_id": "test", "event_type": "page_view", "ts": "2024-01-01"})
print(get_events_by_project("test"))
