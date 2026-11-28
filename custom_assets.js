'use strict';
/* V4.8 — Custom Image Library. Browser-side assets, per-scene placement and
   preview interaction. Keep all user media on their device/project file. */
let imageLibrary=[];
const customImageCache=new Map();
const IMAGE_STORAGE_KEY='japanova-v4.8-image-library';
const MAX_CUSTOM_IMAGES=8,MAX_IMAGE_DATA=1400000;
let customPointer=null;
let customEditing=true;

function customAsset(id){return imageLibrary.find(a=>a.id===id)||null}
function activeCustomScene(){return scenes[active(timelineTime).i]||null}
function customImageForScene(scene){return scene&&scene.custom?customImageCache.get(scene.custom.assetId):null}
function safeCustom(obj){
 if(!obj||typeof obj!=='object'||typeof obj.assetId!=='string')return null;
 const numeric=(v,f)=>Number.isFinite(Number(v))?Number(v):f;
 return {assetId:obj.assetId,x:numeric(obj.x,340),y:numeric(obj.y,500),
   w:numeric(obj.w,400),offset:numeric(obj.offset,0),duration:numeric(obj.duration,2)};
}
function customBounds(scene){
 const img=customImageForScene(scene);
 if(!img||!scene||!scene.custom)return null;
 const c=scene.custom;
 const w=Number(c.w),h=w*(img.naturalHeight/img.naturalWidth);
 return {x:Number(c.x),y:Number(c.y),w,h};
}
function validateCustomImages(){
 const ds=timing();let n=0;
 scenes.forEach((scene,i)=>{
   if(!scene.custom)return;
   n++;
   if(!customAsset(scene.custom.assetId)||!customImageForScene(scene))
     throw Error('Scene '+(i+1)+': Custom Image missing. Upload it again.');
   const b=customBounds(scene),offset=Number(scene.custom.offset),length=Number(scene.custom.duration);
   if(!b||![b.x,b.y,b.w,b.h,offset,length].every(Number.isFinite)
      ||b.w<50||b.w>1080||b.h>1920||b.x<0||b.y<0
      ||b.x+b.w>1080.5||b.y+b.h>1920.5)
     throw Error('Scene '+(i+1)+': Image must fit inside the video frame.');
   if(offset<0||length<.1||offset+length>ds[i]+.02)
     throw Error('Scene '+(i+1)+': Image timing must fit inside the scene.');
 });
 if(n>MAX_CUSTOM_IMAGES)throw Error('Maximum 8 scene images per reel.');
}
function customImageMoments(){
 validateCustomImages();
 const out=[],ds=timing();let time=0;
 scenes.forEach((scene,i)=>{
   if(scene.custom)out.push({scene:i,start:time+Number(scene.custom.offset),
      duration:Number(scene.custom.duration)});
   time+=ds[i];
 });
 return out;
}
function drawCustomImage(t){
 const {i,local}=active(t),scene=scenes[i],obj=scene&&scene.custom;
 if(!obj)return;
 const image=customImageForScene(scene),bounds=customBounds(scene);
 if(!image||!bounds)return;
 if(local<obj.offset||local>=obj.offset+obj.duration)return;
 ctx.drawImage(image,bounds.x,bounds.y,bounds.w,bounds.h);
 if(customEditing&&!locked&&$('panel-scenes').classList.contains('active')){
   ctx.save();ctx.strokeStyle='#00d4ff';ctx.lineWidth=5;ctx.setLineDash([15,10]);
   ctx.strokeRect(bounds.x,bounds.y,bounds.w,bounds.h);ctx.setLineDash([]);
   ctx.fillStyle='#00d4ff';ctx.fillRect(bounds.x+bounds.w-25,bounds.y+bounds.h-25,35,35);
   ctx.restore();
 }
}
async function makeCustomLayer(index){
 const scene=scenes[index],image=customImageForScene(scene),bounds=customBounds(scene);
 if(!image||!bounds)throw Error('Scene '+(index+1)+' image not loaded.');
 const layer=document.createElement('canvas');layer.width=1080;layer.height=1920;
 layer.getContext('2d').drawImage(image,bounds.x,bounds.y,bounds.w,bounds.h);
 return new Promise((resolve,reject)=>layer.toBlob(blob=>blob?resolve(blob):reject(Error('Cannot export custom image')),'image/png'));
}
async function readCustomImage(file){
 if(!file||!['image/png','image/jpeg','image/webp'].includes(file.type))throw Error('Upload PNG, JPG or WebP only.');
 if(file.size>12*1024*1024)throw Error('Image must be smaller than 12 MB before optimization.');
 const url=URL.createObjectURL(file);
 const img=new Image();
 try{
   await new Promise((resolve,reject)=>{img.onload=resolve;img.onerror=()=>reject(Error('Cannot decode image'));img.src=url});
   if(!img.naturalWidth||!img.naturalHeight)throw Error('Invalid image dimensions');
   const sizes=[700,580,460,350,260],canvas=document.createElement('canvas');
   for(const max of sizes){
     const scale=Math.min(1,max/Math.max(img.naturalWidth,img.naturalHeight));
     canvas.width=Math.max(1,Math.round(img.naturalWidth*scale));
     canvas.height=Math.max(1,Math.round(img.naturalHeight*scale));
     canvas.getContext('2d').clearRect(0,0,canvas.width,canvas.height);
     canvas.getContext('2d').drawImage(img,0,0,canvas.width,canvas.height);
     const data=canvas.toDataURL('image/png');
     if(data.length<=MAX_IMAGE_DATA)return data;
   }
   throw Error('Image cannot fit the portable project size limit.');
 }finally{URL.revokeObjectURL(url)}
}
function preloadImageLibrary(){
 customImageCache.clear();
 for(const asset of imageLibrary){
   const img=new Image();
   img.onload=()=>{draw(timelineTime);renderAssetLibrary()};
   img.onerror=()=>{$('assetHint').textContent='An image could not be decoded.'};
   img.src=asset.data;customImageCache.set(asset.id,img);
 }
}
function saveImageLibrary(){
 try{localStorage.setItem(IMAGE_STORAGE_KEY,JSON.stringify(imageLibrary))}
 catch(e){$('assetHint').textContent='Local library storage is full. Save a .jrm project to keep your images.'}
}
function restoreImageLibrary(){
 try{
   const list=JSON.parse(localStorage.getItem(IMAGE_STORAGE_KEY)||'[]');
   if(Array.isArray(list))imageLibrary=list.filter(x=>x&&typeof x.id==='string'&&
      typeof x.name==='string'&&typeof x.data==='string'&&
      x.data.length<=MAX_IMAGE_DATA&&/^data:image\/(png|jpeg|webp);base64,/.test(x.data)).slice(0,MAX_CUSTOM_IMAGES);
 }catch(e){imageLibrary=[]}
 preloadImageLibrary();
}
function renderAssetLibrary(){
 const list=$('customAssetList');if(!list)return;list.replaceChildren();
 for(const asset of imageLibrary){
   const box=document.createElement('div');box.className='asset-card';
   const img=document.createElement('img');img.src=asset.data;img.alt=asset.name;
   const caption=document.createElement('span');caption.textContent=asset.name;
   const use=document.createElement('button');use.type='button';use.className='secondary';use.textContent='Use';
   use.disabled=locked;use.onclick=()=>{
     const scene=activeCustomScene();if(!scene)return;
     if(!customImageCache.get(asset.id)?.naturalWidth)throwCustomError('Image is still loading. Try again.');
     const picture=customImageCache.get(asset.id),naturalH=picture.naturalHeight/picture.naturalWidth;
     const width=Math.min(400,850/naturalH);
     scene.custom={assetId:asset.id,x:Math.round((1080-width)/2),y:540,w:Math.round(width),
       offset:0,duration:Math.min(2,timing()[active(timelineTime).i])};
     editor();draw(timelineTime);$('assetHint').textContent='Image applied to Scene '+(active(timelineTime).i+1)+'. Drag it on Preview.';
   };
   const remove=document.createElement('button');remove.type='button';remove.className='secondary';remove.textContent='×';remove.title='Remove from library';
   remove.disabled=locked;remove.onclick=()=>{
     if(scenes.some(s=>s.custom&&s.custom.assetId===asset.id)){
       throwCustomError('Remove this image from its scenes first.');return;
     }
     imageLibrary=imageLibrary.filter(x=>x.id!==asset.id);customImageCache.delete(asset.id);
     saveImageLibrary();renderAssetLibrary();
   };
   box.append(img,caption,use,remove);list.append(box);
 }
 $('assetCount').textContent=imageLibrary.length+'/'+MAX_CUSTOM_IMAGES+' saved';
}
function throwCustomError(message){$('assetHint').textContent='Error: '+message}
function buildCustomSceneControls(){
 for(const [i,scene] of scenes.entries()){
   const parent=$('editor').children[i];if(!parent)continue;
   const container=document.createElement('div');container.className='custom-scene-control';
   const title=document.createElement('strong');title.textContent='🖼️ Custom Image Layer';
   container.append(title);
   if(!scene.custom){
     const note=document.createElement('p');note.textContent='Select this scene in the timeline, then tap Use on an image above.';
     container.append(note);parent.append(container);continue;
   }
   const asset=customAsset(scene.custom.assetId);
   const label=document.createElement('p');label.textContent=asset?asset.name:'Image not found';
   container.append(label);
   const grid=document.createElement('div');grid.className='custom-grid';
   for(const [key,name,min,max,step] of [['x','X position',0,1080,1],['y','Y position',0,1920,1],['w','Width',50,1080,10],['offset','Appear after',0,60,.1],['duration','Visible for',.1,60,.1]]){
     const line=document.createElement('label');line.textContent=name;
     const input=document.createElement('input');input.type='number';input.min=String(min);
     input.max=String(max);input.step=String(step);input.value=String(scene.custom[key]);input.disabled=locked;
     input.addEventListener('change',()=>{
       const old=scene.custom[key];scene.custom[key]=Number(input.value);
       try{validateCustomImages();draw(timelineTime)}
       catch(e){scene.custom[key]=old;input.value=old;throwCustomError(e.message)}
     });
     line.append(input);grid.append(line);
   }
   container.append(grid);
   const actions=document.createElement('div');actions.className='custom-actions';
   const jump=document.createElement('button');jump.className='secondary';jump.type='button';jump.textContent='Show image in Preview';
   jump.onclick=()=>{const ds=timing();let start=0;for(let j=0;j<i;j++)start+=ds[j];
     timelineJump(start+Number(scene.custom.offset)+.05)};
   const remove=document.createElement('button');remove.className='secondary';remove.type='button';remove.textContent='Remove from scene';
   remove.onclick=()=>{scene.custom=null;editor();draw(timelineTime)};
   actions.append(jump,remove);container.append(actions);parent.append(container);
 }
}
const _editorBeforeCustom=editor;
editor=function(){_editorBeforeCustom();buildCustomSceneControls();renderAssetLibrary()};
const _renderTimelineBeforeCustom=renderTimeline;
renderTimeline=function(){_renderTimelineBeforeCustom();renderAssetLibrary()};
const originalDrawCustom=draw;
draw=function(...args){originalDrawCustom(...args)};
const canvasElement=$('canvas');
canvasElement.style.touchAction='none';
canvasElement.addEventListener('pointerdown',event=>{
 if(locked||!customEditing||$('panel-scenes').hidden)return;
 const scene=activeCustomScene(),b=customBounds(scene);
 if(!b||!scene.custom||!customImageForScene(scene))return;
 const rect=canvasElement.getBoundingClientRect();
 const x=(event.clientX-rect.left)/rect.width*1080,y=(event.clientY-rect.top)/rect.height*1920;
 if(x<b.x||x>b.x+b.w||y<b.y||y>b.y+b.h)return;
 const resizing=x>b.x+b.w-85&&y>b.y+b.h-85;
 customPointer={id:event.pointerId,scene,startX:x,startY:y,
   x:b.x,y:b.y,w:b.w,resize:resizing};
 canvasElement.setPointerCapture(event.pointerId);event.preventDefault();
});
canvasElement.addEventListener('pointermove',event=>{
 if(!customPointer||event.pointerId!==customPointer.id)return;
 const rect=canvasElement.getBoundingClientRect(),x=(event.clientX-rect.left)/rect.width*1080,
   y=(event.clientY-rect.top)/rect.height*1920;
 const p=customPointer,img=customImageForScene(p.scene);
 if(!img)return;
 if(p.resize){
   const ratio=img.naturalHeight/img.naturalWidth;
   const width=Math.max(50,Math.min(1080-p.x,(1920-p.y)/ratio,
      p.w+(x-p.startX), (p.w+(y-p.startY)/ratio)));
   p.scene.custom.w=Math.round(width);
 }else{
   const ratio=img.naturalHeight/img.naturalWidth,height=p.w*ratio;
   p.scene.custom.x=Math.round(Math.max(0,Math.min(1080-p.w,p.x+x-p.startX)));
   p.scene.custom.y=Math.round(Math.max(0,Math.min(1920-height,p.y+y-p.startY)));
 }
 draw(timelineTime);event.preventDefault();
});
function finishCustomPointer(event){
 if(!customPointer||event.pointerId!==customPointer.id)return;
 customPointer=null;try{canvasElement.releasePointerCapture(event.pointerId)}catch(e){}
 editor();draw(timelineTime);
}
canvasElement.addEventListener('pointerup',finishCustomPointer);
canvasElement.addEventListener('pointercancel',finishCustomPointer);
$('assetUpload').addEventListener('change',async()=>{
 const files=Array.from($('assetUpload').files||[]);
 try{
   for(const file of files){
     if(imageLibrary.length>=MAX_CUSTOM_IMAGES)throw Error('Maximum 8 reusable images.');
     const data=await readCustomImage(file);
     const id=Date.now().toString(36)+Math.random().toString(36).slice(2,10);
     imageLibrary.push({id,name:file.name.slice(0,80),data});
   }
   saveImageLibrary();preloadImageLibrary();renderAssetLibrary();$('assetHint').textContent='Saved to this browser and included with .jrm projects.';
 }catch(e){throwCustomError(e.message)}
 finally{$('assetUpload').value=''}
});
$('assetEditMode').addEventListener('change',()=>{customEditing=$('assetEditMode').checked;draw(timelineTime)});
restoreImageLibrary();renderAssetLibrary();
