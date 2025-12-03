from phase1_sn_api.servicenow_client import ServiceNowClient


def test_query_and_get_incident() -> None:
    client = ServiceNowClient.from_env()

    recent = client.query_incidents({"active": "true"}, limit=5)
    assert isinstance(recent, list), "query_incidents should return a list"
    assert len(recent) >= 1, "No active incidents found to read"

    print("✅ Queried incidents (showing up to 5):")
    for inc in recent:
        print(f"  {inc.get('number')} | {inc.get('short_description')} | sys_id={inc.get('sys_id')}")

    first = recent[0]
    detailed = client.get_incident(first["sys_id"])
    assert detailed["sys_id"] == first["sys_id"], "get_incident returned a different record"
    print(f"✅ Retrieved incident: number={detailed.get('number')} sys_id={detailed.get('sys_id')}")
