import json
from datetime import datetime
from pathlib import Path


class TimeLogger:
    def __init__(self, json_path: str = "test_times.json"):
        """
        :param json_path: 기록할 JSON 파일 경로
        """
        self.json_path = Path(json_path)

        # 파일이 없으면 기본 구조 생성
        if not self.json_path.exists():
            self._init_file()

    def _init_file(self):
        """기본 JSON 구조 초기화"""
        data = [
            {
                "case1": {"keyword1":{"exposure": "", "click": "", "상품번호": ""},"keyword2":{"exposure": "", "click": "", "상품번호": ""}},
                "case2": {"keyword1":{"exposure": "", "click": "", "상품번호": ""},"keyword2":{"exposure": "", "click": "", "상품번호": ""}},
                "case3": {"keyword1":{"exposure": "", "click": "", "상품번호": ""},"keyword2":{"exposure": "", "click": "", "상품번호": ""}},
                "case4": {"keyword1":{"exposure": "", "click": "", "상품번호": ""},"keyword2":{"exposure": "", "click": "", "상품번호": ""}},
            }
        ]
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def record_time(self, case_name: str, keyword: str, action: str):
        """
        특정 케이스와 액션(exposure/click)에 현재 시간을 기록
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # JSON 읽기
        with open(self.json_path, "r", encoding="utf-8") as f:
            records = json.load(f)

        # case_name 존재 확인
        if case_name not in records[0]:
            records[0][case_name] = {}

        # keyword 존재 확인
        if keyword not in records[0][case_name]:
            records[0][case_name][keyword] = {}

        # 상품번호 업데이트
        records[0][case_name][keyword][action] = now

        # 다시 저장
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)

        print(f"[{case_name}] {action} 기록 완료: {now}")

    def record_goodscode(self, case_name: str, keyword: str, goodscode: str):
        """
        특정 케이스와 액션(exposure/click)에 현재 시간을 기록
        """
        # JSON 읽기
        with open(self.json_path, "r", encoding="utf-8") as f:
            records = json.load(f)

        # case_name 존재 확인
        if case_name not in records[0]:
            records[0][case_name] = {}

        # keyword 존재 확인
        if keyword not in records[0][case_name]:
            records[0][case_name][keyword] = {}

        # 상품번호 업데이트
        records[0][case_name][keyword]["상품번호"] = goodscode

        # 다시 저장
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)

        print(f"[{case_name}] 상품번호 기록 완료: {goodscode}")