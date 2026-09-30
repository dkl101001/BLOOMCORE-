// SPDX-License-Identifier: AGPL-3.0-only
const {test}=require('node:test');
const assert=require('node:assert/strict');
const {Snake,Blocks,Pong,SHAPES,rotate}=require('../tiagi83/web/arcade-engine.js');
test('Snake eats, grows and refuses reversal and second turn',()=>{
 const s=new Snake(()=>0);s.food={x:12,y:8};s.input('left');s.tick();assert.equal(s.score,10);assert.equal(s.snake.length,4);s.input('up');s.input('left');s.tick();assert.deepEqual(s.snake[0],{x:12,y:7});
});
test('Snake permits vacating its tail, but walls and body end play',()=>{
 const s=new Snake(()=>0);s.snake=[{x:2,y:2},{x:2,y:3},{x:1,y:3},{x:1,y:2}];s.direction=s.pending={x:-1,y:0};s.tick();assert.equal(s.over,false);s.snake=[{x:0,y:2}];s.tick();assert.equal(s.over,true);
 const b=new Snake(()=>0);b.snake=[{x:2,y:2},{x:3,y:2},{x:3,y:3},{x:2,y:3}];b.tick();assert.equal(b.over,true);
});
test('Snake full board ends with a win and no food',()=>{const s=new Snake(()=>0);s.snake=[];for(let y=0;y<16;y++)for(let x=0;x<24;x++)s.snake.push({x,y});s.spawnFood();assert.equal(s.won,true);assert.equal(s.food,null);s.tick();});
test('Blocks bag contains each shape once; four rotations restore it',()=>{
 const b=new Blocks(()=>.4);const shapes=[b.piece,b.next,...Array.from({length:5},()=>b.take())];assert.equal(new Set(shapes.map(JSON.stringify)).size,7);for(const shape of SHAPES){let r=shape;for(let i=0;i<4;i++)r=rotate(r);assert.deepEqual(r,shape);}
});
test('Blocks line clear preserves board height and scores verified clear',()=>{
 const b=new Blocks(()=>0);b.board[15]=Array(10).fill(1);b.board[15][4]=0;b.board[15][5]=0;b.piece=[[1,1]];b.x=4;b.y=15;b.lock();assert.equal(b.lines,1);assert.equal(b.score,100);assert.equal(b.board.length,16);assert.ok(b.board.every(r=>r.every(v=>v===0)));
});
test('Blocks wall kick fits and occupied spawn ends game',()=>{
 const b=new Blocks(()=>0);b.piece=[[1],[1],[1],[1]];b.x=9;b.y=3;b.input('rotate');assert.ok(b.fits(b.piece,b.x,b.y));assert.equal(b.piece[0].length,4);b.board=Array.from({length:16},()=>Array(10).fill(1));b.spawn();assert.equal(b.over,true);const score=b.score;b.input('drop');assert.equal(b.score,score);
});
test('Pong bounce records rally and stays within bounds',()=>{const p=new Pong(()=>.5);p.wait=0;p.ball={x:9,y:32,vx:-2,vy:0};p.tick();assert.ok(p.ball.vx>0);assert.equal(p.score,1);for(let i=0;i<50;i++)p.input('up');assert.equal(p.player,1);for(let i=0;i<50;i++)p.input('down');assert.equal(p.player,51);p.ball={x:40,y:1,vx:1,vy:-2};p.tick();assert.ok(p.ball.vy>0);});
test('Pong ends at five; later ticks cannot add points',()=>{const p=new Pong(()=>.5);for(let i=0;i<5;i++){p.wait=0;p.ball={x:96,y:2,vx:2,vy:0};p.tick();}assert.equal(p.playerPoints,5);assert.equal(p.over,true);p.tick();assert.equal(p.playerPoints,5);});
