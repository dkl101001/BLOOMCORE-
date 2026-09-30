// SPDX-License-Identifier: AGPL-3.0-only
// Optional test dependency: npm install playwright && npx playwright install chromium
const { chromium } = require('playwright');
const { spawn } = require('node:child_process');
const path = require('node:path');
const fs = require('node:fs');

(async () => {
  const root=path.resolve(__dirname,'..');
  const state=process.env.TI_TEST_STATE || path.join(root,'browser-test.sqlite');
  const server=spawn(process.env.TI_PYTHON || 'python3',['-m','tiagi83','--state',state,'--port','8383','--backend','jax'],{cwd:root});
  let browser;
  try {
    await new Promise((resolve,reject)=>{server.stdout.on('data',d=>{if(d.toString().includes('http://'))resolve()});server.stderr.on('data',d=>process.stderr.write(d));server.once('exit',code=>reject(Error('Server exited '+code)));});
    let args=[];
    if(process.env.TI_CHROME_MODULE){const {default:c}=await import(process.env.TI_CHROME_MODULE);args=c.args;}
    browser=await chromium.launch({headless:true,args,...(process.env.TI_CHROME?{executablePath:process.env.TI_CHROME}:{})});
    const page=await browser.newPage({viewport:{width:1280,height:1100},acceptDownloads:true}),errors=[];
    page.on('pageerror',e=>errors.push(e.message));
    await page.goto('http://127.0.0.1:8383');await page.locator('#status').filter({hasText:'JAX BACKEND'}).waitFor();
    await page.getByRole('button',{name:'Audit sheet',exact:true}).click();await page.locator('#count').filter({hasText:'(1)'}).waitFor();
    await page.getByRole('button',{name:'Apply verified repairs',exact:true}).click();await page.locator('#status').filter({hasText:'WORK VERIFIED'}).waitFor();
    if(await page.getByRole('textbox',{name:'Row 2, Line total',exact:true}).inputValue()!=='32.00')throw Error('Repair failed');
    await page.getByRole('button',{name:'Restore sample as new sheet',exact:true}).click();await page.locator('#status').filter({hasText:'READY'}).waitFor();
    await page.getByRole('button',{name:'Audit sheet',exact:true}).click();await page.locator('#findings').filter({hasText:'Related incident #'}).waitFor();
    await page.getByRole('button',{name:'GRAPH',exact:true}).click();await page.locator('.graph-view').waitFor();if(await page.locator('.graph-cell').count()!==64)throw Error('Wrong geometry size');
    const out=process.env.TI_SCREENSHOT_DIR || root;
    await page.screenshot({path:path.join(out,'ti-agi83-desktop.png'),fullPage:true});
    await page.getByRole('button',{name:'TRACE',exact:true}).click();await page.locator('#status').filter({hasText:'LINEAGE RETAINED'}).waitFor();
    await page.getByRole('textbox',{name:'Row 1, Qty',exact:true}).fill('unknown');await page.getByRole('button',{name:'Audit sheet',exact:true}).click();await page.locator('#findings').filter({hasText:'plain bounded number'}).waitFor();
    await page.getByRole('button',{name:'Apply verified repairs',exact:true}).click();await page.locator('#status').filter({hasText:'HUMAN INPUT NEEDED'}).waitFor();
    if(await page.getByRole('textbox',{name:'Row 1, Qty',exact:true}).inputValue()!=='unknown')throw Error('Invented a value');
    const dlPromise=page.waitForEvent('download');await page.locator('[data-cmd="export"]').click();const dl=await dlPromise;if(!dl.suggestedFilename().endsWith('.csv'))throw Error('No CSV');
    await page.reload();await page.locator('#status').filter({hasText:'JAX BACKEND'}).waitFor();
    await page.getByRole('button',{name:'invoice sample copy',exact:true}).click();await page.locator('#status').filter({hasText:'AWAITING HUMAN ERROR'}).waitFor();if(await page.getByRole('textbox',{name:'Row 1, Qty',exact:true}).inputValue()!=='unknown')throw Error('Restart lost edits');
    await page.locator('#csv-file').setInputFiles({name:'browser-import.csv',mimeType:'text/csv',buffer:Buffer.from('Item,Qty,Unit price,Line total\nImported cable,5,8,41\n')});await page.locator('#status').filter({hasText:'READY FOR AUDIT'}).waitFor();
    await page.getByRole('button',{name:'Audit sheet',exact:true}).click();await page.locator('#count').filter({hasText:'(1)'}).waitFor();
    await page.getByRole('button',{name:'Apply verified repairs',exact:true}).click();await page.locator('#status').filter({hasText:'WORK VERIFIED'}).waitFor();
    if(await page.getByRole('textbox',{name:'Row 1, Line total',exact:true}).inputValue()!=='40.00')throw Error('Imported repair failed');
    await page.locator('#undo').click();await page.locator('#status').filter({hasText:'HISTORY PRESERVED'}).waitFor();
    if(await page.getByRole('textbox',{name:'Row 1, Line total',exact:true}).inputValue()!=='41')throw Error('Undo lost imported original');
    await page.locator('#receipt').click();await page.locator('#status').filter({hasText:'LOCAL INTEGRITY PASS'}).waitFor();
    const historyPromise=page.waitForEvent('download');await page.locator('#backup').click();const history=await historyPromise;
    if(history.suggestedFilename()!=='ti-agi83-history.json')throw Error('No history export');
    await page.setViewportSize({width:390,height:844});
    const width=await page.evaluate(()=>document.documentElement.scrollWidth);if(width>390)throw Error('Mobile layout overflows: '+width);
    await page.screenshot({path:path.join(out,'ti-agi83-mobile.png'),fullPage:true});
    if(errors.length)throw Error(errors.join(';'));
    console.log(JSON.stringify({status:'PASS',backend:'JAX',verifiedRepair:'32.00',relatedIncident:true,graphCells:64,trace:true,unknownPreserved:true,csv:dl.suggestedFilename(),reloadPreserved:true,csvImportRepair:'40.00',undo:true,receipts:true,historyExport:true,mobileWidth:width,pageErrors:errors}));
  } finally {if(browser)await browser.close();server.kill();}
})().catch(e=>{console.error(e);process.exitCode=1});
