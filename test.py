from docutils.nodes import target


def test_home_module_check():
    from pom.Etc import Etc
    from pom.HomePage import HomePage
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 420, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)",
            is_mobile=True,
            has_touch=True
        )
        page = context.new_page()
        etc = Etc(page)
        home_page = HomePage(page)

        etc.goto()
        etc.login("t4adbuy01", "Gmkt1004!!")
        parent = home_page.home_module_by_title("이 상품을 본 고객들이")
        goodscode = home_page.assert_item_in_module("이 상품을 본 고객들이")
        print(goodscode)
        # 광고 태크 체크
        result = home_page.check_rvi_vt_cpc_ad_tag(parent)
        print(result)

        # 상품 클릭후 해당 vip 이동 확인
        #home_page.montelena_goods_click(goodscode)
        print(target)
        home_page.click_goods(goodscode)


        print("✅ 모듈 탐색 테스트 완료")


        context.close()
        browser.close()