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

        assert page.locator("#trainingName").input_value()=="MH Training"
        assert page.locator("#nextBtn").is_enabled()
        assert page.evaluate("draft.sourceBranch")=="mh"

        # Grunddaten -> Aufwärmen
        page.locator("#nextBtn").click()
        page.wait_for_function("() => wizardStep===1")

        phase_names=["Aufwärmen","Vielseitigkeit","Fussball spielen lernen","Fussball spielen","Ausklang"]
        for expected_step,phase in enumerate(phase_names,start=1):
            assert page.evaluate("wizardStep")==expected_step
            cards=page.locator(".choice-card")
            count=cards.count()
            assert count>0, f"no MH choices for {phase}"
            cards.first.click()
            assert page.locator("#nextBtn").is_enabled(), f"next disabled after choosing {phase}"
            page.locator("#nextBtn").click()
            page.wait_for_function(f"() => wizardStep==={expected_step+1}")

        assert page.evaluate("wizardStep")==6
        assert page.locator("#wizardBody").get_by_text("Trainingsübersicht",exact=False).count()>0
        assert len(page.evaluate("Object.keys(draft.selections)"))==5

        # Also keep the complete-unit path covered.
        page.evaluate("startWizard()")
        page.wait_for_selector("#eplanOverlay.open")
        page.locator("#fcneMhBranchCard").click()
        page.locator("#epBranch.open").get_by_text("29 komplette Trainingseinheiten",exact=True).click()
        page.wait_for_selector("#epLibrary.open .fcne-mh-unit-card")
        page.locator(".fcne-mh-unit-card").first.click()
        page.wait_for_selector("#mhUnitOverlay.open")
        assert page.locator("#mhUnitOverlay.open").is_visible()

        if errors:
            raise AssertionError("Browser page errors: "+repr(errors))
        print("SMOKE_OK v2.48 MH full manual flow + complete unit")
        browser.close()
finally:
    server.terminate()
    server.wait(timeout=10)
