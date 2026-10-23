/* Real-browser regression check. Requires Playwright and its Chromium browser. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {spawn} = require('node:child_process');
const root = path.resolve(__dirname, '..');
let playwright;
try { playwright = require(process.env.CROSSWIRE_PLAYWRIGHT || 'playwright'); }
catch { playwright = require(path.join(process.env.USERPROFILE || process.env.HOME, '.codex/skills/develop-web-game/node_modules/playwright')); }
const python = process.env.CROSSWIRE_PYTHON || path.join(root, '.venv', process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python');

(async () => {
    const child = spawn(python, ['-m', 'crosswire', 'serve', '--port', '0'], {cwd:root, windowsHide:true, stdio:['ignore','pipe','pipe']});
    let browser, serverErrors = '';
    child.stderr.on('data', value => serverErrors += value);
    try {
        const base = await new Promise((resolve, reject) => {
            const timer = setTimeout(() => reject(new Error('Workbench server did not start')), 15000);
            child.stdout.once('data', value => {clearTimeout(timer);resolve(String(value).trim());});
            child.once('error', reject);
            child.once('exit', code => {clearTimeout(timer);reject(new Error(`Server exited: ${code} ${serverErrors}`));});
        });
        browser = await playwright.chromium.launch({headless:true});
        const page = await browser.newPage({viewport:{width:1440,height:1000}}), errors = [];
        page.on('pageerror', error => errors.push(error.message));
        await page.goto(base);
        await page.waitForFunction(() => !document.querySelector('#run-button').disabled);
        await page.selectOption('#admission', 'adaptive');
        assert.equal(await page.inputValue('#execution_mode'), 'shielded', 'Adaptive selection must choose a compatible deployment mode');
        await page.selectOption('#execution_mode', 'replan');
        assert.equal(await page.inputValue('#execution_mode'), 'replan', 'Adaptive mode must permit replanning shield');
        await page.selectOption('#execution_mode', 'recovery');
        assert.equal(await page.inputValue('#execution_mode'), 'recovery', 'Adaptive mode must permit certified recovery');
        await page.selectOption('#policy', 'ec2');
        assert.equal(await page.inputValue('#policy'), 'ec2', 'Workbench must allow selecting EC2 active probing');
        await page.selectOption('#policy', 'task');
        await page.selectOption('#admission', 'risk_controlled');
        assert.equal(await page.inputValue('#admission'), 'risk_controlled', 'Workbench must allow risk-controlled admission');
        await page.selectOption('#admission', 'adaptive');
        await page.check('#temporal');
        await page.check('#escalate');
        assert.equal(await page.isChecked('#temporal'), false);
        assert.equal(await page.isDisabled('#temporal'), true);
        await page.uncheck('#escalate');
        assert.equal(await page.isDisabled('#temporal'), false);
        await page.selectOption('#family', 'routing');
        await page.fill('#seed', '42');
        await page.fill('#budget', '0');
        await page.fill('#horizon', '3');
        await page.selectOption('#split', 'evaluation');
        assert.match(await page.textContent('#study-description'), /4 runs/);
        const submitted = page.waitForRequest(req => req.method() === 'POST' && req.url().endsWith('/api/studies'));
        await page.click('#study-button');
        const spec = (await submitted).postDataJSON();
        assert.deepEqual(spec, {families:['routing'],seeds:[42,43],budgets:[0],policies:['task'],admissions:['robust','adaptive'],implementations:['procedural'],anchors:false,split:'evaluation',horizon:3,temporal:false,escalate:false,execution_mode:'recovery'});
        await page.waitForFunction(() => !document.querySelector('#result-view').hidden && document.querySelector('#job-panel').hidden, {timeout:60000});
        assert.match(await page.textContent('#result-content'), /parent[ _]clusters/i);
        assert.match(await page.textContent('#result-content'), /descriptive[ _]95/i);
        const downloadPromise = page.waitForEvent('download');
        await page.click('#export-button');
        const download = await downloadPromise;
        const receipt = fs.readFileSync(await download.path(), 'utf8');
        const original = JSON.parse(receipt);
        assert.equal(original.payload.rows.length, 4);
        for (const action of ['replay', 'import']) {
            const block = await page.request.post(base + 'api/studies', {data:{families:['latch'],seeds:[1,2,3,4,5,6,7,8],budgets:[16],policies:['fixed']}});
            const blocking = await block.json();
            assert.ok(blocking.id);
            let submittedJob;
            const jobResponse = page.waitForResponse(response => response.request().method() === 'POST' && (action === 'replay' ? response.url().endsWith('/replay') : response.url().endsWith('/api/import')));
            if (action === 'replay') {
                await page.click('#replay-button');
            } else {
                await page.setInputFiles('#receipt-file', {name:'receipt.json',mimeType:'application/json',buffer:Buffer.from(receipt)});
            }
            submittedJob = await (await jobResponse).json();
            await page.waitForSelector('#job-panel:not([hidden])');
            assert.equal(await page.isEnabled('#cancel-button'), true, `${action} must expose cancellation`);
            const cancelRequest = page.waitForRequest(req => req.method() === 'POST' && req.url().endsWith(`/${submittedJob.id}/cancel`));
            await page.click('#cancel-button');
            await cancelRequest;
            await page.request.post(base + `api/runs/${blocking.id}/cancel`, {data:{}});
            await page.waitForFunction(() => document.querySelector('#job-panel').hidden, {timeout:60000});
            assert.match(await page.textContent('#notice'), /cancelled/i);
            assert.equal(await page.isVisible('#result-view'), true, 'Cancellation preserves previous complete evidence');
        }
        await page.selectOption('#family', 'symmetric');
        await page.selectOption('#admission', 'robust');
        await page.click('#run-button');
        await page.waitForFunction(() => document.querySelector('#result-kind').textContent === 'EXPERIMENT RECEIPT' && document.querySelector('#job-panel').hidden, {timeout:60000});
        assert.match(await page.textContent('#result-content'), /Public model evidence/);
        assert.match(await page.textContent('#result-content'), /does not authenticate/i);
        const output = path.join(root,'output/playwright');
        fs.mkdirSync(output,{recursive:true});
        await page.screenshot({path:path.join(output,'evidence-workbench-desktop.png'),fullPage:true});
        await page.setViewportSize({width:390,height:900});
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth), true, 'Mobile workbench must not overflow horizontally');
        await page.screenshot({path:path.join(output,'evidence-workbench-mobile.png'),fullPage:true});
        assert.deepEqual(errors, []);
        assert.equal(serverErrors, '');
        console.log('PASS: control compatibility, exact study protocol, visible paired evidence, receipt export, cancellable replay/import, certificate scope, responsive layout');
    } finally {
        if (browser) await browser.close();
        child.kill();
    }
})().catch(error => {console.error(error);process.exitCode=1;});
