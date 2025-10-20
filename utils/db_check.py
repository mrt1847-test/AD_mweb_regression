import requests
import time
#from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from src.gtas_python_core_v2.gtas_python_core_vault_v2 import Vault

#load_dotenv()

class DatabricksSPClient:
    def __init__(self):

        self.workspace_url = "https://adb-3951005985438017.17.azuredatabricks.net"
        self.warehouse_id = "d42f11fa1dd58612"
        self.access_token = (Vault("gmarket").get_Kv_credential("authentication/testrail/automation")).get("password")


    def query_databricks(self, sql: str, wait_timeout="30s"):
        """Databricks SQL Warehouse에서 쿼리 실행 후 DataFrame으로 반환"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        # 1. 쿼리 실행 요청
        submit_url = f"{self.workspace_url}/api/2.0/sql/statements"
        payload = {
            "statement": sql,
            "warehouse_id": self.warehouse_id,
            "wait_timeout": wait_timeout,
            "on_wait_timeout": "CONTINUE"
        }
        res = requests.post(submit_url, headers=headers, json=payload)
        res.raise_for_status()
        statement_id = res.json()["statement_id"]

        # 2. 쿼리 실행 상태 확인 (polling)
        status_url = f"{self.workspace_url}/api/2.0/sql/statements/{statement_id}"
        while True:
            res = requests.get(status_url, headers=headers)
            res.raise_for_status()
            state_data = res.json()
            state = state_data.get("status", {}).get("state")
            if state in ("SUCCEEDED", "FAILED", "CANCELED"):
                break
            time.sleep(2)

        if state != "SUCCEEDED":
            raise Exception(f"Query failed with state: {state}")

        # 3. 결과를 DataFrame으로 변환
        result = state_data.get("result", {})
        return result

    def assert_db_record_time(self, db_data, record_time, goodscode):
        """
       DB에 기록된 특정 상품의 시간 기록이 테스트 기록 시간과 일정 허용 오차 내에 있는지 검증하는 함수

       :param db_data: dict, DB에서 조회한 데이터 (예: {"data_array": [[상품번호, ...], ...]})
       :param record_time: str, 테스트 실행 시 기록한 시간 (형식: "YYYY-MM-DD HH:MM:SS")
       :param goodscode: str, 검증할 상품 번호
       :raises AssertionError: DB에 해당 상품이 없거나, DB 기록 시간이 허용 오차(10초)를 벗어날 경우
       :return: None (검증 통과 시 아무 값도 반환하지 않음)

       :example:
       db_data = {
           "data_array": [
               ["2997549821", "2025-09-30 13:00:45"],
               ["2512116583", "2025-09-30 13:01:03"]
           ]
       }
       record_time = "2025-09-30 13:00:50"
       goodscode = "2997549821"
       self.assert_db_record_time(db_data, record_time, goodscode)
       """
        db_row = next(
            (row for row in db_data["data_array"] if row[0] == goodscode),
            None
        )
        if db_row is None:
            raise AssertionError(f"{goodscode}에 해당하는 DB 기록이 없습니다.")  # DB에 레코드가 없는 경우 명확하게 실패 처리

        db_time = db_row[0]  # 안전하게 db_row에서 시간 가져오기

        # 테스트 기록 시간과 DB 기록 시간 비교
        dt1 = datetime.strptime(record_time, "%Y-%m-%d %H:%M:%S")
        dt2 = datetime.strptime(db_time, "%Y-%m-%d %H:%M:%S")
        dt3 = dt1 + timedelta(seconds=10)  # 허용 오차 10초
        print(f"[ASSERT_DB_RECORD_TIME] goodscode={goodscode}, record_time={dt1}, db_time={dt2}")

        assert dt1 <= dt2 <= dt3  # DB 기록 시간이 테스트 기록 시간 ±10초 범위 안인지 확인
