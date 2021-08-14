// @ts-nocheck // TODO enable
import md5 from "blueimp-md5";
import { getScroll, getViewPosition,keepLastIndex} from "./utils/document";
import toggleLightMenu from "./light-menu";
import modal from "./utils/modal";
import AnnotationEditor from "./annotationEditor";
import {LightStatus, AnnotationStatus, StepProps, STORE_KEYS_VERSION_2_VALIDATE} from "./step/const";
import initKeywordTags from "./step/step-initKeywordTags";
import initAnnotation from "./step/step-initAnnotation";
import stepGotoView from "./step/step-gotoView";
import connectToKeywordTag from './step/step-connectToKeywordTag';

const editorModal = new modal();

interface StepOptions{
  onChange: Function,
  onRemove: Function,
}

const Step = function (info: StepProps,options: StepOptions,callback) {
  this.options = options;

  this.listeners = {
    data: {},
    runtime: {},
  };

  // 初始化需要持久化存储的数据
  const data = {
    lightStatus: LightStatus.LIGHT,
    annotationStatus: AnnotationStatus.SHOW,
    lightId : md5(info.id+info.text),
  };
  const that = this;
  this.data = new Proxy(data, {
    set(target,key,value){
      Reflect.set(target, key, value);
      for(let i in that.listeners.data){
        const fun = that.listeners.data[i];
        typeof fun === 'function'  && fun(target,key,value);
      }
      that.options.onChange(data);
      return target;
    }
  });
  STORE_KEYS_VERSION_2_VALIDATE.forEach((key: string)=>{
    this.data[key] = info[key];
  });

  // 初始化运行时产生的数据，不需要持久化存储
  const runtime ={
    warn: '',
    isVisible: false,
    isFocusTag: false,
    isFocusAnnotation: false,
    relatedNode: [],
    relatedAnnotationNode: null,
    focusTimer: null,
    annotationDrag: null,
  }
  this.runtime = new Proxy(runtime,{
    set(target,key,value){
      Reflect.set(target, key, value);
      for(let i in that.listeners.runtime){
        const fun = that.listeners.runtime[i];
        typeof fun === 'function'  && fun(target,key,value);
      }
      return target;
    }
  });

  this.initKeywordTags();
  this.initAnnotation();

  typeof callback === 'function' && callback(this)
}

Step.prototype.initKeywordTags = initKeywordTags;

Step.prototype.initAnnotation = initAnnotation;

Step.prototype.gotoView = stepGotoView;

Step.prototype.connectToKeywordTag = connectToKeywordTag;

Step.prototype.openEditor = function (show=true) {
  if(show===false){
    editorModal.destroy();
    return;
  }

  const that = this;
  this.data.annotationStatus = AnnotationStatus.SHOW;
  const {tip,x,y,text,bg} = this.data;

  let pos = {};
  if(that.runtime.relatedAnnotationNode){
    pos = getViewPosition(that.runtime.relatedAnnotationNode);
  } else {
    pos = {
      bodyLeft: getScroll().y + 200,
    }
  }

  editorModal.show(null,{
    left: pos.bodyLeft+'px',
    top: pos.bodyTop+pos.height+4+'px',
  });
  AnnotationEditor({
    tip,
    color:bg,
    text,
    onchange: function (e) {
      that.data.tip = e.target.value.trim();
      that.data.annotationStatus = !!e.target.value ? AnnotationStatus.SHOW : AnnotationStatus.HIDE;
    },
    root:editorModal.content,
  });

  const el = document.querySelector('pagenote-block[contenteditable="true"]');
  if(el){
    el.focus();
    keepLastIndex(el);
  }

  toggleLightMenu(true,that,{
    left: pos.bodyLeft,
    top: pos.bodyTop - 30,
  });
}

Step.prototype.delete = function () {
  this.runtime.relatedNode.forEach((element)=>{
    element.remove();
  });
  this.runtime.relatedAnnotationNode.remove();
  this.options.onRemove(this.data);
  toggleLightMenu(false);
  editorModal.destroy();
}

Step.prototype.addListener = function (fun,isRuntime=false,funId='default-change-fun') {
  const runtimeKey = isRuntime ? 'runtime' : 'data';
  this.listeners[runtimeKey][funId] = fun;
}


function Steps(option: { max: number; }) {
  this.option = option;
}
Steps.prototype = Array.prototype;
Steps.prototype.add = function (item) {
  if(item.delete){
    this.push(item);
  }else{
    console.error('非法类型',item,item.prototype,item.__proto__,Step.constructor);
  }
};

export {
  Step,
  Steps,
}
