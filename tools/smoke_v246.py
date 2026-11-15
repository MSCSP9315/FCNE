from playwright.sync_api import sync_playwright
import subprocess, time, sys, os

server=subprocess.Popen([sys.executable,"-m","http.server","8765","--bind","127.0.0.1"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    time.sleep(1)
    with sync_playwright() as p:
        browser=p.chromium.launch()
        page=browser.new_page(viewport={"width":390,"height":844})
        errors=[]
        page.on("pageerror",lambda exc: errors.append(str(exc)))
        page.goto("http://127.0.0.1:8765/index.html",wait_until="networkidle")

        # Open Training planen via the app's public entry function.
        # The bottom nav can be hidden on the initial category screen.
        page.evaluate("startWizard()")
        page.wait_for_selector("#eplanOverlay.open")

        # MH branch
        page.wait_for_selector("#fcneMhBranchCard")
        page.locator("#fcneMhBranchCard").click()
        page.wait_for_function("() => window.FCNE_ACTIVE_BRANCH === 'mh'")

        # Complete training must open visibly. Restrict to the visible MH branch panel,
        # because the home-card contains the same words but is hidden at this point.
        mh_branch=page.locator("#epBranch.open")
        mh_branch.get_by_text("29 komplette Trainingseinheiten",exact=True).click()
        page.wait_for_selector("#epLibrary.open .fcne-mh-unit-card")
        page.locator(".fcne-mh-unit-card").first.click()
        page.wait_for_selector("#mhUnitOverlay.open")
        assert page.locator("#mhUnitOverlay.open").is_visible()
        page.locator("#mhUnitOverlay .round-back").click()

        # Return to MH branch, then compose.
        page.locator("#epLibrary.open").get_by_role("button",name="‹ Zurück zu MH").click()
        page.locator("#epBranch.open").get_by_text("Training zusammenstellen",exact=True).click()
        page.wait_for_selector("#screen-wizard.active")
        assert page.locator("#screen-wizard.active").is_visible()
        assert page.evaluate("draft.sourceBranch")=="mh"
        assert page.evaluate("window.FCNE_ACTIVE_BRANCH")=="mh"
        assert page.evaluate("window.fcneBranchPool('mh').length")>=129
        assert page.evaluate("fcneBranchPool().filter(e=>e.fcneBranch==='mh').length")>=129

        if errors:
            raise AssertionError("Browser page errors: "+repr(errors))
        print("SMOKE_OK complete-unit + compose")
        browser.close()
finally:
    server.terminate()
    server.wait(timeout=10)
