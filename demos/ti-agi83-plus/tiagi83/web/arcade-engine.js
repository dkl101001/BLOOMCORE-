// SPDX-License-Identifier: AGPL-3.0-only
// Authorship lineage: Frazer Σ Love ACO-Σ; Sara ΣΩ.
// Original browser implementations; no TI ROMs or community game code.
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.TIArcadeEngine=api;})(typeof globalThis!=='undefined'?globalThis:this,()=>{
  'use strict';
  const same=(a,b)=>a.x===b.x&&a.y===b.y;
  class Snake {
    constructor(rng=Math.random){this.rng=rng;this.kind='snake';this.snake=[{x:11,y:8},{x:10,y:8},{x:9,y:8}];this.direction={x:1,y:0};this.pending=this.direction;this.turned=false;this.score=0;this.over=false;this.won=false;this.spawnFood();}
    get period(){return Math.max(65,145-this.score/3);}
    spawnFood(){const free=[];for(let y=0;y<16;y++)for(let x=0;x<24;x++)if(!this.snake.some(p=>same(p,{x,y})))free.push({x,y});if(!free.length){this.food=null;this.won=true;this.over=true;}else this.food=free[Math.min(free.length-1,Math.floor(this.rng()*free.length))];}
    input(key){const dirs={up:{x:0,y:-1},down:{x:0,y:1},left:{x:-1,y:0},right:{x:1,y:0}};const d=dirs[key];if(!d||this.turned||this.over||d.x===-this.direction.x&&d.y===-this.direction.y)return;this.pending=d;this.turned=true;}
    tick(){if(this.over)return;this.direction=this.pending;this.turned=false;const head={x:this.snake[0].x+this.direction.x,y:this.snake[0].y+this.direction.y};const grows=same(head,this.food);const occupied=grows?this.snake:this.snake.slice(0,-1);if(head.x<0||head.x>=24||head.y<0||head.y>=16||occupied.some(p=>same(p,head))){this.over=true;return;}this.snake.unshift(head);if(grows){this.score+=10;this.spawnFood();}else this.snake.pop();}
  }

  const SHAPES=[[[1,1,1,1]],[[1,1],[1,1]],[[0,1,0],[1,1,1]],[[0,1,1],[1,1,0]],[[1,1,0],[0,1,1]],[[1,0,0],[1,1,1]],[[0,0,1],[1,1,1]]];
  const rotate=m=>m[0].map((_,x)=>m.map(row=>row[x]).reverse());
  class Blocks {
    constructor(rng=Math.random){this.rng=rng;this.kind='blocks';this.board=Array.from({length:16},()=>Array(10).fill(0));this.bag=[];this.score=0;this.lines=0;this.over=false;this.next=this.take();this.spawn();}
    get level(){return 1+Math.floor(this.lines/10);}
    get period(){return Math.max(90,620-(this.level-1)*55);}
    take(){if(!this.bag.length){this.bag=[0,1,2,3,4,5,6];for(let i=6;i>0;i--){const j=Math.min(i,Math.floor(this.rng()*(i+1)));[this.bag[i],this.bag[j]]=[this.bag[j],this.bag[i]];}}return SHAPES[this.bag.pop()].map(row=>row.slice());}
    spawn(){this.piece=this.next;this.next=this.take();this.x=Math.floor((10-this.piece[0].length)/2);this.y=0;if(!this.fits(this.piece,this.x,this.y))this.over=true;}
    fits(piece,x,y){return piece.every((row,dy)=>row.every((cell,dx)=>!cell||(x+dx>=0&&x+dx<10&&y+dy>=0&&y+dy<16&&!this.board[y+dy][x+dx])));}
    move(dx,dy){if(this.fits(this.piece,this.x+dx,this.y+dy)){this.x+=dx;this.y+=dy;return true;}return false;}
    lock(){this.piece.forEach((row,dy)=>row.forEach((cell,dx)=>{if(cell)this.board[this.y+dy][this.x+dx]=1;}));const kept=this.board.filter(row=>!row.every(Boolean)),cleared=16-kept.length;this.score+=[0,100,300,500,800][cleared]*this.level;this.lines+=cleared;this.board=[...Array.from({length:cleared},()=>Array(10).fill(0)),...kept];this.spawn();}
    input(key){if(this.over)return;if(key==='left')this.move(-1,0);else if(key==='right')this.move(1,0);else if(key==='down'){if(this.move(0,1))this.score++;else this.lock();}else if(key==='up'||key==='rotate'){const r=rotate(this.piece);for(const dx of [0,-1,1,-2,2,-3,3])if(this.fits(r,this.x+dx,this.y)){this.piece=r;this.x+=dx;break;}}else if(key==='drop'){let distance=0;while(this.move(0,1))distance++;this.score+=distance*2;this.lock();}}
    tick(){if(!this.over&&!this.move(0,1))this.lock();}
  }

  class Pong {
    constructor(rng=Math.random){this.rng=rng;this.kind='pong';this.player=26;this.cpu=26;this.playerPoints=0;this.cpuPoints=0;this.rally=0;this.score=0;this.over=false;this.serve(1);}
    get period(){return 30;}
    serve(direction){this.ball={x:48,y:32,vx:direction*1.6,vy:(this.rng()-.5)*1.8};this.rally=0;this.wait=22;}
    input(key){if(this.over)return;if(key==='up')this.player=Math.max(1,this.player-2);if(key==='down')this.player=Math.min(51,this.player+2);}
    bounce(paddle,direction){const hit=(this.ball.y-(paddle+6))/6;this.ball.vx=direction*Math.min(3.2,Math.abs(this.ball.vx)+.08);this.ball.vy=hit*1.8;this.rally++;this.score=Math.max(this.score,this.rally);}
    tick(){if(this.over)return;if(this.wait){this.wait--;return;}const b=this.ball;this.cpu=Math.max(1,Math.min(51,this.cpu+Math.max(-.75,Math.min(.75,b.y-(this.cpu+6)))));b.x+=b.vx;b.y+=b.vy;if(b.y<2){b.y=2;b.vy=Math.abs(b.vy);}if(b.y>61){b.y=61;b.vy=-Math.abs(b.vy);}if(b.vx<0&&b.x<=8&&b.x>=4&&b.y>=this.player-1&&b.y<=this.player+13){b.x=8;this.bounce(this.player,1);}else if(b.vx>0&&b.x>=88&&b.x<=92&&b.y>=this.cpu-1&&b.y<=this.cpu+13){b.x=88;this.bounce(this.cpu,-1);}if(b.x<0||b.x>96){const direction=b.x<0?1:-1;if(b.x<0)this.cpuPoints++;else this.playerPoints++;if(this.playerPoints===5||this.cpuPoints===5)this.over=true;else this.serve(direction);}}
  }
  return {Snake,Blocks,Pong,SHAPES,rotate,create:(kind,rng)=>{const C={snake:Snake,blocks:Blocks,pong:Pong}[kind];if(!C)throw Error('Unknown game');return new C(rng);}};
});
