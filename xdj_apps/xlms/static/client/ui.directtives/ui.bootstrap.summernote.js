
angularDefine(function(mdl){
    /**
 * <summernode [ng-model=...] [ng-change=...] [component-id=...]></sumnmernote>
 */
mdl.directive("summernote",["$parse",function($parse){
    function SummernoteInstance(ele){this.ele=ele;} ;
    SummernoteInstance.prototype.insertText=function(txt){
        $(this.ele[0]).summernote('insertText', txt);
        return this;
    }
    SummernoteInstance.prototype.createRange=function(){
        $(this.ele[0]).summernote('createRange');
        return this;
    }
    SummernoteInstance.prototype.enable=function(val){
        if(!val) {
            $(this.ele).summernote('disable');
        }
        else {
            $(this.ele).summernote('enable');
        }
        return this;
    }
    SummernoteInstance.prototype.insertImage=function(url,fileName){
        $(this.ele).summernote('insertImage', url, filename);
        return this;
    }
    
    return {
        restrict:"ECA",
        template:"<div><textarea></textarea></div>",
        replace:true,
        link:function(s,ele,a){
           
            function watch(){
                if(window.$.summernote){
                    init();
                }
                else {
                    setTimeout(watch,1);
                }
            }
            watch();
            function init(){
                var e=ele.find("textarea");
                var isManualChange=false;
                var isChangeByBinding=false;
               var instance=new SummernoteInstance(e[0]);
               if(a.componentId){
                 $parse(a.componentId).assign(s,instance);
               } 
               $(e[0]).summernote();
               $(e[0]).summernote("code",s.$eval(a.ngModel)||"");
               $(e[0]).on('summernote.focus', function() {
                  isManualChange=true;
               });
               $(e[0]).on('summernote.blur', function() {
                 isManualChange=false;
               });
               $(e[0]).on('summernote.change', function(we, contents, $editable) {
                   if(isChangeByBinding) return;
                   if(a.ngModel){
                       var txt=contents;
                       $parse(a.ngModel).assign(s,contents);
                   }
                   if(a.ngChange){
                       var fn=s.$eval(a.ngChange);
                       if(angular.isFunction(fn)){
                           fn(txt);
                       }
    
                   }
                   s.$applyAsync(function(){
                     
                   });
                   
               });
              
               s.$watch(a.ngModel,function(v,o){
                   if(isManualChange) return;
                   if(v!==o){
                    isChangeByBinding=true;
                     $(e[0]).summernote("code",v||"");
                     isChangeByBinding=false;
                   }
               })
               
            }
           


        }
        ///------------
    }
}]);
});