from playwright.sync_api import sync_playwright
import subprocess, time, sys

server=subprocess.Popen([sys.executable,"-m","http.server","8765","--bind","127.0.0.1"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    time.sleep(1)
    with sync_playwright() as p:
        browser=p.chromium.launch()
        page=browser.new_page(viewport={"width":390,"height":844})
        errors=[]
        page.on("pageerror",lambda exc: errors.append(str(exc)))
        page.goto("http://127.0.0.1:8765/index.html",wait_until="networkidle")

        page.evaluate("startWizard()")
        page.wait_for_selector("#eplanOverlay.open")
        page.wait_for_selector("#fcneMhBranchCard")
        page.locator("#fcneMhBranchCard").click()
        page.wait_for_function("() => window.FCNE_ACTIVE_BRANCH === 'mh'")

        page.locator("#epBranch.open").get_by_text("Training zusammenstellen",exact=True).click()
        page.wait_for_selector("#screen-wizard.active")

        # Step 1 / Grunddaten: must be usable immediately.
        assert page.locator("#trainingName").input_value()=="MH Training"
        assert page.locator("#nextBtn").is_enabled()
        assert page.evaluate("draft.sourceBranch")=="mh"

        # Click Weiter and ensure the first exercise-selection step renders.
        page.locator("#nextBtn").click()
        page.wait_for_function("() => typeof wizardStep!=='undefined' && wizardStep===1")
        page.wait_for_selector("#screen-wizard.active .choice-card")
        assert page.locator(".choice-card").count()>0

        # Walk through all five MH phases to catch missing DOM images / empty pools.
        for expected_step in range(1,6):
            assert page.evaluate("wizardStep")==expected_step
            cards=page.locator(".choice-card")
            assert cards.count()>0, f"no choices at wizard step {expected_step}"
            cards.first.click()
            assert page.locator("#nextBtn").is_enabled()
            page.locator("#nextBtn").click()
            page.wait_for_function(f"() => wizardStep==={expected_step+1}")

        # Summary step reached.
        assert page.evaluate("wizardStep")==6
        assert page.locator("#wizardBody").get_by_text("Trainingsübersicht",exact=False).count()>0

        if errors:
            raise AssertionError("Browser page errors: "+repr(errors))
        print("SMOKE_OK MH compose full flow Grunddaten -> 5 phases -> summary")
        browser.close()
finally:
    server.terminate()
    server.wait(timeout=10)
